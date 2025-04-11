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
import pytest
import requests
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
