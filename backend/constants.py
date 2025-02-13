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
"""Defines constants used throughout the project."""


class FirestoreCollections:
  """Constants for Firestore collection names.

  Attributes:
    SESSIONS: The name of the Firestore collection for storing session data.
    VIDEOS: The name of the Firestore collection for storing video data.
    IMAGES: The name of the Firestore collection for storing image data.
    AUDIO: The name of the Firestore collection for storing audio data.
  """

  SESSIONS = 'sessions'
  VIDEOS = 'videos'
  IMAGES = 'images'
  AUDIO = 'audio'


class StoragePaths:
  """Constants for Google Cloud Storage paths (relative to the bucket).

  Attributes:
    IMAGES: The base path for all image-related storage.
    VIDEOS: The base path for all video-related storage.
    AUDIO: The base path for all audio-related storage.
  """

  IMAGES = 'images'
  VIDEOS = 'videos'
  AUDIO = 'audio'


# A set of allowed image file extensions (lowercase).
ALLOWED_IMAGE_EXTENSIONS: set[str] = {
    '.png',
    '.jpg',
    '.jpeg',
    '.gif',
    '.bmp',
    '.tif',
    '.tiff',
}
