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

import unittest.mock

from components import asset_utils
import fastapi
from fastapi import testclient
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
