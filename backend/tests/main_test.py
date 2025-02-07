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
"""Unit tests for main.py."""
from unittest import mock

from fastapi import testclient
import main
from mocks import api_mocks
from models import api_models
from models import vertexai_models
import pytest
import settings


@pytest.fixture(name='client')
def client_fixture():
  with testclient.TestClient(main.app) as test_client:
    yield test_client


@pytest.fixture(name='patch_env_settings', autouse=True)
def patch_env_settings(monkeypatch):
  monkeypatch.setattr(main, 'env_settings', settings.EnvSettings())


@pytest.fixture(name='mock_fetch_operation_status')
def mock_fetch_operation_status_fixture():
  with mock.patch(
      'main.vertexai_component.fetch_operation_status', autospec=True
  ) as mock_fetch:
    mock_fetch.return_value = (
        vertexai_models.VertexAIFetchVeoOperationStatusResponse(
            name='projects/PROJECT_ID/operations/OPERATION_ID',
            done=False,
            response=None,
        )
    )
    yield mock_fetch


@pytest.fixture(name='mock_get_signed_url')
def mock_get_signed_url_fixture():
  with mock.patch(
      'components.gcs_storage.get_signed_url_from_gcs', autospec=True
  ) as mock_sign:
    mock_sign.return_value = (
        'https://storage.googleapis.com/mock-bucket/mock-object?signature=1234'
    )
    yield mock_sign


@pytest.fixture(name='mock_parse_gcs_uri')
def mock_parse_gcs_uri_fixture():
  with mock.patch(
      'components.gcs_storage.parse_gcs_uri'
  ) as mock_parse:
    mock_parse.return_value = (
        'test-bucket',
        'video.mp4',
    )
    yield mock_parse


def test_veo_generate_video_returns_correct_response(client):
  request = api_models.VeoGenerateVideoRequest(prompt='test prompt')
  response = client.post(
      '/veo/generate', json=request.model_dump(exclude_unset=True)
  )
  assert response.status_code == 200
  assert response.json() == {'operation_name': 'operation_name'}


@mock.patch.object(api_mocks, 'mock_veo_generate_video_response', autospec=True)
def test_veo_generate_video_returns_mock_response_with_use_mocks_true(
    mock_veo_generate_response, client
):
  main.env_settings.use_mocks = True
  mock_veo_generate_response.return_value = mock.create_autospec(
      spec=api_models.VeoGenerateVideoResponse, instance=True
  )

  request = api_models.VeoGenerateVideoRequest(prompt='test prompt')
  response = client.post(
      '/veo/generate', json=request.model_dump(exclude_unset=True)
  )
  assert response.status_code == 200
  mock_veo_generate_response.assert_called_once()

  mock_veo_generate_response.assert_called_once()


def test_veo_operation_status_returns_correct_response(
    client, mock_fetch_operation_status
):
  request = api_models.VeoGetOperationStatusRequest(
      operation_name='projects/PROJECT_ID/operations/OPERATION_ID'
  )
  response = client.post(
      '/veo/operation/status', json=request.model_dump(exclude_unset=True)
  )
  assert response.status_code == 200
  assert response.json() == {
      'name': 'projects/PROJECT_ID/operations/OPERATION_ID',
      'done': False,
      'videos': [],
  }
  mock_fetch_operation_status.assert_called_once()


def test_veo_operation_status_returns_done_with_video(
    client, mock_fetch_operation_status, mock_get_signed_url, mock_parse_gcs_uri
):
  mock_video = vertexai_models.VertexAIVideo(
      uri='gs://test-bucket/video.mp4', encoding='mp4'
  )
  mock_sample = vertexai_models.VertexAIVideoSample(video=mock_video)
  mock_generated_samples = vertexai_models.VertexAIGeneratedSamples(
      generated_samples=[mock_sample]
  )

  mock_fetch_operation_status.return_value = (
      vertexai_models.VertexAIFetchVeoOperationStatusResponse(
          name='projects/PROJECT_ID/operations/OPERATION_ID',
          done=True,
          response=mock_generated_samples,
      )
  )

  request = api_models.VeoGetOperationStatusRequest(
      operation_name='projects/PROJECT_ID/operations/OPERATION_ID'
  )
  response = client.post(
      '/veo/operation/status', json=request.model_dump(exclude_unset=True)
  )
  assert response.status_code == 200

  expected_response = {
      'name': 'projects/PROJECT_ID/operations/OPERATION_ID',
      'done': True,
      'videos': [{
          'uri': 'gs://test-bucket/video.mp4',
          'encoding': 'mp4',
          'signed_uri': (
              'https://storage.googleapis.com/mock-bucket/'
              'mock-object?signature=1234'
          ),
      }],
  }
  assert response.json() == expected_response
  mock_fetch_operation_status.assert_called_once()
  mock_parse_gcs_uri.assert_called_once_with('gs://test-bucket/video.mp4')
  mock_get_signed_url.assert_called_once_with('test-bucket', 'video.mp4')


@mock.patch.object(
    api_mocks, 'mock_veo_operation_status_response', autospec=True
)
def test_veo_operation_status_returns_mock_response_with_use_mocks_true(
    mock_veo_operation_status_response, client
):
  main.env_settings.use_mocks = True
  mock_veo_operation_status_response.return_value = mock.create_autospec(
      spec=api_models.VeoGetOperationStatusResponse, instance=True
  )

  request = api_models.VeoGetOperationStatusRequest(
      operation_name='projects/PROJECT_ID/operations/OPERATION_ID'
  )
  response = client.post(
      '/veo/operation/status', json=request.model_dump(exclude_unset=True)
  )
  assert response.status_code == 200
  mock_veo_operation_status_response.assert_called_once()
