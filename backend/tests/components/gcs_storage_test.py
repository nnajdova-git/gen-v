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

import datetime
from unittest import mock

from components import gcs_storage
from google.cloud import storage
import pytest


@pytest.fixture(name='mock_blob')
def fixture_mock_blob():
  mock_blob = mock.MagicMock(spec=storage.Blob)
  mock_blob.generate_signed_url.return_value = (
      'https://signed_url/test_file.mp4'
  )
  mock_blob.open.return_value.__enter__.return_value.read.return_value = (
      b'This is a test file content.'
  )
  yield mock_blob


@pytest.fixture(name='mock_storage_client')
def fixture_storage_client(mock_blob):
  mock_storage_client = mock.MagicMock(spec=storage.Client)
  mock_bucket = mock.MagicMock(spec=storage.Bucket)
  mock_bucket.blob.return_value = mock_blob
  mock_storage_client.bucket.return_value = mock_bucket
  yield mock_storage_client


@pytest.fixture(name='mock_exists')
def fixture_mock_storage():
  with mock.patch.object(storage.Blob, 'exists', autospec=True) as mock_exists:
    yield mock_exists


@pytest.mark.parametrize('exists', [True, False])
def test_check_file_exists_failure(mock_exists, mock_storage_client, exists):
  mock_exists.return_value = exists
  if not exists:
    with pytest.raises(FileNotFoundError) as excinfo:
      gcs_storage.check_file_exists(
          'nonexistent_file.mp4', 'test_bucket', mock_storage_client
      )
    assert (
        str(excinfo.value)
        == 'File not found: nonexistent_file.mp4 at bucket test_bucket'
    )
  else:
    assert gcs_storage.check_file_exists(
        'existing_file.mp4', 'test_bucket', mock_storage_client
    )


def test_get_signed_url_from_gcs(mock_storage_client, mock_blob):
  file_name = 'test_file.mp4'
  expected_url = 'https://signed_url/test_file.mp4'

  file_path = gcs_storage.get_signed_url_from_gcs(
      'test_bucket', file_name, mock_storage_client
  )

  assert file_path == expected_url
  mock_blob.generate_signed_url.assert_called_once_with(
      datetime.timedelta(hours=1), method='GET'
  )


def test_read_from_gcs(mock_storage_client):
  file_content = b'This is a test file content.'
  returned_file_content = gcs_storage.read_from_gcs(
      'test_bucket', 'test_file.mp4', mock_storage_client
  )

  assert returned_file_content == file_content


def test_write_to_gcs(mock_storage_client):
  file_content = 'This is the content to write.'
  gcs_storage.write_to_gcs(
      file_content, 'test_bucket', 'test_file.mp4', mock_storage_client
  )
  mock_storage_client.bucket().blob().open.assert_called_once_with('w')
  # pylint: disable=line-too-long
  mock_storage_client.bucket().blob().open.return_value.__enter__.return_value.write.assert_called_once_with(
      file_content
  )
