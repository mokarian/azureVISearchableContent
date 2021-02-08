import pytest

from src.parser.timeparser import TimeParser
from tests.testbase import TestBase
from tests.utils import Utils


class TestTimeParser(TestBase):
    """
    This class contains unit tests for UsernameHelper class
    """

    time_parser = TimeParser()
    utils = Utils()

    def test_get_related_intervals(self):
        """
        test_alphanum_split for this pattern: "alpha_number_alpha".
        """
        # WHEN
        actual = self.time_parser.get_related_intervals(0, 20000)
        # THEN
        self.assert_equals(actual, [0, 10000])

    def test_get_related_intervals_15_seconds_interval(self):
        """
        test_alphanum_split for this pattern: "alpha_number_alpha".
        """
        # GIVEN
        self.time_parser.interval_in__milliseconds = 15000
        # WHEN
        actual = self.time_parser.get_related_intervals(0, 20000)
        # THEN
        self.assert_equals(actual, [0, 15000])

    def test_string_time_to_milliseconds_seconds_only(self):
        """
        test_alphanum_split for this pattern: "alpha_number_alpha".
        """
        # WHEN
        actual = self.time_parser.string_time_to_milliseconds("00:23:00")
        # THEN
        self.assert_equals(actual, 1380000)

    def test_string_time_to_milliseconds_seconds_and_milliseconds(self):
        """
        test_alphanum_split for this pattern: "alpha_number_alpha".
        """
        # WHEN
        actual = self.time_parser.string_time_to_milliseconds("00:23:00.122")
        # THEN
        self.assert_equals(actual, 1380122)

    def test_string_time_to_milliseconds_wrong_time_format(self):
        # WHEN/THEN
        with pytest.raises(Exception) as info:
            self.time_parser.string_time_to_milliseconds("FOO")
