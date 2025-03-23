from moviepy import VideoFileClip, concatenate_videoclips
from pytubefix import YouTube
from pytubefix.cli import on_progress


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
    with VideoFileClip(video_path) as video:
        # Extract each scene as a subclip
        clips = []
        for start_sec, end_sec in scene_times:
            scene_clip = video.subclipped(start_sec, end_sec)
            clips.append(scene_clip)

    # Concatenate all clips together
    final_clip = concatenate_videoclips(clips, method="compose")

    # Write the result to the output file
    final_clip.write_videofile(output_path)
    final_clip.close()


def get_video_duration_seconds(video_path):
    with VideoFileClip(video_path) as vf:
        return vf.duration
