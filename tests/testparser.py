from src.parser import Parser
from tests.testbase import TestBase
from tests.utils import Utils


class TestParser(TestBase):
    """
    This class contains unit tests for UsernameHelper class
    """

    parser = Parser()
    utils = Utils()

    def test_create_intervals(self):
        """
        test_alphanum_split for this pattern: "alpha_number_alpha".
        """
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        video = vi_output["videos"][0]
        # WHEN
        actual = self.parser.create_intervals(video, "FOO")
        # THEN
        self.assert_equals(
            actual, self.utils.read_json_from_resources("intervals.json", True)
        )

    def test_insert_items_to_intervals(self):
        """
        test_alphanum_split for this pattern: "alpha_number_alpha".
        """
        # GIVEN
        expected = {
            0: {"bar_0": {}, "bar_2": [{"FOO": "BAZ"}]},
            10000: {"bar_1": {}, "bar_2": [{"FOO": "BAZ"}]},
            200000: {"bar_2": {}},
            30000: {"bar_3": {}},
            40000: {"bar_4": {}},
        }
        occurred_intervals = [0, 10000]
        item_tuple = ("bar_2", {"FOO": "BAZ"})
        intervals = {
            0: {"bar_0": {}},
            10000: {"bar_1": {}},
            200000: {"bar_2": {}},
            30000: {"bar_3": {}},
            40000: {"bar_4": {}},
        }
        # WHEN
        actual = self.parser.insert_items_to_intervals(
            occurred_intervals, item_tuple, intervals
        )
        # THEN
        self.assert_equals(actual, expected)

    def test_parse_transcript(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        transcript = vi_output["videos"][0]["insights"]["transcript"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_transcript(transcript, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources("intervals-with-transcript.json", True),
        )

    def test_parse_ocr(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        ocr = vi_output["videos"][0]["insights"]["ocr"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_ocr(ocr, intervals)
        # THEN
        self.assert_equals(
            actual, self.utils.read_json_from_resources("intervals-with-ocr.json", True)
        )

    def test_parse_keywords(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        keyword = vi_output["videos"][0]["insights"]["keywords"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_keywords(keyword, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources("intervals-with-keyword.json", True),
        )

    def test_parse_topics(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        topics = vi_output["videos"][0]["insights"]["topics"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_topics(topics, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources("intervals-with-topics.json", True),
        )

    def test_parse_faces(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        faces = vi_output["videos"][0]["insights"]["faces"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_faces(faces, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources("intervals-with-faces.json", True),
        )

    def test_parse_labels(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        labels = vi_output["videos"][0]["insights"]["labels"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_labels(labels, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources("intervals-with-labels.json", True),
        )

    def test_parse_named_locations(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        named_locations = vi_output["videos"][0]["insights"]["namedLocations"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_named_locations(named_locations, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources(
                "intervals-with-named-locations.json", True
            ),
        )

    def test_parse_named_people(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        named_people = vi_output["videos"][0]["insights"]["namedPeople"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_named_people(named_people, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources(
                "intervals-with-named-people.json", True
            ),
        )

    def test_parse_audio_effects(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        audio_effects = vi_output["videos"][0]["insights"]["audioEffects"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_audio_effects(audio_effects, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources(
                "intervals-with-audio-effects.json", True
            ),
        )

    def test_parse_sentiments(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        sentiments = vi_output["videos"][0]["insights"]["sentiments"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_sentiments(sentiments, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources("intervals-with-sentiments.json", True),
        )

    def test_parse_emotions(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        emotions = vi_output["videos"][0]["insights"]["emotions"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_emotions(emotions, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources("intervals-with-emotions.json", True),
        )

    def test_parse_visual_content_moderation(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        vcm = vi_output["videos"][0]["insights"]["visualContentModeration"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_visual_content_moderation(vcm, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources(
                "intervals-with-visual-content-moderation.json", True
            ),
        )

    def test_parse_frame_patterns(self):
        # GIVEN
        vi_output = self.utils.read_json_from_resources("vi-output.json")
        frame_patterns = vi_output["videos"][0]["insights"]["framePatterns"]
        intervals = self.parser.create_intervals(vi_output["videos"][0], "FOO")
        # WHEN
        actual = self.parser.parse_frame_patterns(frame_patterns, intervals)
        # THEN
        self.assert_equals(
            actual,
            self.utils.read_json_from_resources(
                "intervals-with-frame-patterns.json", True
            ),
        )
