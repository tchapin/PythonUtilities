"""
Name:           SMSUtils

Purpose:        Utilities for sending SMS messages using Twilio API

Dependencies:   twilio

Version:        3.6

Author:         ted.chapin

Created:        9/12/2018
"""


import json
import os
import re
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

config_file = os.path.join(os.path.dirname(__file__), "config.json")
CONFIG = json.loads(open(config_file).read()) if os.path.isfile(config_file) else {}


def main():
    pass

    return


def send_text_message(phone_number, text_message):
    """
    purpose:
        Send a text message.
        Use \n as a line break in multi-line messages.
    arguments:
        phone_number: string
            10-digit phone number to send message to.
            It can contain hyphens or just numbers
            ########## or ###-###-####
        text_message: string
            body of the text message to send
    return value: dictionary
        success: boolean
        messages: list of string
    """

    ret_dict = {"messages": []}

    # validate the inputs
    # phone number must be ########## or ###-###-####
    if re.match(r"^\d{3}-\d{3}-\d{4}$|^\d{10}$", phone_number) is None:
        ret_dict["messages"].append("Phone number must be in the format ########## or ###-###-####")
        ret_dict["success"] = False
        return
    # text_message must be <= 1000 characters
    if len(text_message) > 1000:
        ret_dict["messages"].append("Text message must be <= 1000 characters")
        ret_dict["success"] = False
        return
    # send the text
    acct_sid = CONFIG.get("twilio_sid", "")
    token = CONFIG.get("twilio_token", "")
    from_num = CONFIG.get("twilio_from_num", "")
    to_num = "+1{0}".format(phone_number.replace("-", ""))
    try:
        client = Client(acct_sid, token)
        client.messages.create(to=to_num, from_=from_num, body=text_message)
        ret_dict["success"] = True
    except TwilioRestException as e:
        ret_dict["messages"].append("There was an error sending the SMS: {0}".format(e.msg))
        ret_dict["success"] = False
    except Exception as e:
        ret_dict["messages"].append("An unknown error occurred: {0}".format(e))
        ret_dict["success"] = False
    finally:
        return ret_dict


if __name__ == '__main__':
    main()
