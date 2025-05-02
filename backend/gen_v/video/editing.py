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
import os
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

    add_text_clips_to_video(image_overlay_video, [promo_text], final_video)

  with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(process_video, videos)


def trim_clips(
    video_clips: list[mp.VideoFileClip],
    padding: float,
    output_length: int,
    trim_location: str,
    trim_enabled: bool = True,
) -> list[mp.VideoFileClip]:
  """Trims video clips to fit the desired output length.

  Args:
    video_clips: A list of moviepy VideoFileClip video clips.
    padding: The duration of the padding (for transitions) in seconds.
    output_length: The desired length of the output video in seconds.
    trim_location: Where to trim the videos ("start" or "end").
    trim_enabled: Boolean reflecting if trim is enabled.

  Returns:
    A list of trimmed moviepy VideoFileClip objects.

  Raises:
    ValueError: If the trim_location is invalid or if output_length is <= 0.
  """
  total_length = 0
  for video in video_clips:
    total_length += video.duration
  total_length -= padding * (len(video_clips) - 1)

  total_trim_length = total_length - output_length
  print(f"Total length: {total_length} Output length: {output_length}")
  if total_trim_length < 0 or not trim_enabled:
    print("Trimming not required.")
    return video_clips

  number_of_intros_outros_clips = 2
  number_of_veo_clips = len(video_clips) - number_of_intros_outros_clips
  trim_length = total_trim_length / number_of_veo_clips
  for index, video in enumerate(video_clips[1:-1]):
    if trim_location == "start":
      start_time = -(video.duration - trim_length)
      end_time = None
    elif trim_location == "end":
      start_time = 0
      end_time = video.duration - trim_length
    else:
      raise ValueError(f"Trim location {trim_location} not supported.")

    trimmed_clip = video.subclipped(start_time, end_time)
    video_clips[index + 1] = trimmed_clip

  total_length = 0
  for video in video_clips:
    total_length += video.duration
  total_length += padding * (len(video_clips) - 1)

  print(f"Total length: {total_length} Output length: {output_length}")
  return video_clips


def fade_in(
    video_clips: list[mp.VideoFileClip], padding: float
) -> mp.CompositeVideoClip:
  """Applies a fade-in transition between video clips and saves the result.

  Args:
    video_clips: A list of moviepy VideoFileClip objects to be concatenated.
    padding: The duration of the fade-in transition in seconds.
  Returns:
    mp.CompositeVideoClip: A single moviepy CompositeVideoClip object
                           representing all input clips concatenated with
                           fade-in transitions applied between them.
  """

  print("Concatenating video files...")
  video_fx_list = [video_clips[0]]
  idx = video_clips[0].duration - padding
  for video in video_clips[1:]:
    transition = mp.video.fx.CrossFadeIn(padding).copy()
    video_fx_list.append(transition.apply(video.with_start(idx)))
    idx += video.duration - padding

  composed_clip = mp.CompositeVideoClip(video_fx_list)

  return composed_clip


def slide_in(
    video_clips: list[mp.VideoFileClip], padding: float, side: str
) -> mp.CompositeVideoClip:
  """Applies a slide-in transition to a video clip.

  Args:
    video_clips: The input list of video clips.
    padding: The duration of the transition in seconds.
    side: The direction from which the clip slides in
     ("left", "right", "top", or "bottom"). Defaults to "left".

  Returns:
    mp.CompositeVideoClip: The video clip with the slide-in transition applied.
  """
  print("Concatenating video files...")
  video_fx_list = [video_clips[0]]
  idx = video_clips[0].duration - padding
  for video in video_clips[1:]:
    transition = mp.video.fx.SlideIn(padding, side).copy()
    video_fx_list.append(transition.apply(video.with_start(idx)))
    idx += video.duration - padding

  composed_clip = mp.CompositeVideoClip(video_fx_list)

  return composed_clip


def cross_fade(
    video_clips: list[mp.VideoFileClip],
    padding: float,
) -> mp.CompositeVideoClip:
  """Applies a cross-fade transition between video clips and saves the result.

  Args:
    video_clips: A list of moviepy VideoFileClip objects to be concatenated.
    padding: The duration of the cross-fade transition in seconds.
  Returns:
    mp.CompositeVideoClip: The video clip with cross-fade applied.
  """
  print("Concatenating video files...")
  # video_fx_list = []
  composed_clip = video_clips[0]
  # opposite_side = get_opposite_side(side)
  for video in video_clips[1:]:
    opposite_transition = mp.video.fx.CrossFadeOut(padding).copy()
    transition = mp.video.fx.CrossFadeIn(padding).copy()

    composed_effect = opposite_transition.apply(composed_clip)

    video_effect = transition.apply(
        video.with_start(composed_clip.duration - padding)
    )
    composed_clip = mp.CompositeVideoClip([composed_effect, video_effect])

  return composed_clip


def get_opposite_side(side: str) -> str:
  """Returns the opposite side of a given direction.

  Args:
    side: The input side ("left", "right", "top", or "bottom").

  Returns:
    The opposite side (e.g. "right" for "left", "left" for "right"...).

  Raises:
    ValueError: If the input side is not one of the valid options.
  """
  match side:
    case "left":
      return "right"
    case "right":
      return "left"
    case "top":
      return "bottom"
    case "bottom":
      return "top"
    case _:
      raise ValueError(f"Side {side} not supported.")


def swipe(
    video_clips: list[mp.VideoFileClip], padding: float, side: str
) -> mp.CompositeVideoClip:
  """Applies a swipe transition between video clips and saves the result.

  Args:
    video_clips: A list of moviepy VideoFileClip objects to be concatenated.
    padding: The duration of the transition (padding) in seconds.
    side: The direction of the swipe ('left', 'right', 'top', 'bottom').
  Returns:
    mp.CompositeVideoClip: The video clip with swipe applied.

  """
  print("Concatenating video files...")
  # video_fx_list = []
  composed_clip = video_clips[0]
  opposite_side = get_opposite_side(side)
  for video in video_clips[1:]:
    opposite_transition = mp.video.fx.SlideOut(padding, opposite_side).copy()
    transition = mp.video.fx.SlideIn(padding, side).copy()

    composed_effect = opposite_transition.apply(composed_clip)

    video_effect = transition.apply(
        video.with_start(composed_clip.duration - padding)
    )
    composed_clip = mp.CompositeVideoClip([composed_effect, video_effect])

  return composed_clip


def concatenate_video_clips(
    videos: list[str],
    transition: models.VideoTransition,
    output_length: int,
    trim_location: str,
    resized_image_width: int,
    resized_image_height: int,
    tmp_string: str = "/content",
) -> str:
  """Concatenates video clips with transitions and optional trimming.

  Args:
      videos: A list of paths to the video clips to concatenate.
      transition: A VideoTransition object with transition type and duration.
      output_length: The desired length of the output video in seconds.
      trim_location: Where to trim the videos ("start" or "end").
      resized_image_width: target image width.
      resized_image_height: target image height.
      tmp_string: path to the folder where clips are.

  Returns:
      The path to the concatenated video file, or None if an error occurred.
  """

  try:
    print(f"""Start concatenation of video files {videos}
                 with transition {transition}...""")
    if not videos:
      raise ValueError("No video inputs provided.")

    target_path = f"{tmp_string}/concat_target.mp4"
    video_clips = []
    target_resolution = set_target_resolution(
        videos[0], resized_image_width, resized_image_height
    )
    for vid in videos:
      video_clips.append(
          mp.VideoFileClip(vid, target_resolution=target_resolution)
      )

    video_clips = trim_clips(
        video_clips, transition.padding, output_length, trim_location
    )
    composed_clip = None
    match transition.name:
      case "CROSS_FADE":
        composed_clip = cross_fade(video_clips, transition.padding)
      case "FADE_IN":
        composed_clip = fade_in(video_clips, transition.padding)
      case "SWIPE":
        composed_clip = swipe(video_clips, transition.padding, transition.side)
      case "SLIDE_IN":
        composed_clip = slide_in(
            video_clips, transition.padding, transition.side
        )
      case _:
        raise ValueError(f"Transition {transition.name} not supported.")

    composed_clip.write_videofile(target_path, codec="libx264", logger=None)
    composed_clip.close()

  finally:
    # Clean up temporary files
    try:
      for video in videos:
        print(f"Removing temporary file {video}...")
        os.remove(video)
    except FileNotFoundError:
      pass

  print(f"Concatenation finished, video available: {target_path}")
  return target_path


def set_target_resolution(
    video: str, resized_image_width: int, resized_image_height: int
) -> tuple[int, int]:
  """Sets the target resolution for a video based on its orientation.

  Args:
    video: The path to the video file.
    resized_image_width: target image widht.
    resized_image_height: target image height.

  Returns:
    A tuple containing the target width and height (in pixels).

  """
  print("Retrieve the dimensions...")
  clip = mp.VideoFileClip(video)
  clip_dimension = clip.size
  if clip_dimension[0] < clip_dimension[1]:
    if resized_image_width > resized_image_height:
      dimension = (resized_image_height, resized_image_width)
    else:
      dimension = (resized_image_width, resized_image_height)
  elif clip_dimension[0] > clip_dimension[1]:
    if resized_image_width > resized_image_height:
      dimension = (resized_image_width, resized_image_height)
    else:
      dimension = (resized_image_height, resized_image_width)
  else:
    minimum_size = min(resized_image_height, resized_image_width)
    dimension = (minimum_size, minimum_size)
  # print(f'Output dimensions: {dimension}')
  return dimension


def check_file_exists(file_path: str) -> None:
  """Checks if a file exists at the given path.

  Args:
    file_path: The path to the file.
  Raises:
    FileNotFoundError: If the file does not exist.
  """
  if not os.path.exists(file_path):
    raise FileNotFoundError(f"Media file not found: {file_path}")


def merge_arrays(intro_outro_videos, main_content_videos):
  """Merges intro/outro videos with main content videos.

  This function takes two lists of videos: intro/outro videos and main
  content videos. It inserts the first intro/outro video at the beginning,
  appends all main content videos, and then adds the last intro/outro video
  at the end, creating a merged video sequence. If intro_outro_videos is
  empty, it returns main_content_videos directly.

  Args:
      intro_outro_videos: A list of intro/outro video paths.
                          The first element is used as the intro, and the last
                          as the outro. Can be empty. If intro_outro_videos is
                          empty, it returns main_content_videos directly. If
                          intro_outro_video contains only one video, it
                          appends the same video to both begining and the end
                          of main_content_videos.
      main_content_videos: A list of main content video paths.

  Returns:
      A new list containing the merged video paths, or the
      `main_content_videos` list if `intro_outro_videos` is empty.
  """
  if len(intro_outro_videos) > 0:
    return (
        [intro_outro_videos[0]] + main_content_videos + [intro_outro_videos[-1]]
    )
  # If intro_outro_videos is empty, return main_content_videos directly
  return main_content_videos
