"""
Name:           ZipUtils.py

Purpose:        Zip file utilities

Dependencies:   none

Version:        3.6

Author:         ted.chapin

Created:        9/12/2018
"""


import json
import os
import zipfile


config_file = os.path.join(os.path.dirname(__file__), "config.json")
CONFIG = json.loads(open(config_file).read()) if os.path.isfile(config_file) else {}


def main():
    pass

    return


def zip_folder(folder_path):
    """
    purpose:
      Zip a folder to a .zip file with the same name as the folder.
    arguments:
      folder_path: string
          path to the folder to zip
    return value: string
      path to the zip file if successful,
      "" if not successful
    """

    try:
        if not os.path.isdir(folder_path):
            return ""
        parent_folder = os.path.dirname(folder_path)
        zip_file = "{0}.zip".format(folder_path)
        with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as out_file:
            for root, folders, files in os.walk(folder_path):
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path.replace(parent_folder, "")
                    out_file.write(absolute_path, relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    relative_path = absolute_path.replace(parent_folder, "")
                    out_file.write(absolute_path, relative_path)
        return zip_file
    except Exception:
        return ""


def zip_gdb(gdb_path):
    """
    purpose:
      Zip a file geodatabase.
    arguments:
      gdb_path: string
          path to the file gdb to zip
    return value: string
      the path name of the zip file if successful
      "" if not successful
    """

    try:
        if not os.path.isdir(gdb_path):
            return ""
        zip_file = "{0}.zip".format(gdb_path)
        with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as out_file:
            for root, dirs, files in os.walk(gdb_path):
                for name in files:
                    out_file.write(os.path.join(root, name), os.path.join(
                        os.path.basename(gdb_path), name))
        return zip_file
    except Exception:
        return ""


def unzip_file(file_path):
    """
    purpose:
      Unzip a zip file into a folder with the name of the zip file.
    arguments:
      file_path: string
          path to the file to unzip
          must be a .zip file
    return value: boolean
      True if successful
      False if error
    """

    try:
        # make sure the zip file exists
        if os.path.exists(file_path):
            out_folder = os.path.splitext(file_path)[0]
            # make sure the folder doesn't already exist
            if os.path.isdir(out_folder):
                return False
            else:
                with zipfile.ZipFile(file_path) as zip_file:
                    zip_file.extractall(out_folder)
                return True
        else:
            return False
    except Exception:
        return False


if __name__ == '__main__':
    main()
