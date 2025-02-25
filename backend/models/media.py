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

from typing import Any

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
    method: Either 'label' (default), the picture will be autosized so as to fit
      the text either by auto-computing font size if width is provided or
      auto-computing width and height if font size is defined. 'caption' the
      text will be drawn in a picture with fixed size provided with the size
      argument. The text will be wrapped automatically, either by auto-computing
      font size if width and height are provided or adding line break when
      necesarry if font size is defined
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

  @pydantic.model_validator(mode='before')
  @classmethod
  def ensure_text_or_filename(cls, values: dict[str, Any]) -> dict[str, Any]:
    """Validates that either 'text' or 'filename' is provided."""
    if values.get('filename') is None and values.get('text') is None:
      raise ValueError('Either text or filename must be provided.')
    return values

  @pydantic.model_validator(mode='before')
  @classmethod
  def validate_font_size_for_label(
      cls, values: dict[str, Any]
  ) -> dict[str, Any]:
    """Validates 'font_size' for 'label' method."""
    method = values.get('method')
    font_size = values.get('font_size')
    if method == 'label' and font_size is None:
      raise ValueError("Font size must be provided when method is 'label'.")
    return values

  @pydantic.model_validator(mode='before')
  @classmethod
  def validate_size_for_caption(cls, values: dict[str, Any]) -> dict[str, Any]:
    """Validates 'size' for 'caption' method."""
    method = values.get('method')
    size = values.get('size')
    if method == 'caption' and size is None:
      raise ValueError("Size must be provided when method is 'caption'.")
    return values

  @pydantic.model_validator(mode='before')
  @classmethod
  def validate_bg_color_length(cls, values: dict[str, Any]) -> dict[str, Any]:
    """Validates that bg_color is a touple of 4 when Transparent is True."""
    bg_color = values.get('bg_color')
    transparent = values.get('transparent')
    if transparent and isinstance(bg_color, tuple) and len(bg_color) != 4:
      raise ValueError(
          'Background colour should be a touple of 4 when Transparent is True.'
      )
    return values

  @pydantic.field_validator('margin', mode='before')
  @classmethod
  def validate_margin_format(
      cls,
      margin: (
          tuple[float, float]
          | tuple[float, float, float, float]
          | tuple[None, None]
      ),
  ) -> (
      tuple[float, float]
      | tuple[float, float, float, float]
      | tuple[None, None]
  ):
    """Validates that margin is a tuple of length 2 or 4 with non-negative numbers or None."""
    if not isinstance(margin, tuple):
      raise ValueError('Margin must be a tuple.')

    if len(margin) not in (2, 4):
      raise ValueError('Margin tuple must have length 2 or 4.')

    for m in margin:
      if m is not None and not isinstance(m, (int, float)):
        raise ValueError('Margin values must be numbers or None.')
      if isinstance(m, (int, float)) and m < 0:
        raise ValueError('Margin values must be non-negative.')
    return margin

  @pydantic.field_validator('method')
  @classmethod
  def validate_method_allowed_values(cls, method: str) -> str:
    """Validates that method is one of 'label' or 'caption'."""
    if method not in ('label', 'caption'):
      raise ValueError("Method must be either 'label' or 'caption'.")
    return method

  @pydantic.field_validator('text_align')
  @classmethod
  def validate_text_align_allowed_values(cls, text_align: str) -> str:
    """Validates that text_align is one of 'center', 'left', 'right'."""
    if text_align not in ('center', 'left', 'right'):
      raise ValueError(
          "Text align must be one of 'center', 'left', or 'right'."
      )
    return text_align

  @pydantic.field_validator('horizontal_align')
  @classmethod
  def validate_horizontal_align_allowed_values(
      cls, horizontal_align: str
  ) -> str:
    """Validates that horizontal_align is one of 'center', 'left', 'right'."""
    if horizontal_align not in ('center', 'left', 'right'):
      raise ValueError(
          "Horizontal align must be one of 'center', 'left', or 'right'."
      )
    return horizontal_align

  @pydantic.field_validator('vertical_align')
  @classmethod
  def validate_vertical_align_allowed_values(cls, vertical_align: str) -> str:
    """Validates that vertical_align is one of 'center', 'top', 'bottom'."""
    if vertical_align not in ('center', 'top', 'bottom'):
      raise ValueError(
          "Vertical align must be one of 'center', 'top', or 'bottom'."
      )
    return vertical_align
