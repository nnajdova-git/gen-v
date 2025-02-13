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
"""The model definitions for the backend API."""
import enum
import os
import constants
import fastapi
import pydantic


class VeoGenerateVideoRequest(pydantic.BaseModel):
  """Represents a request to the Veo video generation API.

  Attributes:
    prompt: The prompt to provide to Veo.
    image: A base64-encoded image to use in the generated video.
  """

  prompt: str
  image: str | None = None


class VeoGenerateVideoResponse(pydantic.BaseModel):
  """Represents a response from the Veo video generation API.

  Attributes:
    operation_name: The name of the operation used to track the video generation
      process.
  """

  operation_name: str


class Video(pydantic.BaseModel):
  """Represents a video generated by Veo.

  Attributes:
    uri: The URI of the video on Google Cloud Storage.
    encoding: The encoding of the video.
    signed_uri: The signed URL for accessing the video.
  """

  uri: str
  encoding: str
  signed_uri: str | None = None


class VeoGetOperationStatusRequest(pydantic.BaseModel):
  """Represents a request to the Veo operation status API.

  Attributes:
    operation_name: The name of the operation to get the status of.
  """

  operation_name: str


class VeoGetOperationStatusResponse(pydantic.BaseModel):
  """Represents a response from the Veo operation status API.

  Attributes:
    name: The name of the operation.
    done: Whether the operation is done.
    videos: The list of videos, if the operation is done.
  """

  name: str
  done: bool
  videos: list[Video] | None = None


class ImageSource(str, enum.Enum):
  """Enum for the types of image that can be uploaded."""

  BRAND = 'Brand'
  IMAGEN = 'Imagen'


class UploadImageRequest(pydantic.BaseModel):
  """Represents a request to the upload image asset API.

  Attributes:
      image: The image file to be uploaded.
      source: The source of the image.
      session_id: If this belongs to a session, provide the session ID,
          else if None it will be a global asset.
      image_name: Optional user-provided name for the image.
      context: Optional context description for the image.
  """

  image: fastapi.UploadFile
  source: ImageSource
  session_id: str | None = None
  image_name: str | None = None
  context: str | None = None

  @classmethod
  @pydantic.field_validator('image')
  def validate_image_type(cls, value):
    _, extension = os.path.splitext(value.filename)
    if extension.lower() not in constants.ALLOWED_IMAGE_EXTENSIONS:
      raise ValueError('Invalid image type')
    return value


class UploadImageResponse(pydantic.BaseModel):
  """Represents the response from the image upload asset API.

  Attributes:
    image_id: The unique ID of the uploaded image.
    message: A success message.
    location: The URL to access the uploaded image.
  """

  image_id: str
  message: str
  location: str
