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

"""Pydantic classes for video editing."""

import pydantic
from typing import Self


class VideoInput(pydantic.BaseModel):
  """Represents a video clip.

  Attributes:
    path: Path to the video file.
  """

  path: str


class VideoTransition(pydantic.BaseModel):
  """Represents a video clip transition.

  Attributes:
    name: Reference to the video transition.
    padding: The padding between the video clips.
    side: Side of a transition.
    gcs_uri: GCS URI of the video transition.
  """

  name: str
  padding: float
  side: str
  gcs_uri: str | None = None


class ImageInput(pydantic.BaseModel):
  """Represents an image clip to be overlaid on a video.

  Attributes:
    path: Path to the image file.
    start: Start time of the image overlay in seconds.
    position: Position of the image on the video.
    duration: Duration of the image overlay in seconds.
    height: Height of the image in pixels.
  """

  path: str
  start: int
  position: tuple[str | int, str | int] = ('right', 'top')
  duration: float | None = None
  height: int | None = None


class TextInput(pydantic.BaseModel):
  """Represents a text clip to be overlaid on a video.

  Attributes:
    filename: Path to the text file. Can be provided instead of argument text.
    text: A string of the text to write. Can be replaced by argument filename.
    font: Path to the font to use. Must be an OpenType font. If set to None
      (default) will use Pillow default font
    font_size: Font size in point. Can be auto-set if method='caption', or if
      method='label' and size is set.
    size: Size of the picture in pixels. Can be auto-set if method='label' and
      font_size is set, but mandatory if method='caption. The height can be None
      for caption if font_size is defined, it will then be auto-determined.
    margin: Margin to be added around the text as a tuple of two (symmetrical)
      or four (asymmetrical). Either (horizontal, vertical) or (left, top,
      right, bottom). By default no margin (None, None). This is especially
      useful for auto-compute size to give the text some extra room.
    color: Color of the text. Default to 'black'. Can be a RGB (or RGBA if
      transparent = True) tuple, a color name, or an hexadecimal notation.
    bg_color: Color of the background. Default to None for no background. Can be
      a RGB (or RGBA if transparent = True) tuple, a color name, or an
      hexadecimal notation.
    stroke_color: Color of the stroke (=contour line) of the text. If None,
      there will be no stroke.
    stroke_width: Width of the stroke, in pixels. Must be an int.
    method: Either 'label' (default), the picture will be auto-sized to fit
      the text either by auto-computing font size if width is provided or
      auto-computing width and height if font size is defined. 'caption' the
      text will be drawn in a picture with fixed size provided with the size
      argument. The text will be wrapped automatically, either by auto-computing
      font size if width and height are provided or adding line break when
      necessary if font size is defined
    text_align: center | left | right. Text align similar to css. Default to
      left.
    horizontal_align: center | left | right. Define horizontal align of text
      block in image. Default to center.
    vertical_align: center | top | bottom. Define vertical align of text bloc in
      image. Default to center.
    interline: Interline spacing. Default to 4.
    transparent: True (default) if you want to take into account the
      transparency in the image.
    duration: Duration of the clip.
    start_time: Start time of the clip in seconds.
    position: Position of the text on the video.
  """

  font: str | None = 'Arial'
  text: str | None = None
  filename: str | None = None
  font_size: int | None = None
  size: tuple[int, int] | tuple[None, None] = (None, None)
  margin: (
      tuple[float, float]
      | tuple[float, float, float, float]
      | tuple[None, None]
  ) = (None, None)
  color: str | tuple[int, int, int] | None = 'black'
  bg_color: str | tuple[int, int, int] | tuple[int, int, int, int] | None = None
  stroke_color: str | tuple[int, int, int] | None = None
  stroke_width: int = 0
  method: str = 'label'
  text_align: str = 'left'
  horizontal_align: str = 'center'
  vertical_align: str = 'center'
  interline: int = 4
  transparent: bool = True
  duration: float | None = None
  start_time: float = 0.0
  position: tuple[str | int, str | int] = ('right', 'top')


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


class RGBColor(pydantic.BaseModel):
  """Represents a color in the RGB color space.

  Ensures that red, green, and blue components are integers within the valid
  range of 0 to 255.

  Attributes:
    r (int): The red component of the color (0-255).
    g (int): The green component of the color (0-255).
    b (int): The blue component of the color (0-255).
  """

  r: int = pydantic.Field(ge=0, le=255)
  g: int = pydantic.Field(ge=0, le=255)
  b: int = pydantic.Field(ge=0, le=255)

  @classmethod
  def from_tuple(cls, rgb_tuple: tuple[int, int, int]) -> Self:
    """Creates an RGBColor instance from a tuple of integers.

    Args:
      rgb_tuple: A tuple containing three integers (r, g, b), each expected to
        be between 0 and 255.

    Returns:
      An instance of RGBColor.

    Raises:
      TypeError: If the input is not a tuple or does not contain exactly three
        elements.
      pydantic.ValidationError: If any tuple element is not an integer or is
        outside the 0-255 range."""
    if not isinstance(rgb_tuple, tuple) or len(rgb_tuple) != 3:
      raise TypeError('Input must be a tuple of 3 elements')
    try:
      return cls(r=rgb_tuple[0], g=rgb_tuple[1], b=rgb_tuple[2])
    except pydantic.ValidationError as e:
      raise e
