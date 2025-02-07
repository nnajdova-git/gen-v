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
"""Unit tests for vertexai_component.py."""

from unittest import mock

from components import vertexai_component
from models import vertexai_models
import pytest
import requests


@pytest.fixture(name='mock_requests_post')
def mock_requests_post_fixture():
  with mock.patch.object(requests, 'post', autospec=True) as requests_post:
    yield requests_post


@pytest.fixture(name='mock_generate_video_response_200')
def mock_generate_video_response_200_fixture():
  mock_response = mock.Mock()
  mock_response.status_code = 200
  mock_response.json.return_value = {'name': 'test_operation'}
  return mock_response


@pytest.fixture(name='mock_vertexai_generate_video_request')
def mock_vertexai_generate_video_request_fixture():
  return vertexai_models.VertexAIGenerateVideoRequest(
      prompt='A cat playing the piano',
      google_cloud_project_id='my-project',
      google_cloud_storage_uri='gs://my-bucket/my-folder',
  )


@pytest.fixture(name='mock_vertexai_fetch_status_request')
def mock_vertexai_fetch_status_request_fixture():
  return vertexai_models.VertexAIFetchVeoOperationStatusRequest(
      operation_name='test_operation',
      google_cloud_project_id='my-project',
      google_cloud_region='us-central1',
      veo_model_id=vertexai_models.VeoAIModel.VEO_2_0_GENERATE_EXP,
  )


@mock.patch.object(requests, 'post', autospec=True)
def test_generate_video_success(
    mock_post_request,
    mock_generate_video_response_200,
    mock_vertexai_generate_video_request,
):
  mock_post_request.return_value = mock_generate_video_response_200
  response = vertexai_component.generate_video(
      mock_vertexai_generate_video_request, access_token='mock-token'
  )

  assert response.operation_name == 'test_operation'
  mock_post_request.assert_called_once()

  call_args = mock_post_request.call_args
  _, call_kwargs = call_args

  assert (
      call_kwargs['json']['instances'][0]['prompt']
      == mock_vertexai_generate_video_request.prompt
  )
  assert call_kwargs['headers']['Authorization'] == 'Bearer mock-token'


@mock.patch.object(requests, 'post', autospec=True)
def test_generate_video_with_image(
    mock_post_request,
    mock_generate_video_response_200,
    mock_vertexai_generate_video_request,
):
  mock_post_request.return_value = mock_generate_video_response_200

  mock_vertexai_generate_video_request.image = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
  expected_mime_type = 'image/png'

  response = vertexai_component.generate_video(
      mock_vertexai_generate_video_request, access_token='mock-token'
  )

  assert response.operation_name == 'test_operation'
  mock_post_request.assert_called_once()

  _, call_kwargs = mock_post_request.call_args
  assert (
      call_kwargs['json']['instances'][0]['prompt']
      == mock_vertexai_generate_video_request.prompt
  )
  assert (
      call_kwargs['json']['instances'][0]['image']['bytesBase64Encoded']
      == mock_vertexai_generate_video_request.image
  )
  assert (
      call_kwargs['json']['instances'][0]['image']['mimeType']
      == expected_mime_type
  )


def test_fetch_operation_status_success(
    mock_requests_post, mock_vertexai_fetch_status_request
):
  mock_response = mock.Mock()
  mock_response.status_code = 200
  mock_response.json.return_value = {
      'name': 'test_operation',
      'done': True,
      'response': {
          'generated_samples': [{
              'video': {
                  'uri': 'gs://test-bucket/video1.mp4',
                  'encoding': 'video/mp4',
              }
          }]
      },
  }
  mock_requests_post.return_value = mock_response

  response = vertexai_component.fetch_operation_status(
      mock_vertexai_fetch_status_request, access_token='mock-token'
  )

  assert response.done
  assert response.name == 'test_operation'
  assert response.response
  assert (
      response.response.generated_samples[0].video.uri
      == 'gs://test-bucket/video1.mp4'
  )

  mock_requests_post.assert_called_once()
  call_args, call_kwargs = mock_requests_post.call_args
  assert 'fetchPredictOperation' in call_args[0]
  assert call_kwargs['headers']['Authorization'] == 'Bearer mock-token'
  assert call_kwargs['json'] == {'operationName': 'test_operation'}


def test_fetch_operation_status_not_done(
    mock_requests_post, mock_vertexai_fetch_status_request
):
  mock_response = mock.Mock()
  mock_response.status_code = 200
  mock_response.json.return_value = {'name': 'test_operation', 'done': False}
  mock_requests_post.return_value = mock_response

  response = vertexai_component.fetch_operation_status(
      mock_vertexai_fetch_status_request, access_token='mock-token'
  )

  assert not response.done
  assert response.name == 'test_operation'
  assert response.response is None
  mock_requests_post.assert_called_once()
