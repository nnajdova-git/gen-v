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
"""Unit tests for asset_utils.py."""
import datetime
import io
import unittest.mock

from components import asset_utils
from components import firestore_crud
from components import gcs_storage
import fastapi
from mocks import asset_mocks
from models import api_models
from models import asset_models
import pytest
import settings


@pytest.fixture(name='patch_env_settings', autouse=True)
def patch_env_settings_fixture(monkeypatch):
  monkeypatch.setattr(asset_utils, 'env_settings', settings.EnvSettings())


@pytest.fixture(name='mock_input_data')
def mock_input_data_fixture():
  file_content = b'fake image content'
  temp_file = io.BytesIO(file_content)
  mock_upload_file = fastapi.UploadFile(
      filename='test_image.jpg',
      file=temp_file,
  )
  return asset_models.ImageUploadInput(
      image=mock_upload_file,
      source=api_models.ImageSource.BRAND,
      session_id='test_session',
      image_name='Test Image',
      context='Test Context',
  )


@pytest.fixture(name='mock_write_to_gcs')
def mock_write_to_gcs_fixture():
  with unittest.mock.patch('components.gcs_storage.write_to_gcs') as mock_write:
    yield mock_write


@pytest.fixture(name='mock_create_document')
def mock_create_document_fixture():
  with unittest.mock.patch(
      'components.firestore_crud.create_document'
  ) as mock_create:
    yield mock_create


@pytest.fixture(name='mock_image_metadata_result')
def mock_image_metadata_result_fixture():
  yield asset_models.ImageMetadataResult(
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


@pytest.fixture(name='mock_firestore_crud_module')
def mock_firestore_crud_module_fixture(mock_image_metadata_result):
  mock_firestore = unittest.mock.Mock(spec=firestore_crud)
  mock_firestore.get_document.return_value = mock_image_metadata_result
  yield mock_firestore


@pytest.fixture(name='mock_gcs_storage_module')
def mock_gcs_storage_module_fixture():
  yield unittest.mock.Mock(spec=gcs_storage)


@pytest.fixture(name='mock_asset_mocks_module')
def mock_asset_mocks_module_fixture(mock_image_metadata_result):
  mock_module = unittest.mock.Mock(spec=asset_mocks)
  mock_module.mock_get_image_metadata_with_signed_url.return_value = (
      mock_image_metadata_result
  )
  yield mock_module


def test_upload_image_asset(
    mock_create_document,
    mock_write_to_gcs,
    mock_input_data,
):
  test_image_id = 'test_id'
  mock_input_data.image_id = test_image_id
  mock_create_document.return_value = test_image_id
  image_id = asset_utils.upload_image_asset(mock_input_data)

  assert image_id == test_image_id

  mock_write_to_gcs.assert_called_once()
  mock_create_document.assert_called_once()


def test_upload_image_asset_use_mocks(
    mock_input_data, mock_write_to_gcs, mock_create_document
):
  asset_utils.env_settings.use_mocks = True
  mock_input_data.image_id = 'test_id'
  image_id = asset_utils.upload_image_asset(mock_input_data)
  assert image_id == 'test_id'
  mock_write_to_gcs.assert_not_called()
  mock_create_document.assert_not_called()


def test_get_image_metadata_with_signed_url(
    mock_firestore_crud_module,
    mock_gcs_storage_module,
    mock_asset_mocks_module,
    mock_image_metadata_result,
):
  test_signed_url = 'https://test-signed-url.com'
  mock_gcs_storage_module.get_signed_url_from_gcs.return_value = test_signed_url
  mock_image_metadata_result.signed_url = test_signed_url
  result = asset_utils.get_image_metadata_with_signed_url(
      'test_id',
      firestore_utils=mock_firestore_crud_module,
      storage_utils=mock_gcs_storage_module,
      mocks_module=mock_asset_mocks_module,
  )
  assert result == mock_image_metadata_result
  mock_asset_mocks_module.assert_not_called()
  mock_firestore_crud_module.get_document.assert_called_once()


def test_get_image_metadata_with_signed_url_use_mocks(
    mock_firestore_crud_module,
    mock_gcs_storage_module,
    mock_asset_mocks_module,
    mock_image_metadata_result,
):
  asset_utils.env_settings.use_mocks = True
  result = asset_utils.get_image_metadata_with_signed_url(
      'test_id', mocks_module=mock_asset_mocks_module
  )
  assert result == mock_image_metadata_result
  mock_asset_mocks_module.mock_get_image_metadata_with_signed_url.assert_called_with(
      'test_id'
  )
  mock_firestore_crud_module.assert_not_called()
  mock_gcs_storage_module.assert_not_called()
