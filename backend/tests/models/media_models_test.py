# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the TextInput class."""

from models import media
import pydantic
import pytest


@pytest.mark.parametrize(
    'test_input',
    [
        {
            'text': 'Hello, world!',
            'font_size': 12,
            'method': 'label',
            'size': (640, 480),
        },
        {
            'filename': 'text.txt',
            'font_size': 12,
            'method': 'label',
            'size': (640, 480),
        },
        {
            'text': 'Caption Text',
            'font_size': 20,
            'method': 'caption',
            'size': (1280, 720),
        },
        {
            'filename': 'text.txt',
            'size': (None, None),
            'font_size': 16,
            'method': 'label',
        },
        {
            'text': 'Test',
            'font_size': 14,
            'margin': (10, 20),
            'color': 'red',
            'bg_color': (0, 255, 0, 128),
            'method': 'label',
            'size': (500, 100),
            'transparent': True,
        },
        {
            'text': 'Test',
            'font_size': 14,
            'margin': (10, 5, 10, 5),
            'color': 'red',
            'bg_color': (0, 255, 0),
            'method': 'label',
            'size': (500, 200),
            'transparent': False,
        },
        {
            'text': 'Centered Text',
            'size': (300, 150),
            'text_align': 'center',
            'horizontal_align': 'center',
            'vertical_align': 'center',
            'font_size': 20,
            'method': 'label',
        },
        {
            'text': 'Some text',
            'font_size': 18,
            'stroke_color': 'blue',
            'stroke_width': 2,
            'method': 'label',
            'size': (400, 150),
        },
        {
            'text': 'Hex Colors',
            'font_size': 16,
            'color': '#FF0000',
            'bg_color': '#00FF00',
            'stroke_color': '#0000FF',
            'method': 'label',
            'size': (200, 100),
        },
        {
            'text': 'None values',
            'font_size': 14,
            'font': None,
            'margin': (None, None),
            'bg_color': None,
            'stroke_color': None,
            'duration': None,
            'start_time': 0.0,
            'method': 'label',
            'size': (150, 80),
        },
    ],
)
def test_text_input_valid(test_input):
  """Test valid cases of TextInput."""
  try:
    media.TextInput(**test_input)
  except pydantic.ValidationError:
    pytest.fail('Unexpected pydantic.ValidationError raised')


@pytest.mark.parametrize(
    'test_input,expected_error',
    [
        (
            {'font_size': 12, 'method': 'label'},
            'Either text or filename must be provided.',
        ),  # Missing text/filename
        (
            {'text': 'Hello', 'method': 'label'},
            "Font size must be provided when method is 'label'.",
        ),  # Missing font_size
        (
            {'text': 'Hello', 'font_size': 12, 'method': 'caption'},
            "Size must be provided when method is 'caption'.",
        ),  # Missing size
        (
            {'text': 'Hello', 'font_size': 12, 'margin': (10,)},
            'Margin tuple must have length 2 or 4.',
        ),  # Invalid margin
        (
            {'text': 'Hello', 'font_size': 12, 'margin': (10, 20, 30)},
            'Margin tuple must have length 2 or 4.',
        ),  # Invalid margin
        (
            {'text': 'Hello', 'font_size': 12, 'margin': (-10, 20)},
            'Margin values must be non-negative.',
        ),  # Negative margin
        (
            {
                'text': 'Test',
                'font_size': 20,
                'method': 'invalid_method',
                'size': (100, 100),
            },
            "Method must be either 'label' or 'caption'.",
        ),  # Invalid method
        (
            {
                'text': 'Test',
                'size': (300, 150),
                'text_align': 'justify',
                'font_size': 20,
                'method': 'label',
            },
            "Text align must be one of 'center', 'left', or 'right'.",
        ),  # Invalid align
        (
            {
                'text': 'Test',
                'size': (300, 150),
                'horizontal_align': 'middle',
                'font_size': 20,
                'method': 'label',
            },
            "Horizontal align must be one of 'center', 'left', or 'right'.",
        ),  # Invalid align
        (
            {
                'text': 'Test',
                'size': (300, 150),
                'vertical_align': 'middle',
                'font_size': 20,
                'method': 'label',
            },
            "Vertical align must be one of 'center', 'top', or 'bottom'.",
        ),  # Invalid align
        (
            {
                'text': 'Test',
                'size': (300, 150),
                'font_size': 20,
                'margin': (1, 'abc'),
                'method': 'label',
            },
            'Margin values must be numbers or None.',
        ),  # Invalid margin
        (
            {
                'text': 'Test',
                'font_size': 14,
                'bg_color': (0, 255, 0),
                'transparent': True,
            },
            (
                'Background colour should be a touple of 4 when Transparent is'
                ' True.'
            ),  # Invalid bg_color length when transparent is True
        ),
    ],
)
def test_text_input_invalid(test_input, expected_error):
  """Test invalid cases, expecting pydantic.ValidationError."""
  with pytest.raises(pydantic.ValidationError) as excinfo:
    media.TextInput(**test_input)
  print(excinfo.value)
  assert expected_error in str(excinfo.value)
