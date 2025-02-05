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
    FileNotFoundError: If the video or any image file is not found.
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
