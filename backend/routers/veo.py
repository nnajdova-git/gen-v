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
"""Router for Veo video generation and operation status endpoints.

This module defines API endpoints for interacting with the Veo video
generation service.
"""
import logging

from components import gcs_storage
from components import vertexai_component
import fastapi
from mocks import api_mocks
from models import api_models
from models import vertexai_models
import settings


router = fastapi.APIRouter()
logger = logging.getLogger(__name__)
env_settings = settings.EnvSettings()


@router.post('/generate')
async def veo_generate_video(
    request: api_models.VeoGenerateVideoRequest,
) -> api_models.VeoGenerateVideoResponse:
  """Generates a video using Veo and returns the operation name.

  Args:
    request: The request for generating a video, which includes information
      about the prompt and the video parameters.
  Returns:
    The response from the video generation including the operation name.
  """
  logger.info('VeoGenerateRequest: %s', request)
  if env_settings.use_mocks:
    logger.warning('Returning mock VeoGenerateVideoResponse')
    return api_mocks.mock_veo_generate_video_response()

  google_cloud_storage_uri = (
      f'gs://{env_settings.google_cloud_storage_bucket_name}'
  )
  vertexai_request = vertexai_models.VertexAIGenerateVideoRequest(
      prompt=request.prompt,
      google_cloud_project_id=env_settings.vertexai_google_cloud_project_id,
      google_cloud_storage_uri=google_cloud_storage_uri,
      google_cloud_region=env_settings.vertexai_google_cloud_region,
      veo_model_id=env_settings.vertexai_veo_model,
      image=request.image,
  )
  vertexai_response = vertexai_component.generate_video(vertexai_request)
  return api_models.VeoGenerateVideoResponse(
      operation_name=vertexai_response.operation_name
  )


@router.post('/operation/status')
async def veo_operation_status(
    request: api_models.VeoGetOperationStatusRequest,
) -> api_models.VeoGetOperationStatusResponse:
  """Checks the status of a video generation operation.

  When you generate a video using Veo, it happens asynchronously, and the
  operation name is returned. This endpoint checks the status of the operation,
  and if it is done, returns links to the generated videos.

  Args:
    request: The request for checking the status of a video generation
      operation, which includes the operation name.

  Returns:
    The response from the operation status check, which includes the operation
    name, whether the operation is done, and if it is done, the generated
    videos.
  """
  logger.info('VeoGetOperationStatusRequest: %s', request)
  if env_settings.use_mocks:
    logger.warning('Returning mock VeoGetOperationStatusResponse')
    return api_mocks.mock_veo_operation_status_response(request)

  vertexai_request = vertexai_models.VertexAIFetchVeoOperationStatusRequest(
      operation_name=request.operation_name,
      google_cloud_project_id=env_settings.vertexai_google_cloud_project_id,
      google_cloud_region=env_settings.vertexai_google_cloud_region,
      veo_model_id=env_settings.vertexai_veo_model,
  )

  vertexai_response = vertexai_component.fetch_operation_status(
      vertexai_request
  )
  videos = []
  if vertexai_response.done and vertexai_response.response:
    for sample in vertexai_response.response.generated_samples:
      bucket_name, object_name = gcs_storage.parse_gcs_uri(sample.video.uri)
      signed_uri = gcs_storage.get_signed_url_from_gcs(bucket_name, object_name)
      videos.append(
          api_models.Video(
              uri=sample.video.uri,
              encoding=sample.video.encoding,
              signed_uri=signed_uri,
          )
      )
  return api_models.VeoGetOperationStatusResponse(
      name=vertexai_response.name, done=vertexai_response.done, videos=videos
  )
