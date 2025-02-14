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
"""Defines mock responses for testing assets.

This module is used to mock responses with assets. This is useful for
development and testing when you don't want to make actual calls to the Google
Cloud endpoint.
"""
import datetime
from models import asset_models


def mock_get_image_metadata_with_signed_url(
    image_id: str,
) -> asset_models.ImageMetadataResult | None:
  """Mocks the get_image_metadata_with_signed_url function.

  Args:
      image_id: The ID of the image (used to simulate different responses).

  Returns:
      A mock ImageMetadataResult object, or None if the ID is set to
      simulate a "not found" scenario.
  """
  if image_id == 'not_found':
    return None

  mock_image = asset_models.ImageMetadataResult(
      bucket_name='mock-bucket',
      file_path='images/mock_image.jpg',
      file_name='mock_image.jpg',
      original_file_name='original_mock.jpg',
      full_gcs_path='gs://mock-bucket/images/mock_image.jpg',
      source='Brand',
      image_name='Mock Image',
      context='Mock Context',
      date_created=datetime.datetime(2025, 1, 1, 10, 0, 0),
      signed_url='/assets/gen-v-logo.png',
  )
  return mock_image
