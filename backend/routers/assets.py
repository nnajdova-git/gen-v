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
import sys

from components import asset_utils
from components import firestore_crud
import constants
import fastapi
from mocks import asset_mocks
from models import api_models
from models import asset_models
from models import data_models
import settings


router = fastapi.APIRouter()
logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
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


@router.get('/images/{image_id}')
async def get_image_by_id(image_id: str) -> api_models.ImageMetadataResponse:
  """Fetch image with the specified image_id.

  Args:
    image_id: The ID of the image, which is the name of the Firestore document.

  Returns:
    The image metadata with signed URL.
    Raises 404 HTTPException if image is not found.
  """
  image_metadata = asset_utils.get_image_metadata_with_signed_url(
      image_id=image_id
  )
  if not image_metadata:
    raise fastapi.HTTPException(status_code=404, detail='Image not found')

  return api_models.ImageMetadataResponse(
      source=image_metadata.source,
      image_name=image_metadata.image_name,
      context=image_metadata.context,
      date_created=image_metadata.date_created,
      signed_url=image_metadata.signed_url,
  )


@router.get('/images/type/{image_type}')
async def get_images_by_type(
    image_type: str,
) -> list[api_models.ImageMetadataResponse]:
  """Fetches images of a specific source type (e.g., 'Brand').

  Args:
    image_type: The source type of the images to fetch (e.g., "Brand").

  Returns:
    A list of ImageMetadataResponse objects, each containing image metadata
    and a signed URL. Returns an empty list if no images are found.
  """
  if env_settings.use_mocks:
    logger.warning('Returning mock responses.')
    mocked_image = asset_mocks.mock_get_image_metadata_with_signed_url(
        'mock_id'
    )
    return [
        api_models.ImageMetadataResponse(
            source=mocked_image.source,
            image_name=mocked_image.image_name,
            context=mocked_image.context,
            date_created=mocked_image.date_created,
            signed_url=mocked_image.signed_url,
        )
    ]

  image_docs = firestore_crud.query_collection(
      collection_name=constants.FirestoreCollections.IMAGES,
      model_type=data_models.Image,
      query_field='source',
      query_operator='==',
      query_value=image_type,
      database_name=env_settings.firestore_db_name,
  )

  if not image_docs:
    logger.info('No images found with source type: %s', image_type)
    return []

  logger.info('Fetched %d images from Firestore.', len(image_docs))
  response_list = []
  for image_doc in image_docs:
    image_metadata = asset_models.ImageMetadataResult(**image_doc.model_dump())
    image_metadata.generate_signed_url()
    response_list.append(
        api_models.ImageMetadataResponse(
            source=image_metadata.source,
            image_name=image_metadata.image_name,
            context=image_metadata.context,
            date_created=image_metadata.date_created,
            signed_url=image_metadata.signed_url,
        )
    )
  return response_list
