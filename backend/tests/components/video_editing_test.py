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

"""Tests for video_editing module."""

import os

from components import video_editing
from models import media
import moviepy
from PIL import Image
import pytest


@pytest.fixture(name='sample_images_paths')
def fixture_sample_images(tmpdir):
  """Creates a few sample images for testing."""
  image_paths = []
  for i in range(3):
    image_path = os.path.join(tmpdir, f'image{i}.png')
    img = Image.new('RGB', (200, 100), color=(0, 255, 0))
    img.save(image_path)
    image_paths.append(image_path)
  return image_paths


@pytest.fixture(name='sample_videos_paths')
def fixture_sample_video(tmpdir):
  """Creates a few sample videos for testing."""
  video_paths = []
  for i in range(3):
    video_path = os.path.join(tmpdir, f'test_video{i}.mp4')
    clip = moviepy.ColorClip(size=(100, 100), color=(255, 0, 0), duration=5)
    clip.write_videofile(video_path, fps=24, codec='libx264')
    video_paths.append(video_path)
    clip.close()
  return video_paths


def test_check_file_exists_failure():
  with pytest.raises(
      FileNotFoundError, match='Media file not found: nonexistent_file.mp4'
  ):
    video_editing.check_file_exists('nonexistent_file.mp4')


def test_check_file_exists_success(sample_images_paths):
  video_editing.check_file_exists(sample_images_paths[0])


def test_image_rescaling(sample_images_paths):
  rescaled_image = video_editing.rescale_image(sample_images_paths[0], 200)
  assert rescaled_image.height == 200
  assert rescaled_image.width == 400


def test_add_image_clips_to_video_valid_inputs(
    sample_videos_paths, sample_images_paths, tmpdir
):
  """Tests the function with valid inputs, including image resizing."""
  output_path = os.path.join(tmpdir, 'output.mp4')
  image_inputs = [
      media.ImageInput(
          path=sample_images_paths[0],
          position=('center', 'top'),
          duration=2,
          height=30,
      ),
      media.ImageInput(
          path=sample_images_paths[1], position=('left', 'bottom'), duration=3
      ),
      media.ImageInput(
          path=sample_images_paths[2], position=(10, 10), duration=1
      ),
  ]

  video_editing.add_image_clips_to_video(
      sample_videos_paths[0], image_inputs, output_path
  )

  assert os.path.exists(output_path)


def test_add_image_clips_to_video_no_image_inputs(sample_videos_paths, tmpdir):
  """Tests the function with no image inputs."""
  output_path = os.path.join(tmpdir, 'output.mp4')
  image_inputs = []
  with pytest.raises(ValueError, match='No image inputs provided.'):
    video_editing.add_image_clips_to_video(
        sample_videos_paths[0], image_inputs, output_path
    )


def test_add_image_clips_no_resize_default_duration(
    sample_videos_paths, sample_images_paths, tmpdir
):
  """Tests with no resizing and using the video's duration for image clips."""
  output_path = os.path.join(tmpdir, 'output_noresize.mp4')
  image_inputs = [
      media.ImageInput(
          path=sample_images_paths[0], position=('center', 'center')
      )
  ]

  video_editing.add_image_clips_to_video(
      sample_videos_paths[0], image_inputs, output_path
  )

  assert os.path.exists(output_path)


def test_add_image_clips_single_frame_image(
    sample_videos_paths, sample_images_paths, tmpdir
):
  """Tests with an image clip duration of zero or a very small value."""
  output_path = os.path.join(tmpdir, 'output_single_frame.mp4')
  image_inputs = [
      media.ImageInput(
          path=sample_images_paths[0],
          position=('right', 'bottom'),
          duration=0.01,
      ),
  ]

  video_editing.add_image_clips_to_video(
      sample_videos_paths[0], image_inputs, output_path
  )

  assert os.path.exists(output_path)


def test_add_image_clips_multiple_resizes(
    sample_videos_paths, sample_images_paths, tmpdir
):
  """Tests resizing multiple images with different target heights."""
  output_path = os.path.join(tmpdir, 'output_multiple_resizes.mp4')
  image_inputs = [
      media.ImageInput(path=sample_images_paths[0], position=(5, 5), height=20),
      media.ImageInput(
          path=sample_images_paths[1], position=('center', 'center'), height=40
      ),
      media.ImageInput(
          path=sample_images_paths[2], position=('right', 'bottom'), height=60
      ),
  ]

  video_editing.add_image_clips_to_video(
      sample_videos_paths[0], image_inputs, output_path
  )

  assert os.path.exists(output_path)


def test_concatenate_video_clips(sample_videos_paths, tmpdir):
  """Tests concatenating multiple video clips."""
  output_path = os.path.join(tmpdir, 'concatenated_video.mp4')
  video_clips = [
      media.VideoInput(path=sample_video)
      for sample_video in sample_videos_paths
  ]

  video_editing.concatenate_video_clips(video_clips, output_path)

  assert os.path.exists(output_path)


def test_concatenate_video_clips_no_video_inputs(tmpdir):
  """Tests the function with no video inputs."""
  output_path = os.path.join(tmpdir, 'output.mp4')
  video_inputs = []
  with pytest.raises(ValueError, match='No video inputs provided.'):
    video_editing.concatenate_video_clips(video_inputs, output_path)
