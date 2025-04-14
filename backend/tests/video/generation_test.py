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
"""Unit tests for video generation."""
from unittest import mock
from google import genai
from google.genai import types
import pytest
import requests
from gen_v import models
from gen_v.video import generation


@pytest.fixture(name='mock_requests_post')
def mock_requests_post_fixture():
  with mock.patch.object(requests, 'post', autospec=True) as requests_post:
    yield requests_post


def test_send_request_to_google_api(mock_requests_post):
  mock_api_endpoint = 'https://europe-west2-aiplatform.googleapis.com/v1'
  mock_data = {'key': 'value'}
  mock_access_token = 'my-token-abc'
  expected_response_json = {
      'name': 'test_operation',
      'done': True,
  }

  mock_response = mock.Mock()
  mock_response.status_code = 200
  mock_response.json.return_value = expected_response_json
  mock_requests_post.return_value = mock_response

  response = generation.send_request_to_google_api(
      mock_api_endpoint, mock_data, mock_access_token
  )

  assert response == expected_response_json

  mock_requests_post.assert_called_once()
  call_args, call_kwargs = mock_requests_post.call_args
  assert call_args[0] == mock_api_endpoint
  assert (
      call_kwargs['headers']['Authorization'] == f'Bearer {mock_access_token}'
  )
  assert call_kwargs['json'] == mock_data


@mock.patch('google.genai.types.Part.from_bytes')
def test_get_gemini_prompt_success_with_image(
    mock_part_from_bytes, png_file_in_fs
):
  """Tests a successful call with an image, using a mocked client."""
  test_prompt = 'Describe the provided image.'
  test_model_name = 'gemini-test-model'
  request = models.GeminiPromptRequest(
      prompt_text=test_prompt,
      image_file_path=png_file_in_fs,
      model_name=test_model_name,
  )

  assert request.image_bytes is not None
  assert request.mime_type == 'image/png'

  mock_client = mock.Mock(spec=genai.Client)
  mock_response = mock.Mock()
  mock_response.text = 'Successfully described image!'
  mock_client.models.generate_content.return_value = mock_response

  mock_image_part_instance = mock.Mock(spec=types.Part)
  mock_part_from_bytes.return_value = mock_image_part_instance

  result = generation.get_gemini_generated_video_prompt(
      request_data=request, client=mock_client
  )
  assert result == mock_response.text

  mock_part_from_bytes.assert_called_once_with(
      data=request.image_bytes, mime_type=request.mime_type
  )

  mock_client.models.generate_content.assert_called_once()
  _, call_kwargs = mock_client.models.generate_content.call_args

  assert call_kwargs['model'] == test_model_name


@mock.patch('gen_v.video.generation.time.sleep')
@mock.patch('gen_v.video.generation.send_request_to_google_api')
def test_fetch_operation_success_first_try(
    mock_send_request, mock_sleep, mock_app_settings
):
  """Tests fetch_operation succeeds when API returns 'done': True."""
  mock_app_settings.fetch_endpoint = 'http://fake-endpoint.com/fetch'
  lro_name = 'operations/op123'
  expected_request_data = {'operationName': lro_name}
  success_response = {'done': True, 'response': {'status': 'COMPLETED'}}
  mock_send_request.return_value = success_response

  result = generation.fetch_operation(lro_name, mock_app_settings)

  assert result == success_response
  mock_send_request.assert_called_once_with(
      mock_app_settings.fetch_endpoint, expected_request_data
  )
  mock_sleep.assert_not_called()
