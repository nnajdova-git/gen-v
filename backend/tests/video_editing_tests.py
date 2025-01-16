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

"""Tests for video_editing module."""

import os

from components import video_editing
from PIL import Image
import pytest


@pytest.fixture(name='example_image_path')
def fixture_example_image(tmpdir):
  image_path = os.path.join(tmpdir, 'test_image.png')
  # Create a small example image (e.g., 200x100 pixels, red)
  img = Image.new('RGB', (200, 100), color='red')
  img.save(image_path, 'PNG')
  return image_path


def test_check_file_exists_failure():
  with pytest.raises(FileNotFoundError):
    result = video_editing.check_file_exists('nonexistent_file.mp4')
    assert not result


def test_check_file_exists_success(example_image_path):
  result = video_editing.check_file_exists(example_image_path)
  assert result


def test_image_rescaling(example_image_path):
  rescaled_image = video_editing.rescale_image(
      example_image_path, 200
  )
  assert rescaled_image.height == 200
  assert rescaled_image.width == 400
