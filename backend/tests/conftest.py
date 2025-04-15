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
from unittest import mock
import pytest
from gen_v import config


@pytest.fixture(name='png_file_in_fs')
def png_file_in_fs_fixture(fs):
  """Creates a minimal dummy PNG file in the fake filesystem."""
  file_path = '/fake/dir/test_image.png'
  # Minimal valid PNG file content (1x1 transparent pixel)
  # pylint: disable=line-too-long
  png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xfc\xff?\x03\x00\x01\xff\xff\xa5\xd9\x9a\xc1\x00\x00\x00\x00IEND\xaeB`\x82'
  fs.create_file(file_path, contents=png_data)
  yield file_path


@pytest.fixture(name='mock_app_settings')
def mock_app_settings_fixture():
  """Pytest fixture providing a mocked AppSettings instance."""
  settings = mock.MagicMock(spec=config.AppSettings)
  settings.gcs_project_id = 'my-project'
  settings.gcp_bucket_name = 'my-bucket'
  settings.gcs_folder_name = 'my-folder'
  yield settings
