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
"""Functions to combine audio, video, and image and output to one video."""

import os

import moviepy
from PIL import Image


def create_video_with_brand_and_audio(
    video_path: str,
    logo_image_path: str,
    audio_path: str,
    output_path: str,
    logo_image_position: tuple[str, str] | tuple[int, int],
    logo_image_duration: float | None = None,
    logo_image_height: int | None = None,
    audio_start_time: float | None = 0,
    temp_media_path: str = '/tmp',
) -> None:
  """Creates a video with a brand image & audio overlaid on an existing video.

  This function takes a video, an image (for branding), and an audio file,
  and combines them to produce a new video with the image and audio overlaid.
  The image is resized to the specified height and positioned as needed.

  Args:
      video_path: Path to the input video file (MP4).
      logo_image_path: Path to the brand image file (PNG).
      audio_path: Path to the input audio file (MP3).
      output_path: Path to save the output video file (MP4).
      logo_image_position: Tuple (horizontal, vertical) specifying the position
        of the image. Can be ("left", "top"), ("center", "center"), ("right",
        "bottom"), etc., or numerical coordinates (x, y) from the top-left
        corner.
      logo_image_duration: Duration for which the image should be displayed (in
        seconds). If None, the image will be displayed for the entire video
        duration. Defaults to None.
      logo_image_height: Desired height of the brand image in pixels.
      audio_start_time: Time (in seconds) at which the audio should start
        playing. Defaults to 0.
      temp_media_path: Path to a directory for temporary media files. Defaults
        to "/tmp".

  Raises:
      FileNotFoundError: If any of the input files (video, image, or audio)
        do not exist.
      ValueError: If the provided position is invalid.

  Returns:
    None. The function saves the output video to the specified output_path.
  """

  if not os.path.exists(video_path):
    raise FileNotFoundError(f'Video file not found: {video_path}')
  if not os.path.exists(logo_image_path):
    raise FileNotFoundError(f'Image file not found: {logo_image_path}')
  if not os.path.exists(audio_path):
    raise FileNotFoundError(f'Audio file not found: {audio_path}')

  video = moviepy.VideoFileClip(video_path)

  pil_image = Image.open(logo_image_path)
  scale_factor = logo_image_height / pil_image.height
  new_width = int(pil_image.width * scale_factor)
  pil_image = pil_image.resize(
      (new_width, logo_image_height), Image.Resampling.LANCZOS
  )
  temp_image_path = os.path.join(temp_media_path, 'resized-logo.png')
  pil_image.save(temp_image_path)

  brand_image = (
      moviepy.ImageClip(temp_image_path)
      .with_duration(
          logo_image_duration if logo_image_duration else video.duration
      )
      .with_position(logo_image_position)
  )

  audio = moviepy.AudioFileClip(audio_path)
  audio = audio.with_start(audio_start_time)

  video = video.with_audio(audio)

  final_clip = moviepy.CompositeVideoClip([video, brand_image])
  final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

  video.close()
  brand_image.close()
  audio.close()
  final_clip.close()
