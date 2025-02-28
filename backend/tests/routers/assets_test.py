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
from models import data_models
import pytest
from routers import assets
import settings


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


@pytest.fixture(name='patch_env_settings', autouse=True)
def patch_env_settings_fixture(monkeypatch):
  monkeypatch.setattr(asset_utils, 'env_settings', settings.EnvSettings())


@pytest.fixture(name='mock_image_data_model')
def mock_image_data_model_fixture():
  yield data_models.Image(
      bucket_name='mock-bucket',
      file_path='images/mock_image.jpg',
      file_name='mock_image.jpg',
      original_file_name='original_mock.jpg',
      full_gcs_path='gs://mock-bucket/images/mock_image.jpg',
      source='Brand',
      image_name='Mock Image',
      context='Mock Context',
      date_created=datetime.datetime(2025, 1, 1, 10, 0, 0),
  )


@pytest.fixture(name='mock_image_metadata_result')
def mock_image_metadata_result_fixture(mock_image_data_model):
  mock_image = unittest.mock.MagicMock(spec=asset_models.ImageMetadataResult)
  mock_image.bucket_name = mock_image_data_model.bucket_name
  mock_image.file_path = mock_image_data_model.file_path
  mock_image.file_name = mock_image_data_model.file_name
  mock_image.original_file_name = mock_image_data_model.original_file_name
  mock_image.full_gcs_path = mock_image_data_model.full_gcs_path
  mock_image.source = mock_image_data_model.source
  mock_image.image_name = mock_image_data_model.image_name
  mock_image.context = mock_image_data_model.context
  mock_image.date_created = mock_image_data_model.date_created
  mock_image.signed_url = 'https://example.com/signed-url'
  yield mock_image


@pytest.fixture(name='patch_image_metadata_result')
def patch_image_metadata_result_fixture(mock_image_metadata_result):
  with unittest.mock.patch(
      'routers.assets.asset_models.ImageMetadataResult'
  ) as mock_image:
    mock_image.return_value = mock_image_metadata_result
    yield mock_image


@pytest.fixture(name='patch_asset_mocks_module')
def patch_asset_mocks_module_fixture(mock_image_metadata_result):
  with unittest.mock.patch('routers.assets.asset_mocks') as mock_module:
    mock_module.mock_get_image_metadata_with_signed_url.return_value = (
        mock_image_metadata_result
    )
    yield mock_module


@pytest.fixture(name='patch_firestore_crud_module')
def patch_firestore_crud_module_fixture(mock_image_data_model):
  with unittest.mock.patch('routers.assets.firestore_crud') as mock_firestore:
    mock_firestore.query_collection.return_value = [mock_image_data_model]
    yield mock_firestore


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


def test_get_images_by_type_with_success(
    client,
    patch_asset_mocks_module,
    patch_firestore_crud_module,
    patch_image_metadata_result,
):
  response = client.get('/images/type/Brand')
  assert response.status_code == 200
  patch_asset_mocks_module.mock_get_image_metadata_with_signed_url.assert_not_called()
  patch_firestore_crud_module.query_collection.assert_called_once()
  patch_image_metadata_result.assert_called_once()


def test_get_images_by_type_with_mocks(
    client, patch_asset_mocks_module, patch_firestore_crud_module
):
  assets.env_settings.use_mocks = True
  response = client.get('/images/type/Brand')
  assert response.status_code == 200
  patch_asset_mocks_module.mock_get_image_metadata_with_signed_url.assert_called_once()
  patch_firestore_crud_module.query_collection.assert_not_called()
