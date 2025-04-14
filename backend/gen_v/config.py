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
"""Configuration settings for the video generation backend.

This module defines the application settings using Pydantic, loading values
from environment variables or using sensible defaults. It centralizes
configuration related to Google Cloud Platform resources, storage paths,
and temporary directories.
"""
import pydantic
import pydantic_settings


class AppSettings(pydantic_settings.BaseSettings):
  """The settings used in the application.

  Attributes:
    gcp_project_id: Google Cloud Project ID.
    gcp_bucket_name: Google Cloud Storage bucket name.
    gcs_folder_name: Base folder name within the GCS bucket.
    gcp_region: The Google Cloud region to use.
    veo_model_name: The name of the Veo model to use.
  """

  gcp_project_id: str
  gcp_bucket_name: str
  gcs_folder_name: str
  gcp_region: str = "us-central1"
  veo_model_name: str = "veo-2.0-generate-001"

  @pydantic.computed_field(return_type=str)
  @property
  def input_images_bucket_path(self) -> str:
    """Relative path within the bucket for input images."""
    return f"{self.gcs_folder_name}/input-images/"

  @pydantic.computed_field(return_type=str)
  @property
  def video_model_uri(self) -> str:
    return (
        f"https://{self.gcp_region}-aiplatform.googleapis.com/v1beta1/"
        f"projects/{self.gcp_project_id}/locations/{self.gcp_region}/"
        f"publishers/google/models/{self.veo_model_name}"
    )

  @pydantic.computed_field(return_type=str)
  @property
  def prediction_endpoint(self) -> str:
    return f"{self.video_model_uri}:predictLongRunning"

  @pydantic.computed_field(return_type=str)
  @property
  def fetch_endpoint(self) -> str:
    return f"{self.video_model_uri}:fetchPredictOperation"
