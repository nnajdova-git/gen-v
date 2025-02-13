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
"""Unit tests for api_models.py."""

import unittest.mock

import fastapi
from models import api_models
import pytest


@pytest.mark.parametrize(
    'filename, expected_exception',
    [
        ('good.jpg', None),
        ('good.jpeg', None),
        ('good.png', None),
        ('good.gif', None),
        ('good.JpG', None),
        ('bad.txt', ValueError),
        ('bad.pdf', ValueError),
        ('no_extension', ValueError),
    ],
)
def test_validate_image_type(filename, expected_exception):

  mock_file = unittest.mock.Mock(spec=fastapi.UploadFile)
  mock_file.filename = filename

  if expected_exception:
    with pytest.raises(expected_exception):
      api_models.UploadImageRequest.validate_image_type(mock_file)
  else:
    try:
      api_models.UploadImageRequest.validate_image_type(mock_file)
    except ValueError:
      pytest.fail('Unexpected ValueError raised')
