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
"""Functions for generating video content using Google Cloud AI APIs.

This module handles interactions with services like Vertex AI Gemini for prompt
generation and the Video Generation API for creating video clips from images and
prompts.
"""
import logging
import sys

from google import genai
import google.auth
from google.auth.transport import requests as google_requests
from google.genai import types
import requests

from gen_v import models

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_access_token() -> str:
  """Retrieves the access token for the currently active account."""
  creds, _ = google.auth.default()
  if not creds.valid:
    creds.refresh(google_requests.Request())
  return creds.token


def send_request_to_google_api(
    api_endpoint: str,
    data: dict[str, any] = None,
    access_token: str | None = None,
    timeout: int = 60,
) -> dict[str, any]:
  """Sends an HTTP request to a Google API endpoint.

  Args:
    api_endpoint: The URL of the Google API endpoint.
    data: (Optional) Dictionary of data to send in the request body.
    access_token: The access token to use for authentication. If not provided,
      the default credentials will be used. This is primarily used for
      dependency injection in testing.
    timeout: The number of seconds before giving up the request.

  Returns:
    The response from the Google API.

  Raises:
    requests.exceptions.HTTPError: If the API request fails (non-2xx status
    code).
  """
  if access_token is None:
    access_token = get_access_token()

  headers = {
      'Authorization': f'Bearer {access_token}',
      'Content-Type': 'application/json',
  }

  response = requests.post(
      api_endpoint, headers=headers, json=data, timeout=timeout
  )
  response.raise_for_status()
  return response.json()


def get_gemini_generated_video_prompt(
    request_data: models.GeminiPromptRequest,
    project_id: str = None,
    location: str = None,
    client: genai.Client | None = None,
) -> str | None:
  """Uses Gemini to analyse an image and generate a video prompt.

  Args:
    request_data: A GeminiPromptRequest object containing input file, prompt
      text, and model name.
    project_id: The project ID to use in the client.
    location: The Google Cloud location to use in the client.
    client: For dependency injection, provide a client to use. If not used, one
      will be created using the project_id and location.

  Returns:
      The generated video prompt as a string, or None if there was an error.

  Raises:
    ValueError if client is None and a project_id and location aren't provided.
  """
  if client is None:
    if not project_id or not location:
      raise ValueError(
          'project_id and location must be provided if client is None'
      )
    client = genai.Client(vertexai=True, project=project_id, location=location)

  contents = [request_data.prompt_text]
  if request_data.image_bytes and request_data.mime_type:
    contents.append(
        types.Part.from_bytes(
            data=request_data.image_bytes, mime_type=request_data.mime_type
        )
    )
  else:
    logger.warning('No image found, sending only the prompt.')

  response = client.models.generate_content(
      model=request_data.model_name,
      contents=contents,
      config=types.GenerateContentConfig(
          media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
      ),
  )
  logger.info('The response is: %s', response.text)
  return response.text
