"""
Name:           EmailUtils

Purpose:        Send an email via Python
                Adapted from http://naelshiab.com/tutorial-send-email-python/
                Uses Slack notifications for errors

Dependencies:   SlackUtils

Version:        3.6

Author:         ted.chapin

Created:        9/12/2018
"""


import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import encoders
import SlackUtils


config_file = os.path.join(os.path.dirname(__file__), "config.json")
CONFIG = json.loads(open(config_file).read()) if os.path.isfile(config_file) else {}


def main():
    pass

    return


def send_email(to_list, cc_list, subject, body, files=[]):
    """
    purpose:
        send an email
    arguments:
        to_list: list of string
            list of the TO recipients' email addresses
        cc_list: list of string
            list of the CC recipients' email addresses
        subject: string
            subject of the email
        body: string
            body of the email
        files: list of string
            paths to files to attach to the email
    return value: dictionary
        success: boolean
        messages: list of string
    """

    ret_dict = {"messages": []}
    try:
        # create a message with to, from, subject, body, and attachment
        from_addr = CONFIG.get("email_from", "")
        message = MIMEMultipart()
        message["From"] = from_addr
        message["To"] = ",".join(to_list)
        message["Cc"] = ",".join(cc_list)
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))
        if len(files) > 0:
            for file_path in files:
                if os.path.isfile(file_path):
                    part = MIMEBase("application", "octet-stream")
                    with open(file_path, "rb") as attachment:
                        part.set_payload((attachment).read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment; filename = {0}".format(os.path.basename(file_path)))
                    message.attach(part)

        # send the email
        smtp_server = CONFIG.get("email_smtp_server", "")
        server = smtplib.SMTP(smtp_server)
        server.starttls()
        username = CONFIG.get("email_username", "")
        password = CONFIG.get("email_password", "")
        server.login(username, password)
        result = server.sendmail(from_addr, to_list + cc_list, message.as_string())
        server.quit()
        # if the result has no keys it was a success
        if len(result.keys()) == 0:
            ret_dict["success"] = True
        else:
            SlackUtils.post_slack_message(CONFIG.get("slack_notification_user", ""), "Error in SendEmail. Subject = {0}. Result = {1}".format(subject, result))
            ret_dict["messages"].append(result)
            ret_dict["success"] = False
    except Exception as e:
        SlackUtils.post_slack_message(CONFIG.get("slack_notification_user", ""), "Error in SendEmail. Subject = {0}. Error = {1}".format(subject, e))
        ret_dict["messages"].append(e.message)
        ret_dict["success"] = False
    finally:
        return ret_dict


if __name__ == '__main__':
    main()
