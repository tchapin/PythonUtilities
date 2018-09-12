"""
Name:           FTPUtils

Purpose:        Utilities for FTP

Dependencies:   none

Version:        3.6

Author:         ted.chapin

Created:        9/12/2018
"""

from ftplib import FTP
import json
import os


config_file = os.path.join(os.path.dirname(__file__), "config.json")
CONFIG = json.loads(open(config_file).read()) if os.path.isfile(config_file) else {}


def main():
    pass

    return


def get_file(host, username, password, ftp_folder, file_name, destination_folder, overwrite="no"):
    """
    purpose:
        Download a file from an ftp site and copy it to a destination folder.
    arguments:
        host: string
            ftp site address
        username: string
        password: string
        ftp_folder: string
            folder on the ftp host in which the file exists
        file_name: string
            file to retrieve
        destination_folder: string
            the path to a folder to receive the downloaded file
        overwrite: string
            yes or no
            indicates whether to overwrite the destination file if it already exists
            if no, a number suffix will be added to the file's root name until
            a new filename is obtained
    return value: dictionary
        success: boolean
        messages: list of string
    """

    ret_dict = {"messages": []}
    try:
        # get the output file
        # if no overwrite, append an incrementing suffix until you get a new file name
        if overwrite == "yes":
            destination_file_path = os.path.join(destination_folder, file_name)
        else:
            if os.path.exists(os.path.join(destination_folder, file_name)):
                suffix = 1
                file_root = os.path.splitext(file_name)[0]
                file_ext = os.path.splitext(file_name)[1]
                destination_file_path = os.path.join(destination_folder, "{0} {1}{2}".format(file_root, suffix, file_ext))
                while os.path.exists(destination_file_path):
                    suffix += 1
                    destination_file_path = os.path.join(destination_folder, "{0} {1}{2}".format(file_root, suffix, file_ext))
            else:
                destination_file_path = os.path.join(
                    destination_folder, file_name)
        # download the ftp file to the destination file
        ftp = FTP(host, username, password)
        ftp.cwd(ftp_folder)
        with open(destination_file_path, "wb") as f:
            ftp.retrbinary("RETR {0}".format(file_name), f.write)
        ret_dict["success"] = True
    except Exception as e:
        ret_dict["messages"].append(e.message)
        ret_dict["success"] = False
    finally:
        return ret_dict


def get_folder_tree(host, username, password, ftp_folder, destination_folder):
    """
    purpose:
        Download a folder tree (all files and folders and all files and folders they contain).
    arguments:
        host: string
            ftp site address
        username: string
        password: string
        ftp_folder: string
            top level folder on the ftp host
        destination_folder: string
            The folder on the file system into which
            you want to copy the entire tree starting at ftp_folder
    return value: dictionary
        success: boolean
        messages: list of string
    """

    ret_dict = {"messages": []}
    try:
        # make an ftp connection
        ftp = FTP(host, username, password)
        # get the folder tree
        _get_files_recursive(ftp, ftp_folder, destination_folder, destination_folder)
        # close the ftp connection
        ftp.quit()

        ret_dict["success"] = True
    except Exception as e:
        ret_dict["messages"].append(e.message)
        ret_dict["success"] = False
    finally:
        return ret_dict


def list_items(host, username, password, folder):
    """
    purpose:
        Get a list of items (files & folders) in the ftp host's folder.
    arguments:
        host: string
            ftp site address
        username: string
        password: string
        folder: string
            folder on the ftp host
    return value: dictionary
        success: boolean
        items: list of string
            list of files/folders in the FTP folder
        messages: list of string
    """

    ret_dict = {"messages": [], "items": []}
    try:
        ftp = FTP(host, username, password)
        ftp.cwd(folder)
        # get all the items in this folder, nlst doesn't distinguish between
        # folders and files
        ret_dict["items"] = ftp.nlst()
        ret_dict["success"] = True
    except Exception as e:
        ret_dict["messages"].append(e.message)
        ret_dict["success"] = False
    finally:
        return ret_dict


def put_file(host, username, password, local_file, ftp_folder):
    """
    purpose:
        Upload a file to an ftp server.
        If the file already exists it will be overwritten.
    arguments:
        host: string
            ftp site address
        username: string
        password: string
        local_file: string
            path to a file on the local file system
        ftp_folder: string
            folder on the remote ftp server into which to upload the file
    return value: dictionary
        success: boolean
        messages: list of string
    """

    ret_dict = {"messages": []}
    try:
        ftp = FTP(host, username, password)
        ftp.cwd(ftp_folder)
        ftp.storbinary("STOR {0}".format(os.path.basename(local_file)), open(local_file, "rb"))
        ret_dict["success"] = True
    except Exception as e:
        ret_dict["messages"].append(e.message)
        ret_dict["success"] = False
    finally:
        return ret_dict


def _get_files_recursive(ftp, item, destination_root, destination_folder):
    """
    purpose:
        This is a recursive function that will download all folders, files, and their children.
        The first time this function gets called, the item represents the top-level folder on the ftp server.
        It will walk the FTP folder tree from there down and recreate the tree in destination_root.
    arguments:
        ftp: ftplib.FTP
            authenticated ftp connection
        item: string
            a folder or file in the ftp pwd
        destination_root: string
            the folder on the local file system to receive the remote directory tree
            everything from and including the original item down will get created here
        destination_folder: string
            the sub-folder on the local file system representing this iteration of the item
    return value: none
    """

    if _try_cwd(ftp, item):
        destination_folder = os.path.join(destination_root, os.path.join(*item.split("/")))
        if not os.path.isdir(destination_folder):
            os.makedirs(destination_folder)
        for sub_item in ftp.nlst():
            if sub_item not in (".", ".."):
                sub_folder = "{0}/{1}".format(item, sub_item)
                _get_files_recursive(ftp, sub_folder, destination_root, destination_folder)
    else:
        destination_file = os.path.join(destination_root, os.path.join(*item.split("/")))
        with open(destination_file, "wb") as f:
            ftp.retrbinary("RETR {0}".format(item), f.write)


def _try_cwd(ftp, item):
    """
    purpose:
        Determine if item is an ftp folder.
        Try to cwd into the item.
        If you can cwd it's a folder, if not, it's a file.
    arguments:
        ftp: ftplib.FTP
            an authenticated ftp connection
        item: string
            the name of the folder you are trying to cwd into
    return value: boolean
        True if the item is a folder
        False if it is not a folder
    """

    try:
        ftp.cwd(item)
        return True
    except Exception:
        return False


if __name__ == '__main__':
    main()
