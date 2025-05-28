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
"""Exposes core functions for the video package."""

from gen_v.video.editing import add_text_clips_to_video
from gen_v.video.editing import display_image
from gen_v.video.editing import load_text_clips
from gen_v.video.editing import overlay_image_on_video
from gen_v.video.editing import process_videos_with_overlays_and_text
from gen_v.video.editing import trim_clips
from gen_v.video.editing import fade_in
from gen_v.video.editing import slide_in
from gen_v.video.editing import cross_fade
from gen_v.video.editing import get_opposite_side
from gen_v.video.editing import swipe
from gen_v.video.editing import concatenate_video_clips
from gen_v.video.editing import set_target_resolution
from gen_v.video.editing import check_file_exists
from gen_v.video.editing import merge_arrays
from gen_v.video.editing import calculate_audio_duration
from gen_v.video.editing import load_audio_clips
from gen_v.video.editing import add_audio_clips_to_video
from gen_v.video.generation import fetch_operation
from gen_v.video.generation import generate_videos_and_download
from gen_v.video.generation import generate_videos_concurrently
from gen_v.video.generation import get_gemini_generated_video_prompt
from gen_v.video.generation import image_to_video
from gen_v.video.generation import send_request_to_google_api
from gen_v.video.generation import generate_videos


__all__ = [
    'add_text_clips_to_video',
    'display_image',
    'load_text_clips',
    'overlay_image_on_video',
    'process_videos_with_overlays_and_text',
    'trim_clips',
    'fade_in',
    'slide_in',
    'cross_fade',
    'get_opposite_side',
    'swipe',
    'concatenate_video_clips',
    'set_target_resolution',
    'check_file_exists',
    'merge_arrays',
    'calculate_audio_duration',
    'load_audio_clips',
    'add_audio_clips_to_video',
    'fetch_operation',
    'generate_videos_and_download',
    'generate_videos_concurrently',
    'get_gemini_generated_video_prompt',
    'image_to_video',
    'send_request_to_google_api',
    'generate_videos',
]
