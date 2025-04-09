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
