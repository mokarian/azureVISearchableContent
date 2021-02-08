import json

from parser.timeparser import TimeParser


class Parser:
    """
    This class in responsible to Parse VI JSON file into
    intervals of occurrence based on the defined interval in TimeParser
    the result will be used to upload to Azure search index
    """

    def __init__(self):
        self.time_parser = TimeParser()

    def parse_vi_json(self, vi_json):
        """
        This method parses JSON file (created by VI) and distribute each Item
        under videos[0]["insights"] to different intervals having
        fixed duration (e.g. 10000 milliseconds interval)
        :param vi_json:
        :return: list of intervals
        """
        show_name = vi_json["name"]
        for video in vi_json["videos"]:
            insights = video["insights"]
            intervals = self.create_intervals(video, show_name)
            if "transcript" in insights:
                intervals = self.parse_transcript(insights["transcript"], intervals)
            if "ocr" in insights:
                intervals = self.parse_ocr(insights["ocr"], intervals)
            if "keywords" in insights:
                intervals = self.parse_keywords(insights["keywords"], intervals)
            if "topics" in insights:
                intervals = self.parse_topics(insights["topics"], intervals)
            if "faces" in insights:
                intervals = self.parse_faces(insights["faces"], intervals)
            if "labels" in insights:
                intervals = self.parse_labels(insights["labels"], intervals)
            if "namedLocations" in insights:
                intervals = self.parse_named_locations(
                    insights["namedLocations"], intervals
                )
            if "namedPeople" in insights:
                intervals = self.parse_named_people(insights["namedPeople"], intervals)
            if "audioEffects" in insights:
                intervals = self.parse_audio_effects(
                    insights["audioEffects"], intervals
                )
            if "sentiments" in insights:
                intervals = self.parse_sentiments(insights["sentiments"], intervals)
            if "emotions" in insights:
                intervals = self.parse_emotions(insights["emotions"], intervals)
            if "visualContentModeration" in insights:
                intervals = self.parse_visual_content_moderation(
                    insights["visualContentModeration"], intervals
                )
            if "framePatterns" in insights:
                intervals = self.parse_frame_patterns(
                    insights["framePatterns"], intervals
                )
            if "brands" in insights:
                intervals = self.parse_brands(insights["brands"], intervals)
            return intervals

    def create_intervals(self, video, show_name):
        """
        This method creates a dictionary of intervals
        :param video:
        :param show_name:
        :return:
        """
        dictionary_of_intervals = dict()
        video_id = video["id"] if "id" in video else ""
        account_id = video["accountId"] if "accountId" in video else ""
        external_id = video["externalId"] if "externalId" in video else ""
        meta_data = video["metadata"] if "metadata" in video else ""
        duration_in_milliseconds = int(
            self.time_parser.string_time_to_milliseconds(video["insights"]["duration"])
        )
        for i in range(0, duration_in_milliseconds):
            if i % self.time_parser.interval_in_milliseconds == 0:
                start_time = self.time_parser.seconds_to_time_string(i / 1000)
                end_time = (
                    self.time_parser.seconds_to_time_string(duration_in_milliseconds)
                    if i + self.time_parser.interval_in_milliseconds
                    >= duration_in_milliseconds
                    else self.time_parser.seconds_to_time_string(
                        (i + self.time_parser.interval_in_milliseconds) / 1000
                    )
                )
                dictionary_of_intervals[i] = {
                    "id": video_id
                    + "-"
                    + str(int(i / self.time_parser.interval_in_milliseconds)),
                    "accountId": account_id,
                    "externalId": external_id,
                    "name": show_name,
                    "metaData": meta_data,
                    "startTime": start_time,
                    "endTime": end_time,
                }
        return dictionary_of_intervals

    @staticmethod
    def insert_items_to_intervals(occurred_intervals, item_tuple, intervals):
        """
        This method inserts occurred intervals into the
        dictionary of intervals (that covers all  the video)
        :param occurred_intervals:
        :param item_tuple: a tuple of Item .
         e.g. : ("faces", {"face": face["name"],
                 "assets": "{...}"})
        :return:
        """
        for i in occurred_intervals:
            if item_tuple[0] in intervals[i]:
                intervals[i][item_tuple[0]].append(item_tuple[1])
            else:
                intervals[i][item_tuple[0]] = [item_tuple[1]]
        return intervals

    def parse_transcript(self, transcripts, intervals):
        """
        this  method parses transcript and add
         data to dictionary of intervals
        :param transcripts:
        :param intervals:
        :return:
        """
        for transcript in transcripts:
            if transcript["text"] != "" and transcript["confidence"] > 0.5:
                for instance in transcript["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )

                    assets = {
                        "id": transcript["id"],
                        "speakerId": transcript["speakerId"],
                        "language": transcript["language"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    transcript_object = {
                        "transcript": transcript["text"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("transcripts", transcript_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_ocr(self, ocrs, intervals):
        """
        this  method parses ocrs and add related data
        to dictionary of intervals
        :param ocrs:
        :param intervals:
        :return:
        """
        for ocr in ocrs:
            if ocr["text"] != "" and ocr["confidence"] > 0.5:
                for instance in ocr["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": ocr["id"],
                        "left": ocr["left"],
                        "top": ocr["top"],
                        "width": ocr["width"],
                        "height": ocr["height"],
                        "language": ocr["language"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    ocr_object = {
                        "ocr": ocr["text"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("ocrs", ocr_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_keywords(self, keywords, intervals):
        """
        this  method parses keywords and add related
        data to dictionary of intervals
        :param keywords:
        :param intervals:
        :return:
        """
        for keyword in keywords:
            if keyword["text"] != "" and keyword["confidence"] > 0.5:
                for instance in keyword["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": keyword["id"],
                        "language": keyword["language"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    ocr_object = {
                        "keyword": keyword["text"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("keywords", ocr_object)

                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_topics(self, topics, intervals):
        """
        this  method parses topics and add related
        data to dictionary of intervals
        :param topics:
        :param intervals:
        :return:
        """
        for topic in topics:
            if topic["name"] != "" and topic["confidence"] > 0.5:
                for instance in topic["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": topic["id"],
                        "referenceId": topic["referenceId"]
                        if "referenceId" in topic
                        else "",
                        "referenceType": topic["referenceType"]
                        if "referenceType" in topic
                        else "",
                        "iptcName": topic["iptcName"] if "iptcName" in topic else "",
                        "iabName": topic["iabName"] if "iabName" in topic else "",
                        "language": topic["language"] if "language" in topic else "",
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    ocr_object = {
                        "topic": topic["name"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("topics", ocr_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_faces(self, faces, intervals):
        """
        this  method parses faces and add related
        data to dictionary of intervals
        it extracts faces from insights and thumbnails
        :param faces:
        :param intervals:
        :return:
        """
        for face in faces:
            if face["name"] != "" and face["confidence"] > 0.5:
                for instance in face["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": face["id"],
                        "description": face["description"]
                        if "description" in face
                        else "",
                        "thumbnailId": face["thumbnailId"]
                        if "thumbnailId" in face
                        else "",
                        "knownPersonId": face["knownPersonId"]
                        if "knownPersonId" in face
                        else "",
                        "title": face["title"] if "title" in face else "",
                        "imageUrl": face["imageUrl"] if "imageUrl" in face else "",
                        "thumbnailsIds": instance["thumbnailsIds"]
                        if "thumbnailsIds" in instance
                        else "",
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    face_object = {
                        "face": face["name"],
                        "assets": json.dumps(assets),
                    }
                    tuples = ("faces", face_object)

                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
                if "thumbnails" in face:
                    for thumbnail in face["thumbnails"]:
                        thumbnail_url = thumbnail["fileName"]
                        for instance in thumbnail["instances"]:
                            start = self.time_parser.string_time_to_milliseconds(
                                instance["start"]
                            )
                            end = self.time_parser.string_time_to_milliseconds(
                                instance["end"]
                            )
                            occurred_intervals = self.time_parser.get_related_intervals(
                                start, end
                            )
                            assets = {
                                "id": face["id"],
                                "description": face["description"]
                                if "description" in face
                                else "",
                                "thumbnailId": face["thumbnailId"]
                                if "thumbnailId" in face
                                else "",
                                "knownPersonId": face["knownPersonId"]
                                if "knownPersonId" in face
                                else "",
                                "title": face["title"] if "title" in face else "",
                                "imageUrl": face["imageUrl"]
                                if "imageUrl" in face
                                else "",
                                "thumbnailsIds": thumbnail["id"],
                                "start": instance["start"],
                                "end": instance["end"],
                            }
                            thumbnail_object = {
                                "thumbnail": thumbnail_url,
                                "assets": json.dumps(assets),
                            }
                            tuples = ("thumbnails", thumbnail_object)
                            intervals = self.insert_items_to_intervals(
                                occurred_intervals, tuples, intervals
                            )

        return intervals

    def parse_labels(self, labels, intervals):
        """
        this  method parses labels and add related
        data to dictionary of intervals
        :param labels:
        :param intervals:
        :return:
        """
        for label in labels:
            if label["name"] != "":
                for instance in label["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": label["id"],
                        "referenceId": label["referenceId"]
                        if "referenceId" in label
                        else "",
                        "language": label["language"] if "language" in label else "",
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    label_object = {
                        "label": label["name"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("labels", label_object)

                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_named_locations(self, named_locations, intervals):
        """
        this  method parses namedLocations and add
        related data to dictionary of intervals
        :param named_locations:
        :param intervals:
        :return:
        """
        for namedLocation in named_locations:
            if namedLocation["name"] != "" and namedLocation["confidence"] > 0.5:
                for instance in namedLocation["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": namedLocation["id"],
                        "referenceId": namedLocation["referenceId"]
                        if "referenceId" in namedLocation
                        else "",
                        "referenceUrl": namedLocation["referenceUrl"]
                        if "referenceUrl" in namedLocation
                        else "",
                        "description": namedLocation["description"]
                        if "description" in namedLocation
                        else "",
                        "confidence": namedLocation["confidence"]
                        if "confidence" in namedLocation
                        else "",
                        "instanceSource": instance["instanceSource"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    label_object = {
                        "namedLocation": namedLocation["name"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("namedLocations", label_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_named_people(self, named_people, intervals):
        """
        this  method parses namedPeople and add
        related data to dictionary of intervals
        :param named_people:
        :param intervals:
        :return:
        """
        for name in named_people:
            if name["name"] != "" and name["confidence"] > 0.5:
                for instance in name["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": name["id"],
                        "referenceId": name["referenceId"]
                        if "referenceId" in name
                        else "",
                        "referenceUrl": name["referenceUrl"]
                        if "referenceUrl" in name
                        else "",
                        "description": name["description"]
                        if "description" in name
                        else "",
                        "confidence": name["confidence"]
                        if "confidence" in name
                        else "",
                        "instanceSource": instance["instanceSource"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    label_object = {
                        "namedPerson": name["name"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("namedPeople", label_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_audio_effects(self, audio_effects, intervals):
        """
        this  method parses audioEffects and add
        related data to dictionary of intervals
        :param audio_effects:
        :param intervals:
        :return:
        """
        for audioEffect in audio_effects:
            if audioEffect["type"] != "":
                for instance in audioEffect["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": audioEffect["id"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    label_object = {
                        "audioEffect": audioEffect["type"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("audioEffects", label_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_sentiments(self, sentiments, intervals):
        """
        this  method parses sentiments and add
        related data to dictionary of intervals
        :param sentiments:
        :param intervals:
        :return:
        """
        for sentiment in sentiments:
            if sentiment["sentimentType"] != "" and sentiment["averageScore"] > 0.5:
                for instance in sentiment["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": sentiment["id"],
                        "averageScore": sentiment["averageScore"]
                        if "averageScore" in sentiment
                        else "",
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    label_object = {
                        "sentimentType": sentiment["sentimentType"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("sentiments", label_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_emotions(self, emotions, intervals):
        """
        this  method parses emotions and add
        related data to dictionary of intervals
        :param emotions:
        :param intervals:
        :return:
        """
        for emotion in emotions:
            if emotion["type"] != "":
                for instance in emotion["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": emotion["id"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    label_object = {
                        "emotion": emotion["type"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("emotions", label_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_visual_content_moderation(self, visual_contents, intervals):
        """
        this  method parses visual_contents and
        add related data to dictionary of intervals
        :param visual_contents:
        :param intervals:
        :return:
        """
        for content in visual_contents:
            for instance in content["instances"]:
                start = self.time_parser.string_time_to_milliseconds(instance["start"])
                end = self.time_parser.string_time_to_milliseconds(instance["end"])
                occurred_intervals = self.time_parser.get_related_intervals(start, end)
                assets = {
                    "id": content["id"],
                    "start": instance["start"],
                    "end": instance["end"],
                }
                label_object = {
                    "adultScore": str(content["adultScore"]),
                    "assets": json.dumps(assets),
                }

                tuples = ("adultScores", label_object)
                intervals = self.insert_items_to_intervals(
                    occurred_intervals, tuples, intervals
                )
            for instance in content["instances"]:
                start = self.time_parser.string_time_to_milliseconds(instance["start"])
                end = self.time_parser.string_time_to_milliseconds(instance["end"])
                occurred_intervals = self.time_parser.get_related_intervals(start, end)
                assets = {
                    "id": content["id"],
                    "start": instance["start"],
                    "end": instance["end"],
                }
                label_object = {
                    "racyScore": str(content["racyScore"]),
                    "assets": json.dumps(assets),
                }

                tuples = ("racyScores", label_object)
                intervals = self.insert_items_to_intervals(
                    occurred_intervals, tuples, intervals
                )
        return intervals

    def parse_frame_patterns(self, frame_patterns, intervals):
        """
        this  method parses framePatterns and add
        related data to dictionary of intervals
        :param frame_patterns:
        :param intervals:
        :return:
        """
        for pattern in frame_patterns:
            if pattern["confidence"] > 0.5:
                for instance in pattern["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": pattern["id"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    frame_patterns_object = {"assets": json.dumps(assets)}

                    tuples = ("framePatterns", frame_patterns_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_brands(self, brands, intervals):
        """
        this  method parses brands and add related
        data to dictionary of intervals
        :param brands:
        :param intervals:
        :return:
        """
        for brand in brands:
            if brand["name"] != "" and brand["confidence"] > 0.5:
                for instance in brand["instances"]:
                    start = self.time_parser.string_time_to_milliseconds(
                        instance["start"]
                    )
                    end = self.time_parser.string_time_to_milliseconds(instance["end"])
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = {
                        "id": brand["id"],
                        "confidence": brand["confidence"],
                        "referenceId": brand["referenceId"],
                        "referenceType": brand["referenceType"],
                        "description": brand["description"],
                        "brandType": instance["brandType"],
                        "start": instance["start"],
                        "end": instance["end"],
                    }
                    frame_patterns_object = {
                        "brand": brand["name"],
                        "assets": json.dumps(assets),
                    }

                    tuples = ("brands", frame_patterns_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals

    def parse_custom_model(self, custom_model_json, intervals, model_property):
        for item in custom_model_json:
            for prediction in item["imagePrediction"]["predictions"]:
                if prediction["probability"] != "" and prediction["probability"] > 0.5:
                    start = self.time_parser.string_time_to_milliseconds(
                        item["thumbnailMetadata"]["starttime"]
                    )
                    if "endtime" in item["thumbnailMetadata"]:
                        end = self.time_parser.string_time_to_milliseconds(
                            item["thumbnailMetadata"]["endtime"]
                        )
                    else:
                        end = self.time_parser.string_time_to_milliseconds(
                            item["thumbnailMetadata"]["starttime"]
                        )
                    occurred_intervals = self.time_parser.get_related_intervals(
                        start, end
                    )
                    assets = item["thumbnailMetadata"]
                    assets["probability"] = prediction["probability"]
                    custom_item_object = {
                        model_property["tagName"]: prediction["tagName"],
                        "assets": json.dumps(assets),
                    }
                    tuples = (model_property["tagGroup"], custom_item_object)
                    intervals = self.insert_items_to_intervals(
                        occurred_intervals, tuples, intervals
                    )
        return intervals
