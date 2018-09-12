"""
Name:           SlackUtils

Purpose:        Post messages and files to Slack

Dependencies:   requests

Version:        3.6

Author:         ted.chapin

Created:        9/12/2018
"""


import json
import os
import requests
import time


config_file = os.path.join(os.path.dirname(__file__), "config.json")
CONFIG = json.loads(open(config_file).read()) if os.path.isfile(config_file) else {}


def main():
    pass

    return


def post_slack_message(channel, text):
    """
    purpose:
        posts a text message to a Slack channel
        uses the token for the Slack bot
    arguments:
        channel: string
            The name of the channel to post in
            For person or private group, use @name, other just use channel_name
        text: string
            the message to post
    return value: dictionary
        success: boolean
        messages: list of string
    """

    ret_dict = {"messages": []}
    try:
        message_url = r"https://slack.com/api/chat.postMessage"
        token = CONFIG.get("slack_token", "")
        params = {
            "token": token,
            "channel": channel,
            "text": text
        }
        resp = requests.post(message_url, params)
        if resp.status_code == 200:
            resp_json = resp.json()
            if resp_json.get("ok") is True:
                ret_dict["messages"].append("Message posted to {0} at {1}".format(channel, time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(float(resp_json.get("ts"))))))
                ret_dict["success"] = True
            else:
                ret_dict["messages"].append(resp_json.get("error"))
                ret_dict["success"] = False
        else:
            ret_dict["messages"].append("Error posting message: {0}".format(resp.content))
            ret_dict["success"] = False
    except Exception as e:
        ret_dict["messages"].append(e.message)
        ret_dict["success"] = False
    finally:
        return ret_dict


def post_slack_file(channel, file_path, title="", initial_comment=""):
    """
    purpose:
        posts a file to a Slack channel
        uses the token for the Slack bot
    arguments:
        channel: string
            The name of the channel to post in
            for person or private group, use @name, other just use channel_name
        file_path: string
            path to the file to upload
        title: string
            title of the post
        initial_comment: string
            initial comment to the post
    return value: dictionary
        success: Boolean
        messages: List of string
    """

    ret_dict = {"messages": []}
    try:
        files_url = r"https://slack.com/api/files.upload"
        token = CONFIG.get("slack_token", "")
        params = {
            "token": token,
            "channels": channel,
            "title": title,
            "initial_comment": initial_comment
        }
        files = {"file": open(file_path, "rb")}
        resp = requests.post(files_url, params=params, files=files)
        if resp.status_code == 200:
            resp_json = resp.json()
            if resp_json.get("ok") is True:
                ret_dict["messages"].append("File posted to {0} at {1}".format(channel, time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(float(resp_json.get("ts"))))))
                ret_dict["success"] = True
            else:
                ret_dict["messages"].append(resp_json.get("error"))
                ret_dict["success"] = False
        else:
            ret_dict["messages"].append("Error posting file: {0}".format(resp.content))
            ret_dict["success"] = False
    except Exception as e:
        ret_dict["messages"].append(e.message)
        ret_dict["success"] = False
    finally:
        return ret_dict


if __name__ == '__main__':
    main()
