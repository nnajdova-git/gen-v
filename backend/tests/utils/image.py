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


@pytest.fixture(name='sample_image_files')
def fixture_sample_image_files(tmpdir):
  """Creates sample wide (200x100) and tall (100x200) images.

  Returns:
    A dictionary mapping descriptive names ('wide', 'tall') to image file
    paths.
  """
  image_paths = {}

  wide_image_path = os.path.join(tmpdir, 'wide_test_image.png')
  img_wide = Image.new('RGB', (200, 100), color=(0, 255, 0))
  img_wide.save(wide_image_path)
  image_paths['wide'] = wide_image_path

  tall_image_path = os.path.join(tmpdir, 'tall_test_image.png')
  img_tall = Image.new('RGB', (100, 200), color=(0, 0, 255))
  img_tall.save(tall_image_path)
  image_paths['tall'] = tall_image_path

  return image_paths


def test_rescale_image_height(sample_image_files):
  """Tests correct height and aspect ratio after rescaling by height."""
  rescaled_image = image.rescale_image_height(
      sample_image_files['wide'], desired_height=200
  )
  assert rescaled_image.height == 200
  assert rescaled_image.width == 400
  assert rescaled_image.mode == 'RGBA'


def test_rescale_image_width(sample_image_files):
  """Tests correct width and aspect ratio after rescaling by width."""
  rescaled_image = image.rescale_image_width(
      sample_image_files['wide'], desired_width=500
  )
  assert rescaled_image.height == 250
  assert rescaled_image.width == 500
  assert rescaled_image.mode == 'RGBA'


def test_rescale_image_to_fit_wide_image_into_square(sample_image_files):
  """Tests fitting a wide image into a square box.

  The image is wider than the box (400x200 vs 100x100).
  It should be scaled based on width, resulting in 100x50.
  """
  rescaled_img = image.rescale_image_to_fit(
      sample_image_files['wide'], desired_width=100, desired_height=100
  )
  assert rescaled_img.width == 100
  assert rescaled_img.height == 50


def test_rescale_image_to_fit_tall_image_into_square(sample_image_files):
  """Tests fitting a tall image into a square box.

  The image is taller than the box (200x400 vs 100x100).
  It should be scaled based on height, resulting in 50x100.
  """
  rescaled_img = image.rescale_image_to_fit(
      sample_image_files['tall'], desired_width=100, desired_height=100
  )
  assert rescaled_img.width == 50
  assert rescaled_img.height == 100


@pytest.mark.parametrize(
    'hex_input, expected_rgb_tuple',
    [
        ('#FF0000', (255, 0, 0)),
        ('00FF00', (0, 255, 0)),
        ('0000FF', (0, 0, 255)),
        ('#ffffff', (255, 255, 255)),
        ('000000', (0, 0, 0)),
        ('#fF0aA9', (255, 10, 169)),
        ('123456', (18, 52, 86)),
    ],
)
def test_hex_to_rgb_valid_inputs(hex_input, expected_rgb_tuple):
  """Tests successful conversion for various valid hex strings."""
  assert image.hex_to_rgb(hex_input) == expected_rgb_tuple


@pytest.mark.parametrize(
    'invalid_hex_input',
    [
        '#FF000',
        'FF000',
        '#FF00001',
        'FF00001',
        'FFG000',
        '#FFG000',
        '',
        '#',
        ' #FF0000FF 00 00',
        '#F00',
    ],
)
def test_hex_to_rgb_invalid_inputs_raise_value_error(invalid_hex_input):
  """Tests that invalid hex strings raise a ValueError."""
  with pytest.raises(ValueError):
    image.hex_to_rgb(invalid_hex_input)
