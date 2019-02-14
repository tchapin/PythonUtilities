"""
Name:           GISUtils

Purpose:        GIS utilities

Dependencies:   arcpy, requests, TypeUtils

Version:        3.6

Author:         ted.chapin

Created:        9/17/2018
"""


import arcpy
import csv
import datetime
import json
import os
import requests
import TypeUtils

config_file = os.path.join(os.path.dirname(__file__), "config.json")
CONFIG = json.loads(open(config_file).read()) if os.path.isfile(config_file) else {}


def main():
    pass

    return


def add_message(message, message_type="message", run_method="script"):
    """
    purpose:
        mixed messaging for ArcGIS Python toolbox development
        Prints to python interpreter when run as a script,
        Uses Python Toolbox's messaging system when run as a tool.
            AddMessage, AddWarning, AddError
        If the tool gets published as a GP service, use message level "Error".
            That way, the web app builder apps will show errors without inundating
            the user with verbose messaging.
        For GP tools that will be published as services,
            use "messages" output parameter method.
            it is more friendly for the WAB gp widget
    arguments:
        message: string
            the message to send to the user
        message_type: string
            message (default), warning, error
        run_method: string
            script (default), tool
    return value: none
    """

    if run_method == "script":
        print("{0}: {1}".format(message_type, message))
    elif run_method == "tool":
        if message_type == "message":
            arcpy.AddMessage(message)
        elif message_type == "warning":
            arcpy.AddWarning(message)
        elif message_type == "error":
            arcpy.AddError(message)


def export_table_to_csv(input_table, output_file, field_names=["*"], include_header=True):
    """
    purpose:
        Export a feature class or table to a csv file
    arguments:
        input_table: string
            full path to a feature class, layer, table, or table view
        output_file: string
            full path to the csv file to create
            WARNING: if the output_file exists it will be overwritten
        field_names: list of string
            list of field names to include in the csv file
            specify individual field names or use ["*"] for all fields
        include_header: boolean
            whether or not to include the header row in the output_file
    return value: dictionary
        success: boolean
        messages: list of string
            only error messages will be returned.
            This will be empty if successful
    """

    ret_dict = {"messages": []}
    try:
        # get all the fields if ["*"] was specified
        if len(field_names) == 1 and field_names[0] == "*":
            field_names = [fld.name for fld in arcpy.ListFields(input_table)]
        with open(output_file, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            # write the header row
            if include_header is True:
                csvwriter.writerow(field_names)
            # write the data
            for row in arcpy.da.SearchCursor(input_table, field_names):
                csvwriter.writerow(row)
        ret_dict["success"] = True
    except Exception as e:
        ret_dict["messages"].append(e.message)
        ret_dict["success"] = False
    finally:
        return ret_dict


def field_exists(feature_class, field_name):
    """
    purpose:
        determine if a field exists in a feature class
    arguments:
        feature_class: string
            gdb feature class
        field_name: string
    return value: boolean
        True if the field exists
        False if it does not exist or if there is an error
    """
    try:
        return field_name.lower() in [fld.name.lower() for fld in arcpy.ListFields(feature_class, field_name)]
    except Exception:
        return False


def format_station(station):
    """
    purpose:
        format a measure as a station value with hundreds offset
        0+00 notation
    arguments:
        station: number
            station measurement
    return value: string
        measurement formatted as 0+00
        None if error
    """

    try:
        if TypeUtils.is_numeric(station):
            station_str = str(station)
            if station < 100 and station >= 10:
                return "0+{0}".format(station_str)
            elif station < 10:
                return "0+0{0}".format(station_str)
            else:
                if "." in station_str:
                    return "{0}+{1}.{2}".format(
                        station_str.split(".")[0][:-2],
                        station_str.split(".")[0][-2:],
                        station_str.split(".")[1]
                    )
                else:
                    return "{0}+{1}".format(
                        station_str.split(".")[0][:-2],
                        station_str.split(".")[0][-2:]
                    )
        else:
            return None
    except Exception:
        return None


def get_agol_token(username, password):
    """
    purpose:
        get a security token from ArcGIS Online
    arguments:
        username: string
        password: string
    return value: string
        token, None if error
    """

    try:
        url = "https://www.arcgis.com/sharing/rest/generateToken"
        params = {
            "username": username,
            "password": password,
            "referer": "something",
            "f": "json"}
        result = requests.post(url, params).json()
        return result.get("token")
    except Exception:
        return None


def get_ags_token(server, username, password):
    """
    purpose:
        get a security token from ArcGIS Server
    arguments:
        server: string
            the name of the ArcGIS Server to get the token from
        username: string
        password: string
    return value: string
        token, None if error
    """

    try:
        url = r"http://{0}:6080/arcgis/tokens/generateToken".format(server)
        params = {
            "username": username,
            "password": password,
            "f": "json"}
        result = requests.post(url, params).json()
        return result.get("token")
    except Exception:
        return None


def get_domain(gdb, domain_name):
    """
    purpose:
        get a domain from a geodatabase
    arguments:
        gdb: string
            geodatabase
        domain_name: string
            name of the domain to retrieve
    return value: arcpy.Domain
        None if error
    """
    ret_val = None
    try:
        for domain in arcpy.da.ListDomains(gdb):
            if domain.name.lower() == domain_name.lower():
                ret_val = domain
    except Exception:
        return None
    finally:
        return ret_val


def get_prior_date(this_date, day_of_week):
    """
    purpose:
        Get the date of a day of the week prior to a given date.
        If the date provided is on the same day of the week as the requested
        day, the prior week will be returned.
    arguments:
        this_date: datetime.date
            date prior to which the date will be returned
        day_of_week: int
            Monday is 0, Sunday is 6
    return value: datetime.date
        the datetime.date of the day_of_week before this_date
        returns None if error
    """

    try:
        if day_of_week not in range(0, 7):
            raise Exception()
        this_day = this_date.weekday()
        if this_day > day_of_week:
            # if this_day is ahead of the day of week, subtract the number of days it's ahead
            ret_date = this_date - datetime.timedelta(days=(this_day - day_of_week))
        else:
            # if this_day is on or behind the day of week, subtract a week minus the number days it's behind
            ret_date = this_date - datetime.timedelta(days=(7 - (day_of_week - this_day)))
        return ret_date
    except Exception:
        return None


def get_station(point, lines):
    """
    purpose:
        gets the station of an arcpy.Point to the closest line
        in a list of arcpy.Polyline
        uses the measure of the point along the line
    arguments:
        point: arcpy.Point
        lines: list of arcpy.Polyline
    return value: string
        formatted station string if successful
        None if error
    """

    try:
        # get the closest line to the point
        closest_line = None
        try:
            min_distance = None
            for line in lines:
                dist = line.distanceTo(point)
                if min_distance is None or dist < min_distance:
                    min_distance = dist
                    closest_line = line
        except Exception:
            return None
        # get the station of the closest line
        if closest_line is not None:
            # get the measure of the point on the closest line
            measure = closest_line.measureOnLine(point)
            # get the formatted station
            station_txt = format_station(measure)
            return station_txt
        else:
            return None
    except Exception:
        return None


if __name__ == '__main__':
    main()
