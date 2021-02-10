class TestBase:
    """
    This class contains test base class
    """

    @staticmethod
    def assert_equals(actual, expected):
        """
        asserts the equality of two objects
        """
        assert (
            actual == expected
        ), "Expected to have result equal to '{}', but received:'{}'".format(
            expected, actual
        )
