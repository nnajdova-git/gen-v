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
"""A component to work with Vertex AI in Google Cloud."""
import google.auth
from google.auth.transport import requests as google_requests
from models import vertexai_models
import requests


_VERTEX_AI_ENDPOINT = 'https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/{model_id}:predictLongRunning'


def get_access_token() -> str:
  """Retrieves the access token for the currently active account."""
  creds, _ = google.auth.default()
  if not creds.valid:
    creds.refresh(google_requests.Request())
  return creds.token


def generate_video(
    request: vertexai_models.VertexAIGenerateVideoRequest,
    access_token: str = None,
) -> vertexai_models.VertexAIGenerateVideoResponse:
  """Generates a video using Veo.

  Args:
    request: The request object containing the parameters for the video
      generation.
    access_token: The access token to use for authentication. If not provided,
      the default credentials will be used. This is primarily used for
      dependency injection in testing.

  Returns:
    The response object containing the operation name.

  Raises:
    requests.exceptions.HTTPError: If the API request fails (non-2xx status
    code).
  """
  if access_token is None:
    access_token = get_access_token()

  url = _VERTEX_AI_ENDPOINT.format(
      region=request.google_cloud_region,
      project_id=request.google_cloud_project_id,
      model_id=request.veo_model_id.value,
  )
  payload = {
      'instances': [{
          'prompt': request.prompt,
      }],
      'parameters': {
          'storageUri': request.google_cloud_storage_uri,
          'sampleCount': request.sample_count,
      },
  }
  if request.image:
    mime_type = request.get_image_mime_type()
    if mime_type is None:
      raise ValueError('Mime type cannot be determined from the image.')
    payload['instances'][0]['image'] = {
        'bytesBase64Encoded': request.image,
        'mimeType': mime_type,
    }

  headers = {
      'Authorization': f'Bearer: {access_token}',
      'Content-Type': 'application/json; charset=utf-8',
  }
  response = requests.post(url, json=payload, headers=headers)
  response.raise_for_status()
  return vertexai_models.VertexAIGenerateVideoResponse(
      operation_name=response.json()['name'],
  )
