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

"""Functions to handle storage operations."""
import datetime
from google.cloud import storage


def check_file_exists(
    file_name: str,
    bucket_name: str,
    storage_client: storage.Client | None = None,
) -> None:
  """Checks if a file exists at the given bucket.

  Args:
    file_name: The name of the file to check.
    bucket_name: The name of the bucket containing the file.
    storage_client: The Google Cloud Storage client.

  Returns:
    True if the file exists, False otherwise.

  Raises:
    FileNotFoundError: If the file does not exist.
  """
  storage_client = storage_client or storage.Client()
  bucket = storage_client.bucket(bucket_name)
  exists = storage.Blob(bucket=bucket, name=file_name).exists(storage_client)
  if not exists:
    raise FileNotFoundError(
        f'File not found: {file_name} at bucket {bucket_name}'
    )
  return exists


def get_signed_url_from_gcs(
    bucket_name: str,
    file_name: str,
    storage_client: storage.Client | None = None,
) -> str:
  """Gets the signed URL to a file in Google Cloud Storage.

  Args:
    bucket_name: The name of the bucket containing the file.
    file_name: The name of the file.
    storage_client: The Google Cloud Storage client.

  Returns:
    The signed URL to the file.
  """
  storage_client = storage_client or storage.Client()
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(file_name)
  file_path = blob.generate_signed_url(
      datetime.timedelta(hours=1), method='GET'
  )
  return file_path


def read_from_gcs(
    bucket_name: str,
    file_name: str,
    storage_client: storage.Client | None = None,
) -> bytes:
  """Reads a file from Google Cloud Storage.

  Args:
    bucket_name: The name of the bucket containing the file.
    file_name: The name of the file.
    storage_client: The Google Cloud Storage client.

  Returns:
    The content of the file.
  """
  storage_client = storage_client or storage.Client()
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(file_name)
  with blob.open('r') as f:
    file_content = f.read()
  return file_content


def write_to_gcs(
    file_content,
    bucket_name: str,
    file_name: str,
    storage_client: storage.Client | None = None,
) -> None:
  """Writes a file to Google Cloud Storage.

  Args:
    file_content: The content of the file.
    bucket_name: The name of the bucket containing the file.
    file_name: The name of the file.
    storage_client: The Google Cloud Storage client.
  """
  storage_client = storage_client or storage.Client()
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(file_name)
  # Mode can be specified as wb/rb for bytes mode.
  # See: https://docs.python.org/3/library/io.html
  with blob.open('w') as f:
    f.write(file_content)
