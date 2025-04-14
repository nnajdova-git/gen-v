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
    kwargs['title'] = kwargs.get('title', 'Image')
    kwargs['border'] = True
  try:
    input_image = Image.open(image_path)
    display_function(input_image, **kwargs)
  except FileNotFoundError:
    print(f'Error: Image file not found: {image_path}')
  except Image.UnidentifiedImageError:
    print(f'Error: Could not open or read image file: {image_path}')
