import mimetypes
import os
import shutil
import tempfile
import time
import traceback
import typing

import pydantic
import requests
from google import genai
from google.genai import types

from .utils import (
    concatenate_scenes,
    download_yt_video,
    get_video_duration_seconds,
    is_yt_url,
    timestamp_to_seconds,
)


class TimeStamp(pydantic.BaseModel):
    start_time: str = pydantic.Field(
        ...,
        description="Start timestamp of the segment. Strictly follow HH:MM:SS format. For example, '00:10:23'",
    )
    end_time: str = pydantic.Field(
        ...,
        description="End timestamp of the segment. Strictly follow HH:MM:SS format. For example, '00:13:56'",
    )


class HighlightOut(typing.TypedDict):
    timestamp: typing.Optional[list[TimeStamp]] = pydantic.Field(
        default=[], description="List of timestamps of the key moments, if any."
    )


class VisualGroundingOut(typing.TypedDict):
    timestamp: typing.Optional[TimeStamp] = pydantic.Field(
        default=None, description="Timestamp of the moment/incident"
    )


class VideoIntelligence:
    def __init__(self, path: str):
        self.model_id = "models/gemini-2.0-flash-001"  # pro - "gemini-2.0-flash"
        self.num_retries = 3

        temp_directory = ".assets"
        os.makedirs(temp_directory, exist_ok=True)

        # https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/video-analysis/youtube_video_analysis.ipynb
        # https://googleapis.github.io/python-genai/
        self.client = genai.Client()

        self.token_count = {"input": 0, "output": 0, "total": 0}
        try:
            # check video type and create part accordingly
            if is_yt_url(path):
                self.video_path = download_yt_video(path, temp_directory)
                self.video_part = self.get_video_part(self.video_path)

            elif path.startswith("https") and path.endswith(".mp4"):
                self.video_path = os.path.join(temp_directory, "video.mp4")
                # download video
                response = requests.get(path, stream=True)
                with open(self.video_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)

                self.video_part = self.get_video_part(self.video_path)

            elif os.path.exists(path):
                self.video_path = os.path.join(temp_directory, "video.mp4")
                shutil.move(path, self.video_path)
                self.video_part = self.get_video_part(path)

            else:
                raise ValueError(
                    "Could not parse the given path into file. Check if it is valid"
                )

            # gen config
            self.gen_config = dict(
                candidate_count=1,
                temperature=1.1,
                top_k=65,
                top_p=0.95,
                max_output_tokens=4096,
            )

            self.model_chat = self.client.chats.create(
                model=self.model_id,
                # TODO: add video to chat history while instantiation (couldn't get it working as of now)
                config=types.GenerateContentConfig(
                    system_instruction="You are an expert video analyzer, and your job is to answer the user's query based on the provided video. Always respond in a natural tone.",
                    **self.gen_config,
                ),
            )

            # send the video once, to be at the top of the chat history to be questioned on (kinda works atleast for now)
            self.model_chat.send_message(self.video_part)
            self.token_count["input"] = self.token_count["total"] = (
                self.client.models.count_tokens(
                    model=self.model_id,
                    contents=self.model_chat.get_history(curated=False),
                ).total_tokens
            )  # need comprehensive, as is

            self.video_seconds = get_video_duration_seconds(self.video_path)

        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Failed to process video content: {str(e)}")

    def chat(self, message: str):
        try:
            response = self.model_chat.send_message(message)
            self.update_token_count(response.usage_metadata)
            return response.text

        except Exception as e:
            return f"\n\nI apologize, I encountered an error: {str(e)}"

    def get_correct_response(self, contents, sys_instruction, out_schema):
        for _ in range(self.num_retries):
            print("Try {}".format(_), flush=True)
            broken_formatting = False  # fresh try

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction,
                    response_mime_type="application/json",
                    response_schema=out_schema,
                    **self.gen_config,
                ),
            )
            self.update_token_count(response.usage_metadata)

            segment_timestamps = []
            if timestamps := response.parsed.get("timestamp", None):
                print("Timestamps extracted! Validating it...", flush=True)
                timestamps = (
                    [timestamps] if not isinstance(timestamps, list) else timestamps
                )

                for __, ts in enumerate(timestamps):
                    print(ts)
                    # TODO: Check whether last end_second and current start_second is same, if so replace last end_second with current endsecond
                    start_second = timestamp_to_seconds(ts.start_time)
                    end_second = timestamp_to_seconds(ts.end_time)

                    if (start_second < self.video_seconds) and (
                        end_second < self.video_seconds
                    ):
                        if end_second - start_second == 0:
                            continue  # start and end are same
                        segment_timestamps.append((start_second, end_second))

                    else:
                        broken_formatting = True
                        break  # wrong timestamp str, retry

                if broken_formatting:
                    continue
                return segment_timestamps

            else:
                # no segment found []
                return segment_timestamps

        # evry retry failed :|
        if broken_formatting:
            raise RuntimeError(
                "There is an error with parsing due to incorrect formatting from the model. Try again!"
            )

    def generate_highlight(self):
        SYSTEM_INSTRUCTION = (
            "You are an expert video analyst. Carefully examine the provided video thoroughly. Identify and provide timestamps of any potential highlights, significant events, key, or noteworthy moments found within the video. Keep it concise",
        )

        try:
            segments = self.get_correct_response(
                [self.video_part], SYSTEM_INSTRUCTION, HighlightOut
            )

            if segments:
                with tempfile.NamedTemporaryFile(
                    suffix=".mp4", delete=False
                ) as tmp_file:
                    temp_output = tmp_file.name
                    concatenate_scenes(self.video_path, segments, temp_output)
                return temp_output, "Highlights generated!"

            else:
                return None, "No highlight found!"

        except Exception as e:
            return None, "Process interrupted. Error occured: {}".format(str(e))

    def identify_moment(self, query: str):
        SYSTEM_PROMPT = "You are a highly skilled expert in video analysis with deep expertise in frame-by-frame inspection, scene recognition, and precise timestamp identification. Your task is to carefully examine a given video and accurately determine the exact timestamp(s) that correspond to the user's query, only if it exist in the video. You must ensure a thorough and detailed analysis before making a decision. Maintain accuracy, attention to detail while delivering results with concistent and correct formatting."
        try:
            segment = self.get_correct_response(
                [self.video_part, query.strip().capitalize()],
                SYSTEM_PROMPT,
                VisualGroundingOut,
            )

            if segment:
                with tempfile.NamedTemporaryFile(
                    suffix=".mp4", delete=False
                ) as tmp_file:
                    temp_output = tmp_file.name
                    concatenate_scenes(self.video_path, segment, temp_output)
                return temp_output, "Moment Identified!"

            else:
                return None, "Moment could not be found within the video"

        except Exception as e:
            return None, "Process interrupted, Error occured: {}".format(str(e))

    def get_video_part(self, video_path):
        # check size (if less tha n 20MB it can be included inline)
        size_in_bytes = os.path.getsize(video_path)
        video_size = round((size_in_bytes / (1024 * 1024)), 2)  # Convert bytes to MB

        if video_size > 19.5:
            # upload to files API
            video_file = self.client.files.upload(file=video_path)
            while video_file.state.name == "PROCESSING":
                time.sleep(1)
                video_file = self.client.files.get(name=video_file.name)

            if video_file.state.name == "FAILED":
                raise ValueError(video_file.state.name)
            video_part = video_file

        else:
            with open(video_path, "rb") as vf:
                video_bytes = vf.read()
            mt, _ = mimetypes.guess_type(video_path)
            video_part = types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type=mt)
            )

        return video_part

    def update_token_count(self, usage):
        usage_metadat_dict = usage.model_dump()
        for i, j in zip(
            ["input", "output", "total"],
            ["prompt_token_count", "candidates_token_count", "total_token_count"],
        ):
            if v := usage_metadat_dict[j]:
                self.token_count[i] += v
