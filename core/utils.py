# helpers
from pytubefix import YouTube
from pytubefix.cli import on_progress
import json
import subprocess


def timestamp_to_seconds(time_str):
    parts = list(map(int, time_str.split(":")))
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]  # HH:MM:SS
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]  # MM:SS
    else:
        return int(parts[0])  # Seconds only


def download_yt_video(url: str, directory) -> str:
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        ys = yt.streams.get_highest_resolution()
        file_path = ys.download(output_path=directory)
        return file_path
    except Exception as e:
        raise RuntimeError(f"Failed to download the video using pytube: {str(e)}")


def is_yt_url(url: str) -> str:
    # YT URL formats
    url_patterns = {
        "youtu.be": lambda u: u.split("/")[-1].split("?")[0],
        "youtube.com/watch": lambda u: u.split("v=")[1].split("&")[0],
        "youtube.com/shorts": lambda u: u.split("/")[-1].split("?")[0],
    }

    for pattern, extractor in url_patterns.items():
        if pattern in url:
            try:
                video_id = extractor(url)
                if len(video_id) == 11:  # YT video IDs are 11 characters
                    return True
            except IndexError:
                pass
    return False


def concatenate_scenes(video_path, scene_times, output_path):
    filter_complex_parts = []
    concat_inputs = []

    for i, (start_sec, end_sec) in enumerate(scene_times):
        filter_complex_parts.append(
            f"[0:v]trim=start={start_sec}:end={end_sec},setpts=PTS-STARTPTS[v{i}];"
        )
        filter_complex_parts.append(
            f"[0:a]atrim=start={start_sec}:end={end_sec},asetpts=PTS-STARTPTS[a{i}];"
        )
        concat_inputs.append(f"[v{i}][a{i}]")

    concat_filter = (
        f"{''.join(concat_inputs)}concat=n={len(scene_times)}:v=1:a=1[outv][outa]"
    )
    filter_complex = "".join(filter_complex_parts) + concat_filter

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-filter_complex",
        filter_complex,
        "-map",
        "[outv]",
        "-map",
        "[outa]",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        output_path,
    ]

    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def get_video_duration_seconds(video_path):
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])
