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
"""Unit tests for video editing."""
from unittest import mock
from PIL import Image
from gen_v import video


@mock.patch('gen_v.video.editing.Image.open')
def test_display_image_calls_provided_function_correctly(
    mock_image_open, png_file_in_fs
):
  """Tests display_image calls the provided func with correct args."""
  test_height = 250
  mock_pil_image = mock.MagicMock(spec=Image)
  mock_image_open.return_value = mock_pil_image
  mock_custom_display_func = mock.MagicMock()

  video.display_image(
      png_file_in_fs,
      display_function=mock_custom_display_func,
      height=test_height,
  )

  mock_image_open.assert_called_once_with(png_file_in_fs)
  mock_custom_display_func.assert_called_once_with(
      mock_pil_image, height=test_height
  )
