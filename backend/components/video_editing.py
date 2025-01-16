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

from PIL import Image


def check_file_exists(file_path: str) -> bool:
  """Checks if a file exists at the given path.

  Args:
    file_path: The path to the file.

  Returns:
    True if the file exists, False otherwise.

  Raises:
    FileNotFoundError: If the file does not exist.
  """
  exists = os.path.exists(file_path)
  if not exists:
    raise FileNotFoundError(f"Video file not found: {file_path}")
  return exists


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

