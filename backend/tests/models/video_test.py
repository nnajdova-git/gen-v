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
"""Unit tests for the video models."""
import pytest
from gen_v.models import video


def test_gemini_request_with_image(png_file_in_fs):
  """Tests model initialisation loads data when an image path is provided."""
  prompt = 'Describe this image'
  image_path_str = png_file_in_fs

  model = video.GeminiPromptRequest(
      prompt_text=prompt, image_file_path=image_path_str
  )

  assert model.prompt_text == prompt
  assert model.image_file_path == image_path_str
  assert model.image_bytes is not None
  assert isinstance(model.image_bytes, bytes)
  assert model.mime_type == 'image/png'


def test_gemini_request_without_image():
  """Tests model initialisation works correctly when no image path is given."""
  prompt = 'Just a text prompt'
  model = video.GeminiPromptRequest(prompt_text=prompt, image_file_path=None)

  assert model.prompt_text == prompt
  assert model.image_file_path is None
  assert model.mime_type is None
  assert model.image_bytes is None


def test_gemini_request_nonexistent_image_path(tmp_path):
  """Tests model initialisation fails if the image path does not exist."""
  non_existent_path = str(tmp_path / 'non_existent.png')
  prompt = 'This should fail'

  with pytest.raises(ValueError, match='Image file not found'):
    video.GeminiPromptRequest(
        prompt_text=prompt, image_file_path=non_existent_path
    )
