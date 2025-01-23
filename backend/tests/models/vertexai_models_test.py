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
"""Unit tests for vertexai_models.py."""

from models import vertexai_models
import pydantic
import pytest


def test_vertexai_generate_video_request_with_simple_valid_inputs():
  request = vertexai_models.VertexAIGenerateVideoRequest(
      prompt='A cat playing the piano',
      google_cloud_project_id='my-project',
      google_cloud_storage_uri='gs://my-bucket/my-folder',
  )
  assert request.prompt == 'A cat playing the piano'
  assert request.google_cloud_project_id == 'my-project'
  assert request.google_cloud_storage_uri == 'gs://my-bucket/my-folder'


def test_vertexai_generate_video_request_with_invalid_storage_uri():
  with pytest.raises(pydantic.ValidationError):
    vertexai_models.VertexAIGenerateVideoRequest(
        prompt='A cat playing the piano',
        google_cloud_project_id='my-project',
        google_cloud_storage_uri='https://my-bucket/my-folder',
    )


def test_vertexai_generate_video_request_with_invalid_sample_counts():
  with pytest.raises(pydantic.ValidationError):
    vertexai_models.VertexAIGenerateVideoRequest(
        prompt='A cat playing the piano',
        google_cloud_project_id='my-project',
        google_cloud_storage_uri='gs://my-bucket/my-folder',
        sample_count=0
    )
  with pytest.raises(pydantic.ValidationError):
    vertexai_models.VertexAIGenerateVideoRequest(
        prompt='A cat playing the piano',
        google_cloud_project_id='my-project',
        google_cloud_storage_uri='gs://my-bucket/my-folder',
        sample_count=5
    )


def test_vertexai_generate_video_request_get_image_mime_type_valid():
  request = vertexai_models.VertexAIGenerateVideoRequest(
      prompt='A cat playing the piano',
      google_cloud_project_id='my-project',
      google_cloud_storage_uri='gs://my-bucket/my-folder',
      image='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
  )
  assert request.get_image_mime_type() == 'image/png'


def test_vertexai_generate_video_request_get_image_mime_type_invalid():
  request = vertexai_models.VertexAIGenerateVideoRequest(
      prompt='A cat playing the piano',
      google_cloud_project_id='my-project',
      google_cloud_storage_uri='gs://my-bucket/my-folder',
      image='invalid-b64'
  )
  assert request.get_image_mime_type() is None
