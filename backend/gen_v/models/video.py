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
"""Pydantic models specific to video workflows."""
import logging
import mimetypes
import os
import sys
from typing import Self
import pydantic


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GeminiPromptRequest(pydantic.BaseModel):
  """Input data for making a Gemini request.

  Attributes:
    prompt_text: The prompt to use with Gemini.
    image_file_path: If provided, the image will be read and sent to Gemini with
      the prompt.
    model_name: The name of the Gemini model to use.
    image_bytes: The raw bytes read from image_file_path. Populated
      automatically if image_file_path is provided. Defaults to None. Excluded
      from model serialization.
    mime_type: The detected MIME type of the image file. Populated automatically
      if image_file_path is provided. Defaults to None. Excluded from model
      serialization.
  """

  prompt_text: str
  image_file_path: str | None
  model_name: str = 'gemini-2.0-flash'

  image_bytes: bytes | None = pydantic.Field(None, exclude=True)
  mime_type: str | None = pydantic.Field(None, exclude=True)

  @pydantic.model_validator(mode='after')
  def load_image_data_if_path_provided(self) -> Self:
    """If image_file_path is set, load bytes and MIME type."""
    if self.image_file_path:
      try:
        logger.info(
            'Attempting to load image data from: %s', self.image_file_path
        )
        if not os.path.exists(self.image_file_path):
          raise ValueError(f'Image file not found: {self.image_file_path}')

        mime_type_guess, _ = mimetypes.guess_type(self.image_file_path)
        if mime_type_guess is None:
          self.mime_type = 'application/octet-stream'
          logger.warning(
              'Could not determine MIME type for %s. Defaulting to %s',
              self.image_file_path,
              self.mime_type,
          )
        else:
          logger.info('Determined MIME type: %s', self.mime_type)
          self.mime_type = mime_type_guess

        with open(self.image_file_path, 'rb') as f:
          self.image_bytes = f.read()
        logger.info('image_bytes attribute populated.')

      except FileNotFoundError as e:
        logger.error(
            'File not found error during model validation: %s', exc_info=True
        )
        raise ValueError(f'Image file not found: {self.image_file_path}') from e
      except Exception as e:
        logger.error(
            'Error processing image during model validation: %s',
            exc_info=True,
        )
        raise ValueError(f'Failed to process image file: {e}') from e
    else:
      self.image_bytes = None
      self.mime_type = None

    return self
