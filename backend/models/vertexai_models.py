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
"""The model definitions for working with Vertex AI."""

import enum
import re

import pydantic


class VeoAIModel(str, enum.Enum):
  """Enum of the various Veo AI models."""

  VEO_2_0_GENERATE_EXP = 'veo-2.0-generate-exp'
  VEO_1_PREVIEW_0815 = 'veo-001-preview-0815'


class VertexAIGenerateVideoRequest(pydantic.BaseModel):
  """The information needed to generate a video using Vertex AI.

  Attributes:
    prompt: The prompt to provide to Veo.
    google_cloud_project_id: The Google Cloud project ID to use with Vertex AI.
    google_cloud_storage_uri: The Google Cloud Storage URI to use for the
      request. This URI must start with 'gs://', and should be a path to a
      directory, where you'd like to output the videos to.
    google_cloud_region: The Google Cloud region to use.
    veo_model_id: The Veo AI model to use.
    sample_count: The number of samples to generate. This should be between 1
      and 4.
    image: A base64-encoded image to use in the generated video.
  """

  prompt: str
  google_cloud_project_id: str
  google_cloud_storage_uri: str
  google_cloud_region: str = 'us-central1'
  veo_model_id: VeoAIModel = VeoAIModel.VEO_2_0_GENERATE_EXP
  sample_count: int = 4
  image: str | None = None

  @pydantic.field_validator('google_cloud_storage_uri')
  @classmethod
  def validate_storage_uri(cls, google_cloud_storage_uri: str):
    """Validates that the google_cloud_storage_uri starts with 'gs://'."""
    if not google_cloud_storage_uri.startswith('gs://'):
      raise ValueError('google_cloud_storage_uri must start with "gs://"')
    return google_cloud_storage_uri

  @pydantic.field_validator('sample_count')
  @classmethod
  def validate_sample_count(cls, sample_count: int):
    """Validates that sample_count is between 1 and 4 (inclusive)."""
    if not 1 <= sample_count <= 4:
      raise ValueError('sample_count must be between 1 and 4')
    return sample_count

  def get_image_mime_type(self) -> str | None:
    """Detects the MIME type of the base64 encoded image.

    Returns:
      The MIME type of the image (e.g. "image/jpeg", "image/png"), or None if
      unknown.
    """
    if self.image is None:
      return None

    match = re.match(r'^data:(?P<mime_type>[\w/\-\.]+);base64', self.image)
    if match:
      return match.group('mime_type')
    return None


class VertexAIGenerateVideoResponse(pydantic.BaseModel):
  """Represents a response from the Veo video generation API.

  Attributes:
    operation_name: The name of the operation used to track the video generation
      process.
  """

  operation_name: str


class VertexAIVideo(pydantic.BaseModel):
  """A single video in Vertex AI.

  Attributes:
    uri: The URI of the video.
    encoding: The encoding of the video.
  """

  uri: str
  encoding: str


class VertexAIVideoSample(pydantic.BaseModel):
  """A single video sample in Vertex AI.

  Attributes:
    video: The video sample.
  """

  video: VertexAIVideo


class VertexAIGeneratedSamples(pydantic.BaseModel):
  """A list of generated video samples from Vertex AI.

  Attributes:
    samples: The list of generated video samples.
  """

  generated_samples: list[VertexAIVideoSample]


class VertexAIFetchVeoOperationStatusRequest(pydantic.BaseModel):
  """A request to check the status of a Veo operation.

  Attributes:
    operation_name: The name of the operation to get the status of.
    google_cloud_project_id: The Google Cloud project ID to use with Vertex AI.
    google_cloud_region: The Google Cloud region to use.
    veo_model_id: The Veo AI model to use.
  """

  operation_name: str
  google_cloud_project_id: str
  google_cloud_region: str = 'us-central1'
  veo_model_id: VeoAIModel = VeoAIModel.VEO_2_0_GENERATE_EXP


class VertexAIFetchVeoOperationStatusResponse(pydantic.BaseModel):
  """A response from checking the status of a Veo operation.

  Attributes:
    name: The name of the operation.
    done: Whether the operation is done.
    response: The response from the operation, if it is done.
  """

  name: str
  done: bool = False
  response: VertexAIGeneratedSamples | None = None
