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
"""The main entry point for the backend.

This file provides the routing for the backend application.
"""

import logging
import os
import sys

import fastapi
from fastapi.middleware import cors
from models import veo_models
import uvicorn


# Configure logging.
logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# The host and port to run the application on.
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8080))
# The origin to allow CORS requests from.
ALLOWED_ORIGIN = os.environ.get('ALLOWED_ORIGIN', '*')

app = fastapi.FastAPI()
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/veo/generate')
async def veo_generate_video(
    request: veo_models.VeoGenerateVideoRequest,
) -> veo_models.VeoGenerateVideoResponse:
  """Generates a video using Veo and returns the operation name.

  Args:
    request: The request for generating a video, which includes information
      about the prompt and the video parameters.

  Returns:
    The response from the video generation including the operation name.
  """
  # TODO: b/389066523 - Remove mock logic.
  logger.info('VeoGenerateRequest: %s', request)
  operation_name = 'projects/PROJECT_ID/operations/OPERATION_ID'
  return veo_models.VeoGenerateVideoResponse(operation_name=operation_name)


@app.post('/veo/operation/status')
async def veo_operation_status(
    request: veo_models.VeoGetOperationStatusRequest,
) -> veo_models.VeoGetOperationStatusResponse:
  """Checks the status of a video generation operation.

  When you generate a video using Veo, it happens asynchronously, and the
  operation name is returned. This endpoint checks the status of the operation,
  and if it is done, returns links to the generated videos.

  Args:
    request: The request for checking the status of a video generation
      operation, which includes the operation name.

  Returns:
    The response from the operation status check, which includes the operation
    name, whether the operation is done, and if it is done, the generated
    videos.
  """
  # TODO: b/390327877 - Remove mock response.
  logger.info('VeoGetOperationStatusRequest: %s', request)
  response = veo_models.VeoGetOperationStatusResponse(**{
      'name': 'projects/PROJECT_ID/operations/OPERATION_ID',
      'done': True,
      'response': {
          'generated_samples': [{
              'video': {
                  'uri': 'gs://BUCKET_NAME/TIMESTAMPED_FOLDER/sample_0.mp4',
                  'encoding': 'video/mp4',
              }
          }]
      },
  })
  return response


if __name__ == '__main__':
  uvicorn.run(app, host=HOST, port=PORT)
