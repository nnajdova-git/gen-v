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
"""Defines mock responses for testing from the backend API.

This module is used to mock responses from the APIs. This is useful for
development and testing when you don't want to make actual calls to the Google
Cloud endpoint like Veo.
"""

from models import api_models


def mock_veo_generate_video_response() -> api_models.VeoGenerateVideoResponse:
  """Returns a mock VeoGenerateVideoResponse for testing.

  Returns:
    A mock VeoGenerateVideoResponse.
  """
  operation_name = 'projects/PROJECT_ID/operations/OPERATION_ID'
  return api_models.VeoGenerateVideoResponse(operation_name=operation_name)


def mock_veo_operation_status_response(
    request: api_models.VeoGetOperationStatusRequest,
    gcs_bucket_name: str = 'mock-storage-bucket-name',
    num_of_videos: int = 4,
) -> api_models.VeoGetOperationStatusResponse:
  """Returns a mock VeoGetOperationStatusResponse for testing.

  Args:
    request: The request object.
    gcs_bucket_name: If you wish to use a real Google Cloud Storage bucket, you
      can pass the name of the bucket here.
    num_of_videos: How many videos should be returned in the response.

  Returns:
    A mock VeoGetOperationStatusResponse.
  """
  generated_video_samples = []
  for i in range(num_of_videos):
    mock_video = api_models.Video(
        uri=f'gs://{gcs_bucket_name}/veo/generated/sample_{i}.mp4',
        encoding='video/mp4'
    )
    generated_video_samples.append(api_models.VideoSample(video=mock_video))

  return api_models.VeoGetOperationStatusResponse(
      name=request.operation_name,
      done=True,
      response=api_models.GeneratedSamples(
          generated_samples=generated_video_samples
      ),
  )
