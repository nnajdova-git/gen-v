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
"""Unit tests for asset_models.py."""

import datetime
import unittest.mock

from components import gcs_storage
import fastapi
from models import asset_models
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
      asset_models.ImageUploadInput.validate_image_type(mock_file)
  else:
    try:
      asset_models.ImageUploadInput.validate_image_type(mock_file)
    except ValueError:
      pytest.fail('Unexpected ValueError raised')


@pytest.mark.parametrize(
    'filename, expected_extension',
    [
        ('image.jpg', '.jpg'),
        ('image.JPG', '.jpg'),
        ('image.jpeg', '.jpeg'),
        ('image.png', '.png'),
        ('image.gif', '.gif'),
        ('no_extension', ''),
        ('', ''),
        ('"".jpg', '.jpg'),
        ('folder/image.png', '.png'),
        ('folder.with.dots/image.png', '.png'),
        ('image', ''),
        ('.hidden.jpg', '.jpg'),
        ('...manydots.jpg', '.jpg'),
    ],
)
def test_get_file_extension(filename, expected_extension):

  mock_file = unittest.mock.Mock(spec=fastapi.UploadFile)
  mock_file.filename = filename

  input_data = asset_models.ImageUploadInput(
      image=mock_file,
      source='Brand',
  )
  assert input_data.get_file_extension() == expected_extension


def test_image_metadata_result_generate_signed_url():
  mock_storage_utils = unittest.mock.Mock(spec=gcs_storage)
  mock_signed_url = 'https://example.com/mock-signed-url'
  mock_storage_utils.get_signed_url_from_gcs.return_value = mock_signed_url

  image_metadata = asset_models.ImageMetadataResult(
      bucket_name='test-bucket',
      file_path='images/test-image.jpg',
      file_name='test-image.jpg',
      original_file_name='original.jpg',
      full_gcs_path='gs://test-bucket/images/test-image.jpg',
      source='Brand',
      image_name='Test Image',
      context='Test Context',
      date_created=datetime.datetime(2024, 1, 1, 12, 0, 0),
      signed_url='',
  )

  image_metadata.generate_signed_url(storage_utils=mock_storage_utils)

  mock_storage_utils.get_signed_url_from_gcs.assert_called_once_with(
      bucket_name='test-bucket', file_name='images/test-image.jpg'
  )
  assert image_metadata.signed_url == mock_signed_url
