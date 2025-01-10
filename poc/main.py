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
"""The orchestration for Gen V. This is the main entry point."""
import os
import combiner
import texttospeech
import vertexai

MEDIA_PATH = '../media'
VIDEO_PATH = os.path.join(MEDIA_PATH, 'input-video.mp4')
IMAGE_PATH = os.path.join(MEDIA_PATH, 'logo.png')
AUDIO_PATH = os.path.join(MEDIA_PATH, 'voice-over.mp3')
OUTPUT_PATH = os.path.join(MEDIA_PATH, 'output-video.mp4')
LOGO_POSITION = ('right', 'top')
LOGO_DURATION = None  # Show for the whole video
LOGO_HEIGHT = 120


def main():
  video = vertexai.generate_video_from_veo()
  script = vertexai.generate_voice_over_script()
  voice_over_audio = texttospeech.generate_voice_over_audio(script)
  print(video, script, voice_over_audio)

  combiner.create_video_with_brand_and_audio(
      video_path=VIDEO_PATH,
      logo_image_path=IMAGE_PATH,
      audio_path=AUDIO_PATH,
      output_path=OUTPUT_PATH,
      logo_image_position=LOGO_POSITION,
      logo_image_duration=LOGO_DURATION,
      logo_image_height=LOGO_HEIGHT,
  )


if __name__ == '__main__':
  main()
