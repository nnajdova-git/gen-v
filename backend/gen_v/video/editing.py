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
"""Video editing and processing functions using MoviePy.

This module provides utilities for manipulating video clips after generation.
"""
from typing import Any, Callable
import mediapy
from PIL import Image
from gen_v import models
from gen_v import storage as gcs
from gen_v import utils
import moviepy as mp
import contextlib
import concurrent.futures


def display_image(
    image_path: str,
    display_function: Callable[[Any], None] | None = None,
    **kwargs,
) -> None:
  """Displays image using a provided function or defaults to mediapy.show_image.

  Args:
    image_path: The local path to the image file.
    display_function: A callable that takes the image as its first argument and
      displays it. If None, defaults to mediapy.show_image.
    **kwargs: Additional keyword arguments passed directly to the display
      function. Useful for things like title or height.

  Raises:
    FileNotFoundError: If the image at the file path cannot be found.
    Image.UnidentifiedImageError: If the image couldn't be read by Pillow
  """
  if display_function is None:
    display_function = mediapy.show_image
    kwargs["title"] = kwargs.get("title", "Image")
    kwargs["border"] = True
  try:
    input_image = Image.open(image_path)
    display_function(input_image, **kwargs)
  except FileNotFoundError:
    print(f"Error: Image file not found: {image_path}")
  except Image.UnidentifiedImageError:
    print(f"Error: Could not open or read image file: {image_path}")


def overlay_image_on_video(
    input_video: models.VideoInput,
    images: list[models.ImageInput],
    output_video_path: models.VideoInput,
) -> mp.VideoFileClip:
  """Overlays images on a video.

  Args:
      input_video: A VideoInput object with the input video.
      images: A list of ImageInput objects with the images to overlay.
      output_video_path: A VideoInput object with the output video path.

  Returns:
      The modified video clip if successful, or None if an error occurred.
  """
  print("Started overlay_image_on_video...")

  # gcs_filename = gcs.get_file_name_from_gcs_url(input_video.path)
  local_video_path = input_video.path
  final_clip = mp.VideoFileClip(local_video_path)
  fade_duration = 1

  video_file_name = gcs.get_file_name_from_gcs_url(output_video_path.path)
  local_output_video_path = f"/content/overlay_output_{video_file_name}"

  for img in images:
    overlay_file_name = gcs.get_file_name_from_gcs_url(img.path)
    no_extension_video_file_name = video_file_name.split(".")[0]

    image_file_name = f"{no_extension_video_file_name}_{overlay_file_name}"
    local_img_path = gcs.download_file_locally(img.path, image_file_name)

    image_file = Image.open(local_img_path)
    image_file = image_file.convert("RGBA")
    local_img_path_png = local_img_path.replace(".jpg", ".png")
    image_file.save(local_img_path_png)

    if img.height > 0:
      resized_img_path = local_img_path_png.replace(".png", "_resized.png")
      rescaled_img = utils.rescale_image_height(local_img_path_png, img.height)
      rescaled_img.save(resized_img_path)
      local_img_path_png = resized_img_path
    img_clip = (
        mp.ImageClip(local_img_path_png)
        .with_duration(img.duration)
        .with_position(img.position)
    )
    img_clip = img_clip.with_effects(
        [mp.vfx.CrossFadeIn(fade_duration)]
    ).with_effects([mp.vfx.CrossFadeOut(fade_duration)])

    final_clip = mp.CompositeVideoClip(
        [final_clip, img_clip.with_start(img.start)]
    )

  # Write the output video
  final_clip.write_videofile(
      local_output_video_path,
      codec="libx264",
      fps=final_clip.fps,
      bitrate="8000k",
  )
  output_uri = output_video_path.path
  gcs.upload_file_to_gcs(local_output_video_path, output_uri)
  final_clip.close()
  return output_uri


@contextlib.contextmanager
def load_text_clips(video_path: str, text_inputs: list[models.TextInput]):
  """Loads text clips from a list of text inputs and a video clip.

  Args:
    video_path: The path to the video clip to use as a reference for duration.
    text_inputs: List of TextInput objects.
  Yields:
    List of TextClip objects and the video clip.
  """
  text_clips = []
  with mp.VideoFileClip(video_path) as video:
    for text_input in text_inputs:
      if not text_input.duration:
        text_input.duration = video.duration
      text_clip = mp.TextClip(
          **text_input.model_dump(exclude={"start_time", "position"})
      ).with_start(text_input.start_time)
      text_clip = text_clip.with_position(text_input.position)

      text_clips.append(text_clip)
    try:
      yield [video] + text_clips
    finally:
      for text_clip in text_clips:
        text_clip.close()


def add_text_clips_to_video(
    input_video: models.VideoInput,
    text_inputs: list[models.TextInput],
    output_video_path: models.VideoInput,
) -> None:
  """Adds text to a video clip.

  Args:
    input_video: Path to the video file.
    text_inputs: List of TextInput objects, each representing the text to add.
    output_video_path: Path to save the output video.
  """
  local_video_path = gcs.download_file_locally(input_video.path)
  input_file_name = gcs.get_file_name_from_gcs_url(input_video.path)
  local_output_video_path = f"/content/output_{input_file_name}"

  for text in text_inputs:
    local_font_path = gcs.download_file_locally(text.font)
    text.font = local_font_path

  with load_text_clips(local_video_path, text_inputs) as clips:
    with mp.CompositeVideoClip(clips) as final_clip:
      final_clip.write_videofile(local_output_video_path, codec="libx264")
      output_uri = output_video_path.path
      gcs.upload_file_to_gcs(local_output_video_path, output_uri)
      final_clip.close()


def process_videos_with_overlays_and_text(
    videos: list[dict[str, str]],
    images: list[models.ImageInput],
    overlay_text: models.TextInput,
    overlays_uri: str,
    final_uri: str,
) -> None:
  """Processes videos by adding image and text overlays and uploading to gcs.

  Args:
      videos: A list of video dictionaries with GCS URI and local file path.
      images: A list of `ImageInput` image overlays to be added to the videos.
      overlay_text: A `TextInput` object, defining the text overlay.
      overlays_uri: The GCS URI where intermediate overlays will be stored.
      final_uri: The GCS URI where final videos with overlays will be stored.

  Returns:
      None.
  """
  print("process_videos_with_overlays_and_text...")

  def process_video(video: dict[str, str]):
    """Processes a single video by adding overlays and text.

    Args:
      video: A dictionary representing a video
    """
    print(f"process_video: {video}")
    local_video_file_path = gcs.download_file_locally(
        video["gcs_uri"], video["local_file_name"]
    )
    local_video_file = models.VideoInput(path=local_video_file_path)

    gcs_file_name = video["local_file_name"]
    gcs_image_overlay_video_path = f"{overlays_uri}/{gcs_file_name}"
    image_overlay_video = models.VideoInput(
        path=f"gs://{gcs_image_overlay_video_path}"
    )

    overlay_image_on_video(local_video_file, images, image_overlay_video)

    promo_text = models.TextInput(
        text=video["promo_text"],
        font=overlay_text.font,
        font_size=overlay_text.font_size,
        start_time=overlay_text.start_time,
        duration=overlay_text.duration,
        color=overlay_text.color,
        position=overlay_text.position,
    )

    # Define the GCS path for the final video with text overlay.
    final_video_gcs_path = f"{final_uri}/{gcs_file_name}"
    final_video = models.VideoInput(path=final_video_gcs_path)

    add_text_clips_to_video(
        image_overlay_video, [promo_text], final_video
    )

  with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(process_video, videos)
