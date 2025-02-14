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
"""Unit tests for asset routers."""

import datetime
import unittest.mock

from components import asset_utils
import fastapi
from fastapi import testclient
from models import asset_models
import pytest
from routers import assets


@pytest.fixture(name='client')
def client_fixture():
  with testclient.TestClient(assets.router) as test_client:
    yield test_client


@pytest.fixture(name='mock_upload_image_asset')
def mock_upload_image_asset_fixture(monkeypatch):
  mock = unittest.mock.Mock(return_value='mocked_image_id')
  monkeypatch.setattr(asset_utils, 'upload_image_asset', mock)
  return mock


@pytest.fixture(name='mock_get_image_metadata')
def mock_get_image_metadata_fixture(monkeypatch):
  mock = unittest.mock.Mock()
  monkeypatch.setattr(asset_utils, 'get_image_metadata_with_signed_url', mock)
  return mock


def test_upload_image_success(client, mock_upload_image_asset):
  response = client.post(
      '/images',
      files={
          'image': ('test.jpg', b'fake image content', 'image/jpeg'),
      },
      data={'source': 'Brand'},
  )

  assert response.status_code == fastapi.status.HTTP_201_CREATED
  assert response.json()['image_id'] == 'mocked_image_id'
  mock_upload_image_asset.assert_called_once()


def test_get_image_by_id_success(client, mock_get_image_metadata):
  mock_signed_url = 'https://example.com/signed-url'
  mock_image_metadata = asset_models.ImageMetadataResult(
      bucket_name='test-bucket',
      file_path='images/test-image.jpg',
      file_name='test-image.jpg',
      original_file_name='original.jpg',
      full_gcs_path='gs://test-bucket/images/test-image.jpg',
      source='Brand',
      image_name='Test Image',
      context='Test Context',
      date_created=datetime.datetime(2024, 1, 1, 12, 0, 0),
      signed_url=mock_signed_url,
  )
  mock_get_image_metadata.return_value = mock_image_metadata
  response = client.get('/images/test_image_id')
  assert response.status_code == 200
  assert response.json().get('signed_url') == mock_signed_url


def test_get_image_by_id_not_found(client, mock_get_image_metadata):
  mock_get_image_metadata.return_value = None
  with pytest.raises(fastapi.HTTPException) as exc_info:
    client.get('/images/nonexistent_image_id')
  assert exc_info.value.status_code == 404
