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
"""This file defines the environment settings used in the application.

To override the default settings, simply set environment variables accordingly,
and they will be automatically picked up by the application.
"""
import pydantic_settings


class EnvSettings(pydantic_settings.BaseSettings):
  """The environment settings used in the application.

  Attributes:
    host: The host to run the application on.
    port: The port to run the application on.
    allowed_origin: The origin to allow CORS requests from.
    use_mocks: If set to "True", mock responses will be returned from the API.
    vertexai_google_cloud_project_id: The Google Cloud project ID to use for
      requests to Vertex AI.
    vertexai_google_cloud_region: The region to use with Vertex AI.
  """

  host: str = '0.0.0.0'
  port: int = 8080
  allowed_origin: str = '*'
  use_mocks: bool = False
  vertexai_google_cloud_project_id: str = 'my-gcp-project'
  vertexai_google_cloud_region: str = 'us-central1'
