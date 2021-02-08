import time
from os.path import isfile
from os import getenv

from datetime import datetime
import re

from utils.util import Util


class TimeParser:
    def __init__(self):
        """
        This is a constructor for the Time parser.
        It initiates a TimeParser with desired intervals
        e.g. interval_in__milliseconds=10000 creates intervals of 10 seconds in that video
        """

        self.interval_in_milliseconds = int(
            Util().config["parser"]["milliseconds-interval"]
            if isfile("config/config.yml")
            else getenv("MILLISECONDS_INTERVAL")
        )

    def get_related_intervals(self, start, end):
        """
        This method returns a list of intervals based on start  and end time passed
        e.g.
        start:00:00:00
        end: 00:00:35
        returns [0000,01000,02000,03000] which represents  moments of:
        0 to 10 seconds
        10 to 20 seconds
        20 to 30 seconds
        30 to 40 seconds
        :param start: start time in milliseconds
        :param end: end time in milliseconds
        :return: list of intervals based on start  and end time passed
        """
        intervals = []
        if (
            end - start < self.interval_in_milliseconds
        ):  # CASE: when appearance is within time interval
            intervals.append(int(start) - int(start) % self.interval_in_milliseconds)
        for i in range(int(start), int(end)):
            if i % self.interval_in_milliseconds == 0:
                intervals.append(i)
        return intervals

    @staticmethod
    def string_time_to_milliseconds(string_time):
        """
        This method converts string time to milliseconds
        it uses regex to handle both of the following  cases formats:
        - %H:%M:%S
        - %H:%M:%S.%f
        :param string_time:
        :return: passed time converted to milliseconds
        """
        if re.search("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$", string_time):
            date_time = datetime.strptime(string_time, "%H:%M:%S")
        elif re.search("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]\.\d", string_time):
            date_time = datetime.strptime(string_time, "%H:%M:%S.%f")
        else:
            raise ("time format  error")
        date_time = date_time - datetime(1900, 1, 1)
        milliseconds = date_time.total_seconds() * 1000
        return milliseconds

    @staticmethod
    def seconds_to_time_string(seconds):
        """
        This method converts seconds to %H:%M:%S format
        :param seconds:
        :return:
        """

        return str(time.strftime("%H:%M:%S", time.gmtime(seconds)))
