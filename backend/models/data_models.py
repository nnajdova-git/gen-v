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
"""Data models for the application.

This module defines Pydantic models used to represent data entities within the
application. These models are database-agnostic and can be used with various
data storage solutions.

The module includes a base `DataModel` class that serves as a foundation for all
other data models, promoting consistency and providing a central place for
common fields or methods.

These models are used for data validation, serialization, and type hinting
throughout, the application.  They help ensure data integrity and improve code
maintainability.
"""
import datetime
import pydantic


class DataModel(pydantic.BaseModel):
  """Base class for all data models."""

  pass


class Image(DataModel):
  """Represents an image document stored in Firestore.

  Attributes:
    bucket_name: The name of the Google Cloud Storage bucket where the image is
      stored.
    file_path: The path on the bucket to the image file.
    file_name: The original filename of the uploaded image.
    original_file_name: The name of the original file.
    full_gcs_path: The full Google Cloud Storage path to the image, e.g.
      "gs://path/to/image/my-image.png".
    source: The source of the image (e.g., "Brand", "Imagen").  Stored as
        the string value of the ImageSource enum.
    image_name: Optional user-provided name for the image.
    context: Optional context description for the image.
    date_created: The datetime that this was created.
  """

  bucket_name: str
  file_path: str
  file_name: str
  original_file_name: str
  full_gcs_path: str
  source: str
  image_name: str | None = None
  context: str | None = None
  date_created: datetime.datetime = pydantic.Field(
      default_factory=datetime.datetime.now
  )
