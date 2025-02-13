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
"""Router for asset-related endpoints.

This module provides API endpoints for managing various assets.
"""

import logging

from components import asset_utils
import fastapi
from models import api_models
from models import asset_models
import settings


router = fastapi.APIRouter()
logger = logging.getLogger(__name__)
env_settings = settings.EnvSettings()


async def get_upload_image_request(
    request: fastapi.Request,
) -> api_models.UploadImageRequest:
  """Dependency function to parse the form data into the model.

  Args:
    request: The request object containing the form data.

  Returns:
    The parsed UploadImageRequest model.
  """
  form_data = await request.form()
  try:
    return api_models.UploadImageRequest(**form_data)
  except Exception as e:
    raise fastapi.HTTPException(status_code=422, detail=str(e))


@router.post('/images', status_code=fastapi.status.HTTP_201_CREATED)
async def upload_image(
    request: api_models.UploadImageRequest = fastapi.Depends(
        get_upload_image_request
    ),
) -> api_models.UploadImageResponse:
  """Uploads a new image to Firestore.

  Args:
    request: The request object containing the image to upload and relevant
      metadata.

  Returns:
    The response object containing the image ID and location.
  """
  input_data = asset_models.ImageUploadInput(
      image=request.image,
      source=request.source,
      session_id=request.session_id,
      image_name=request.image_name,
      context=request.context,
  )

  image_id = asset_utils.upload_image_asset(input_data)
  return api_models.UploadImageResponse(
      image_id=image_id,
      message='Image uploaded successfully!',
      location=f'/images/{image_id}',
  )
