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
"""The models for working with Veo."""
import pydantic


class GenerateVideoRequest(pydantic.BaseModel):
  """Represents a request to the Veo video generation API.

  Attributes:
    prompt: The prompt to provide to Veo.
    image: A base64-encoded image to use in the generated video.
  """
  prompt: str
  image: str | None = None


class GenerateVideoResponse(pydantic.BaseModel):
  """Represents a response from the Veo video generation API.

  Attributes:
    operation_name: The name of the operation used to track the video generation
      process.
  """
  operation_name: str
