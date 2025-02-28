# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Functions to perform video editing."""
import contextlib
import os
import tempfile
import uuid

from models import media
import moviepy
from PIL import Image


def check_file_exists(file_path: str) -> None:
  """Checks if a file exists at the given path.

  Args:
    file_path: The path to the file.

  Raises:
    FileNotFoundError: If the file does not exist.
  """
  if not os.path.exists(file_path):
    raise FileNotFoundError(f'Media file not found: {file_path}')


def rescale_image(image_path: str, desired_height: int) -> Image.Image:
  """Rescales an image to the desired height and returns it.

  Args:
    image_path: The path to the image to be rescaled.
    desired_height: The desired height of the rescaled image.

  Returns:
    The rescaled image.
  """
  image = Image.open(image_path)
  scale_factor = desired_height / image.height
  desired_width = int(image.width * scale_factor)
  image = image.resize(
      (desired_width, desired_height), Image.Resampling.LANCZOS
  )
  return image


def add_image_clips_to_video(
    video_path: str,
    image_inputs: list[media.ImageInput],
    output_path: str,
) -> None:
  """Adds one or more image clips to a video clip.

  This function overlays images onto a video, allowing for customization of
  position, duration, and size.  It handles resizing the images to maintain
  aspect ratio if a height is specified.

  Args:
    video_path: Path to the video file.
    image_inputs: List of ImageInput objects, each representing an image to
      overlay.
    output_path: Path to save the output video.

  Raises:
    ValueError: If no image inputs are provided.
  """
  #  Check that files have been saved locally
  check_file_exists(video_path)
  if not image_inputs:
    raise ValueError('No image inputs provided.')

  video = moviepy.VideoFileClip(video_path)
  image_clips = []

  with tempfile.TemporaryDirectory() as temp_dir:
    for image_input in image_inputs:
      check_file_exists(image_input.path)
      resized_img_path = ''

      if image_input.height:
        resized_img_path = os.path.join(
            temp_dir, f'resized-image-{uuid.uuid4()}.png'
        )
        rescaled_img = rescale_image(image_input.path, image_input.height)
        rescaled_img.save(resized_img_path)

      duration = image_input.duration or video.duration

      image_clips.append(
          moviepy.ImageClip(resized_img_path or image_input.path)
          .with_duration(duration)
          .with_position(image_input.position)
      )

    final_clip = moviepy.CompositeVideoClip([video] + image_clips)
    final_clip.write_videofile(output_path, codec='libx264')

    video.close()
    for image_clip in image_clips:
      image_clip.close()
    final_clip.close()


def concatenate_video_clips(
    video_inputs: list[media.VideoInput], output_path: str
) -> None:
  """Concatenates multiple video clips together.

  Args:
      video_inputs: List of paths to the video files.
      output_path: Path to save the output video.

  Raises:
      ValueError: If no video inputs are provided.
  """
  if not video_inputs:
    raise ValueError('No video inputs provided.')

  video_clips = []

  for video_input in video_inputs:
    check_file_exists(video_input.path)
    video_clips.append(moviepy.VideoFileClip(video_input.path))

  final_clip = moviepy.concatenate_videoclips(video_clips)
  final_clip.write_videofile(output_path, codec='libx264')

  for video_clip in video_clips:
    video_clip.close()
  final_clip.close()


def calculate_audio_duration(
    i: int, audio_inputs: list[media.AudioInput], video_duration: float
) -> float:
  """Calculates the duration for each audio clip.

  Args:
    i: Index of the audio clip.
    audio_inputs: List of AudioInput objects.
    video_duration: Duration of the video in seconds.

  Returns:
    Duration of the audio clip in seconds.
  """
  if not audio_inputs[i].duration:
    next_start_time = (
        audio_inputs[i + 1].start_time
        if i < len(audio_inputs) - 1
        else video_duration
    )
    duration = next_start_time - audio_inputs[i].start_time
  else:
    duration = audio_inputs[i].duration
  return duration


def load_audio_clips(
    audio_inputs: list[media.AudioInput], video_duration: float
) -> list[moviepy.AudioFileClip]:
  """Loads audio clips from a list of paths.

  Args:
    audio_inputs: List of paths to the audio files.
    video_duration: Duration of the video in seconds.

  Returns:
    List of AudioFileClip objects.
  """
  audio_clips = []

  for i, audio_input in enumerate(audio_inputs):
    check_file_exists(audio_input.path)

    # If no duration calculate it based on the next start or video duration
    duration = calculate_audio_duration(i, audio_inputs, video_duration)

    audio_clip = (
        moviepy.AudioFileClip(audio_input.path)
        .with_start(audio_input.start_time)
        .with_duration(duration)
    )
    audio_clips.append(audio_clip)
  return audio_clips


def add_audio_clips_to_video(
    video_path: str,
    audio_inputs: list[media.AudioInput],
    output_path: str,
) -> None:
  """Adds one or more audio clips to a video clip.

  If several videos are provided without start times and duration, they will be
  played in successive order, and the duration will be equal for each of the
  audio clips.

  Args:
    video_path: Path to the video file.
    audio_inputs: List of AudioInput objects, each representing an audio clip to
      add.
    output_path: Path to save the output video.

  Raises:
    ValueError: If the number of audio start times or durations does not match
    the number of audio clips.
  """
  check_file_exists(video_path)
  if not audio_inputs:
    raise ValueError('No audio inputs provided.')

  video = moviepy.VideoFileClip(video_path)

  audio_clips = load_audio_clips(audio_inputs, video.duration)

  final_audio = moviepy.CompositeAudioClip(audio_clips)
  final_clip = video.with_audio(final_audio).with_duration(video.duration)
  final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

  video.close()
  for audio in audio_clips:
    audio.close()
  final_clip.close()


@contextlib.contextmanager
def load_text_clips(
    video_path: str, text_inputs: list[media.TextInput]
):
  """Loads text clips from a list of text inputs and a video clip.

  Args:
    video_path: The path to the video clip to use as a reference for duration.
    text_inputs: List of TextInput objects.

  Yields:
    List of TextClip objects and the video clip.
  """
  text_clips = []

  with moviepy.VideoFileClip(video_path) as video:
    for text_input in text_inputs:
      if text_input.filename:
        check_file_exists(text_input.filename)

      if not text_input.duration:
        text_input.duration = video.duration

      text_clip = moviepy.TextClip(
          **text_input.model_dump(exclude={'start_time'})
      ).with_start(text_input.start_time)

      text_clips.append(text_clip)

    try:
      yield [video] + text_clips
    finally:
      for text_clip in text_clips:
        text_clip.close()


def add_text_clips_to_video(
    video_path: str, text_inputs: list[media.TextInput], output_path: str
) -> None:
  """Adds text to a video clip.

  Args:
    video_path: Path to the video file.
    text_inputs: List of TextInput objects, each representing the text to add.
    output_path: Path to save the output video.

  Raises:
    FileNotFoundError: If the video file is not found.
  """
  check_file_exists(video_path)

  with load_text_clips(video_path, text_inputs) as clips:
    with moviepy.CompositeVideoClip(clips) as final_clip:
      final_clip.write_videofile(output_path, codec='libx264')

