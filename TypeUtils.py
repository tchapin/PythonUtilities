"""
Name:           TypeUtils

Purpose:        Determine the data types of arguments

Dependencies:   none

Version:        3.6

Author:         ted.chapin

Created:        9/17/2018
"""


import datetime
import json
import os


config_file = os.path.join(os.path.dirname(__file__), "config.json")
CONFIG = json.loads(open(config_file).read()) if os.path.isfile(config_file) else {}


def main():
    pass

    return


def is_date(date_string, date_format):
    """
    purpose:
        determine if the string is a date in the specified format
    arguments:
        date_string: string
            The value to evaluate for dateness
        date_format: string
            The format string to use to evaluate the date string
    return value: Boolean
    """

    try:
        datetime.datetime.strptime(date_string, date_format)
        return True
    except Exception:
        return False


def is_none_or_empty(arg):
    """
    purpose:
        check if the arg is either None or an empty string
    arguments:
        arg: varies
    return value: Boolean
    """

    try:
        return arg is None or arg == ""
    except Exception:
        return False


def is_numeric(arg):
    """
    purpose:
        check if the arg is a number
    arguments:
        arg: varies
    return value: Boolean
    """

    try:
        float(arg)
        return True
    except Exception:
        return False


def is_integer(arg):
    """
    purpose:
        check if the arg is an integer
    arguments:
        arg: varies
    return value: Boolean
    """

    try:
        return float(arg).is_integer()
    except Exception:
        return False


def is_string(arg):
    """
    purpose:
        check is the arg is a string
    arguments:
        arg: varies
    return value: Boolean
    """

    try:
        str(arg)
        return True
    except Exception:
        return False


if __name__ == '__main__':
    main()
