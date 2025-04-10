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
"""Utilities for image manipulation.

Helper functions for working with images using the Pillow library."""
from PIL import Image
from gen_v import models


def rescale_image_height(image_path: str, desired_height: int) -> Image:
  """Rescales an image to a desired height, maintaining the aspect ratio.

  Args:
    image_path: The path to the image file.
    desired_height: The desired height of the resized image.

  Returns:
    A PIL Image object representing the resized image in RGBA format.
  """
  image = Image.open(image_path)
  scale_factor = desired_height / image.height
  desired_width = int(image.width * scale_factor)
  image = image.resize(
      (desired_width, desired_height), Image.Resampling.LANCZOS
  )
  return image.convert('RGBA')


def rescale_image_width(image_path: str, desired_width: int) -> Image:
  """Rescales an image to a desired width, maintaining the aspect ratio.

  Args:
    image_path: The path to the image file.
    desired_width: The desired width of the resized image.

  Returns:
    A PIL Image object representing the resized image in RGBA format.
  """
  image = Image.open(image_path)
  aspect_ratio = desired_width / image.width
  desired_height = int(image.height * aspect_ratio)
  image = image.resize(
      (desired_width, desired_height), Image.Resampling.LANCZOS
  )
  return image.convert('RGBA')


def rescale_image_to_fit(
    image_path: str, desired_width: int, desired_height: int
):
  """Rescales an image to fit within desired dimensions, keeps aspect ratio.

  Chooses between rescaling by height or width to ensure the image fits
  within the given dimensions without distortion.

  Args:
    image_path: Path to the image file.
    desired_width: The desired width of the resized image.
    desired_height: The desired height of the resized image.

  Returns:
    A PIL Image object representing the resized image.
  """
  image = Image.open(image_path)
  original_width, original_height = image.size

  image_aspect_ratio = original_width / original_height
  desired_aspect_ratio = desired_width / desired_height

  if image_aspect_ratio > desired_aspect_ratio:
    # Image is wider than desired, rescale by width
    return rescale_image_width(image_path, desired_width)
  else:
    # Image is taller than desired, rescale by height
    return rescale_image_height(image_path, desired_height)


def hex_to_rgb(hex_color_string: str) -> tuple[int, int, int] | None:
  """Converts a hexadecimal color string to an RGB tuple.

  Handles 6-digit hex strings, optionally prefixed with '#'. Input is
  case-insensitive.

  Args:
    hex_color_string: The hex code to convert (e.g., "#FF0000", "ff0000")

  Returns:
    A tuple containing the integer values for Red, Green, and Blue
    (e.g., (255, 0, 0)).

  Raises:
    ValueError: If the input string is not a valid 6-digit hex color (after
      removing '#').
  """
  hex_code = hex_color_string.lstrip('#')
  if len(hex_code) != 6:
    raise ValueError(
        f'Invalid hex color string "{hex_color_string}". '
        'Must be 3 or 6 hex digits (optional leading "#").'
    )
  else:
    red = int(hex_code[0:2], 16)
    green = int(hex_code[2:4], 16)
    blue = int(hex_code[4:6], 16)
    return red, green, blue


def place_rescaled_image_on_background(
    foreground_image_path: str,
    background_width: int,
    background_height: int,
    background_color: models.RGBColor,
    output_path: str,
) -> Image:
  """Place fit-rescaled foreground image onto specified background.

  Rescales an image to fit within desired dimensions, keeps aspect ratio,
  and places it on top of a background image of the specified colour.

  Args:
    foreground_image_path: Path to the foreground image file.
    background_width: The desired width of the background image.
    background_height: The desired height of the background image.
    background_color: The RGB color of the background image.
    output_path: Local path to save the resulting image.

  Returns:
    A PIL Image object representing the resulting image.
  """
  rescaled_image = rescale_image_to_fit(
      foreground_image_path, background_width, background_height
  )

  background_image = Image.new(
      'RGB', (background_width, background_height), background_color.to_tuple()
  )

  # Calculate offset to centre the image.
  x_offset = (background_width - rescaled_image.width) // 2
  y_offset = (background_height - rescaled_image.height) // 2

  background_image.paste(rescaled_image, (x_offset, y_offset), rescaled_image)

  background_image.save(output_path)
  return background_image


def replace_background_color(
    image_path: str,
    target_color: models.RGBColor,
    replacement_color: models.RGBColor,
    recolored_image_local_path: str,
    threshold: int = 25,
):
  """Replaces the target color in an image with the replacement color.

  Args:
    image_path: Path to the input image.
    target_color: The color to be replaced.
    replacement_color: The new color to use.
    recolored_image_local_path: Path to save the recolored image.
    threshold: The color distance threshold for edge detection.

  Raises:
    ValueError: If a problem occurs when saving the output.
  """
  with Image.open(image_path) as image:
    image = image.convert('RGBA')
    image_data = image.load()
    width, height = image.size
    replacement_rgba = (
        replacement_color.r,
        replacement_color.g,
        replacement_color.b,
        255,
    )
    for x in range(width):
      for y in range(height):
        current_pixel_rgba = image_data[x, y]
        current_color = models.RGBColor.from_tuple(current_pixel_rgba[:3])
        if current_color.distance_to(target_color) < threshold:
          image_data[x, y] = replacement_rgba
    try:
      image.save(recolored_image_local_path)
    except (ValueError, OSError) as save_err:
      raise ValueError(
          f'Failed to save image to {recolored_image_local_path}: {save_err}'
      ) from save_err
