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

"""Tests for storage module."""


from unittest import mock
from gen_v import storage as gcs
from google.cloud import storage
import pytest


@pytest.fixture(name='fake_fs')
def fake_filesystem(fs):
  yield fs


@pytest.fixture(name='mock_blob')
def fixture_mock_blob(fs):
  mock_blob = mock.MagicMock(spec=storage.Blob)
  mock_blob.file = 'original_video.mp4'
  mock_blob.contents = 'The original contents'

  def upload_from_filename(filename: str, client: storage.Client):  # pylint: disable=unused-argument
    mock_blob.file = filename
    with open(filename, 'r', encoding='UTF-8') as f:
      mock_blob.contents = f.read()

  mock_blob.upload_from_filename = upload_from_filename

  def download_to_filename(filename: str):
    fs.create_file(filename)
    with open(filename, 'w', encoding='UTF-8') as f:
      f.write(mock_blob.contents)

  mock_blob.download_to_filename = download_to_filename

  mock_blob.generate_signed_url.return_value = (
      'https://signed_url/test_file.mp4'
  )
  mock_blob.open.return_value.__enter__.return_value.read.return_value = (
      b'This is a test file content.'
  )
  yield mock_blob


@pytest.fixture(name='mock_bucket')
def fixture_mock_bucket(mock_blob):
  mock_bucket = mock.MagicMock(spec=storage.Bucket)
  mock_bucket.blob.return_value = mock_blob

  yield mock_bucket


@pytest.fixture(name='mock_storage_client')
def fixture_storage_client(mock_bucket):
  mock_storage_client = mock.MagicMock(spec=storage.Client)
  mock_storage_client.bucket.return_value = mock_bucket
  yield mock_storage_client


@pytest.fixture(name='mock_exists')
def fixture_mock_storage():
  with mock.patch.object(storage.Blob, 'exists', autospec=True) as mock_exists:
    yield mock_exists


def test_get_file_name_from_gcs_url():
  test_filename = 'gcs://hello/world/video.mp4'
  expected_file = 'video.mp4'
  res = gcs.get_file_name_from_gcs_url(test_filename)
  assert res == expected_file


def test_upload_file_to_gcs(mock_storage_client, fake_fs):
  file_path = '/var/data/test_file.mp4'
  file_content = 'This is the content to write.'
  fake_fs.create_file(file_path)
  with open(file_path, 'w', encoding='UTF-8') as f:
    f.write(file_content)

  gcs.upload_file_to_gcs(file_path, 'test_bucket', mock_storage_client)
  assert mock_storage_client.bucket().blob().contents == file_content
  assert mock_storage_client.bucket().blob().file == file_path


def test_download_file_locally(mock_storage_client):
  file_content = 'The original contents'
  file_path = '/content/test_file.mp4'
  ret_file_path = gcs.download_file_locally(
      uri='uri', file_name='test_file.mp4', storage_client=mock_storage_client
  )

  assert ret_file_path == file_path

  ret_file_contents = None
  with open(file=file_path, mode='r', encoding='UTF-8') as f:
    ret_file_contents = f.read()

  assert ret_file_contents == file_content


def test_create_gcs_folders_in_subfolder_with_one_folder(
    mock_storage_client, mock_bucket, mock_blob, caplog
):
  bucket_name = 'my-test-bucket'
  subfolder_name = 'my-subfolder'
  folder_names = ['new-folder1']
  mock_blob.exists.return_value = False

  gcs.create_gcs_folders_in_subfolder(
      bucket_name, subfolder_name, folder_names, mock_storage_client
  )

  mock_storage_client.bucket.assert_called_once_with(bucket_name)
  mock_bucket.blob.assert_called_once_with(
      f'{subfolder_name}/{folder_names[0]}/'
  )
  mock_blob.exists.assert_called_once()
  mock_blob.upload_from_string.assert_called_once_with('')

  assert 'Folder created: new-folder1' in caplog.text


# @pytest.mark.parametrize('exists', [True, False])
# def test_check_file_exists_failure(mock_exists, mock_storage_client, exists):
#   mock_exists.return_value = exists
#   if not exists:
#     with pytest.raises(FileNotFoundError) as excinfo:
#       gcs.check_file_exists(
#           'nonexistent_file.mp4', 'test_bucket', mock_storage_client
#       )
#     assert (
#         str(excinfo.value)
#         == 'File not found: nonexistent_file.mp4 at bucket test_bucket'
#     )
#   else:
#     assert gcs.check_file_exists(
#         'existing_file.mp4', 'test_bucket', mock_storage_client
#     )
