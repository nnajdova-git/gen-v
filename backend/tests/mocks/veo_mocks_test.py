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
"""Unit tests for veo_mocks.py."""

from mocks import veo_mocks
from models import veo_models
import pytest


@pytest.fixture(name='operation_status_request')
def operation_status_request_fixture():
  return veo_models.VeoGetOperationStatusRequest(
      operation_name='projects/PROJECT_ID/operations/TEST_OPERATION_ID'
  )


def test_mock_veo_generate_video_response():
  response = veo_mocks.mock_veo_generate_video_response()
  assert (
      response.operation_name == 'projects/PROJECT_ID/operations/OPERATION_ID'
  )


def test_default_mock_veo_operation_status_response(operation_status_request):
  response = veo_mocks.mock_veo_operation_status_response(
      operation_status_request
  )

  assert response.name == operation_status_request.operation_name
  assert response.done
  assert len(response.response.generated_samples) == 4
  assert response.response.generated_samples[0].video.uri.startswith('gs://')


def test_mock_veo_operation_status_response_custom_videos(
    operation_status_request,
):
  num_videos = 2
  response = veo_mocks.mock_veo_operation_status_response(
      operation_status_request, num_of_videos=num_videos
  )

  assert len(response.response.generated_samples) == num_videos
  assert response.response.generated_samples[0].video.uri.startswith('gs://')


def test_mock_veo_operation_status_response_custom_bucket_name(
    operation_status_request,
):
  custom_bucket_name = 'my-custom-bucket'
  response = veo_mocks.mock_veo_operation_status_response(
      operation_status_request, gcs_bucket_name=custom_bucket_name
  )

  assert response.response.generated_samples[0].video.uri.startswith(
      f'gs://{custom_bucket_name}/'
  )
  assert custom_bucket_name in response.response.generated_samples[0].video.uri
