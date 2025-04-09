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
"""Unit tests for image utils."""
import os
from PIL import Image
import pytest
from gen_v.utils import image


@pytest.fixture(name='sample_images_paths')
def fixture_sample_images(tmpdir):
  """Creates a few sample images for testing."""
  image_paths = []
  for i in range(3):
    image_path = os.path.join(tmpdir, f'image{i}.png')
    img = Image.new('RGB', (200, 100), color=(0, 255, 0))
    img.save(image_path)
    image_paths.append(image_path)
  return image_paths


def test_rescale_image_height(sample_images_paths):
  """Tests correct height and aspect ratio after rescaling by height."""
  rescaled_image = image.rescale_image_height(sample_images_paths[0], 200)
  assert rescaled_image.height == 200
  assert rescaled_image.width == 400
  assert rescaled_image.mode == 'RGBA'
