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
"""Unit tests for media models."""
import math
import pytest
from gen_v import models


def test_video_input_model_creation():
  """A simple unit test to validate the creation of VideoInputs."""
  video_input = models.VideoInput(path='/a/path/to/a/file')
  assert video_input.path == '/a/path/to/a/file'


@pytest.mark.parametrize(
    'r, g, b, expected_r, expected_g, expected_b',
    [
        (10, 128, 200, 10, 128, 200),
        (0, 0, 0, 0, 0, 0),
        (255, 255, 255, 255, 255, 255),
    ],
    ids=['standard', 'min_values', 'max_values'],
)
def test_valid_creation_direct(r, g, b, expected_r, expected_g, expected_b):
  """Test creating RGBColor directly with valid integer values."""
  color = models.RGBColor(r=r, g=g, b=b)
  assert color.r == expected_r
  assert color.g == expected_g
  assert color.b == expected_b


@pytest.mark.parametrize(
    'rgb_tuple, expected_r, expected_g, expected_b',
    [
        ((10, 128, 200), 10, 128, 200),
        ((0, 0, 0), 0, 0, 0),
        ((255, 255, 255), 255, 255, 255),
    ],
    ids=['standard', 'min_values', 'max_values'],
)
def test_valid_creation_from_tuple(
    rgb_tuple, expected_r, expected_g, expected_b
):
  """Test creating RGBColor using from_tuple with valid tuples."""
  color = models.RGBColor.from_tuple(rgb_tuple)
  assert color.r == expected_r
  assert color.g == expected_g
  assert color.b == expected_b


@pytest.mark.parametrize(
    'r, g, b, expected_tuple',
    [
        (10, 128, 200, (10, 128, 200)),
        (0, 0, 0, (0, 0, 0)),
        (255, 255, 255, (255, 255, 255)),
    ],
    ids=['standard', 'min_values', 'max_values'],
)
def test_to_tuple_conversion(r, g, b, expected_tuple):
  """Test converting an RGBColor instance back to a tuple."""
  color = models.RGBColor(r=r, g=g, b=b)
  assert color.to_tuple() == expected_tuple


def test_color_distance():
  """Tests the distance_to method for calculating Euclidean distance."""
  color1 = models.RGBColor(r=0, g=0, b=0)
  color2 = models.RGBColor(r=255, g=255, b=255)
  color3 = models.RGBColor(r=30, g=40, b=0)
  color4 = models.RGBColor(r=0, g=0, b=0)
  color5 = models.RGBColor(r=3, g=4, b=0)

  assert color1.distance_to(color1) == pytest.approx(0.0)
  assert color1.distance_to(color4) == pytest.approx(0.0)

  assert color1.distance_to(color5) == pytest.approx(5.0)

  expected_max_dist = math.sqrt(255**2 + 255**2 + 255**2)
  assert color1.distance_to(color2) == pytest.approx(expected_max_dist)

  dist_1_to_3 = color1.distance_to(color3)
  dist_3_to_1 = color3.distance_to(color1)
  assert dist_1_to_3 == pytest.approx(dist_3_to_1)

  assert color1.distance_to(color3) == pytest.approx(50.0)
