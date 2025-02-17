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

"""Media input classes for the video editing module."""

import pydantic


class ImageInput(pydantic.BaseModel):
  """Represents an image clip to be overlaid on a video.

  Attributes:
    path: Path to the image file.
    position: Position of the image on the video.
    duration: Duration of the image overlay in seconds.
    height: Height of the image in pixels.
  """

  path: str
  position: tuple[str | int, str | int] = ('right', 'top')
  duration: float | None = None
  height: int | None = None


class VideoInput(pydantic.BaseModel):
  """Represents a video clip.

  Attributes:
    path: Path to the video file.
  """

  path: str


class AudioInput(pydantic.BaseModel):
  """Represents an audio clip.

  Attributes:
    path: Path to the audio file.
    start_time: Start time of the audio clip in seconds.
    duration: Duration of the audio clip in seconds.
  """

  path: str
  start_time: float = 0.0
  duration: float | None = None

