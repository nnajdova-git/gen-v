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
"""Video editing and processing functions using MoviePy.

This module provides utilities for manipulating video clips after generation.
"""
from typing import Any, Callable
import mediapy
from PIL import Image
from gen_v import models
from gen_v import storage as gcs
from gen_v import utils
import moviepy as mp


def display_image(
    image_path: str,
    display_function: Callable[[Any], None] | None = None,
    **kwargs,
) -> None:
  """Displays image using a provided function or defaults to mediapy.show_image.

  Args:
    image_path: The local path to the image file.
    display_function: A callable that takes the image as its first argument and
      displays it. If None, defaults to mediapy.show_image.
    **kwargs: Additional keyword arguments passed directly to the display
      function. Useful for things like title or height.

  Raises:
    FileNotFoundError: If the image at the file path cannot be found.
    Image.UnidentifiedImageError: If the image couldn't be read by Pillow
  """
  if display_function is None:
    display_function = mediapy.show_image
    kwargs["title"] = kwargs.get("title", "Image")
    kwargs["border"] = True
  try:
    input_image = Image.open(image_path)
    display_function(input_image, **kwargs)
  except FileNotFoundError:
    print(f"Error: Image file not found: {image_path}")
  except Image.UnidentifiedImageError:
    print(f"Error: Could not open or read image file: {image_path}")


def overlay_image_on_video(
    input_video: models.VideoInput,
    images: list[models.ImageInput],
    output_video_path: models.VideoInput,
) -> mp.VideoFileClip:
  """Overlays images on a video.

  Args:
      input_video: A VideoInput object with the input video.
      images: A list of ImageInput objects with the images to overlay.
      output_video_path: A VideoInput object with the output video path.

  Returns:
      The modified video clip if successful, or None if an error occurred.
  """
  print("Started overlay_image_on_video...")

  # gcs_filename = gcs.get_file_name_from_gcs_url(input_video.path)
  local_video_path = input_video.path
  final_clip = mp.VideoFileClip(local_video_path)
  fade_duration = 1

  video_file_name = gcs.get_file_name_from_gcs_url(output_video_path.path)
  local_output_video_path = f"/content/overlay_output_{video_file_name}"

  for img in images:
    overlay_file_name = gcs.get_file_name_from_gcs_url(img.path)
    no_extension_video_file_name = video_file_name.split(".")[0]

    image_file_name = f"{no_extension_video_file_name}_{overlay_file_name}"
    local_img_path = gcs.download_file_locally(img.path, image_file_name)

    image_file = Image.open(local_img_path)
    image_file = image_file.convert("RGBA")
    local_img_path_png = local_img_path.replace(".jpg", ".png")
    image_file.save(local_img_path_png)

    if img.height > 0:
      resized_img_path = local_img_path_png.replace(".png", "_resized.png")
      rescaled_img = utils.rescale_image_height(local_img_path_png, img.height)
      rescaled_img.save(resized_img_path)
      local_img_path_png = resized_img_path
    img_clip = (
        mp.ImageClip(local_img_path_png)
        .with_duration(img.duration)
        .with_position(img.position)
    )
    img_clip = img_clip.with_effects(
        [mp.vfx.CrossFadeIn(fade_duration)]
    ).with_effects([mp.vfx.CrossFadeOut(fade_duration)])

    final_clip = mp.CompositeVideoClip(
        [final_clip, img_clip.with_start(img.start)]
    )

  # Write the output video
  final_clip.write_videofile(
      local_output_video_path,
      codec="libx264",
      fps=final_clip.fps,
      bitrate="8000k",
  )
  output_uri = output_video_path.path
  gcs.upload_file_to_gcs(local_output_video_path, output_uri)
  final_clip.close()
  return output_uri
