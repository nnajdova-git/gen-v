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
import sys

import fastapi
from fastapi.middleware import cors
from routers import assets
from routers import veo
import settings
import uvicorn


# Configure logging.
logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialise the environment settings.
env_settings = settings.EnvSettings()

app = fastapi.FastAPI()
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=[env_settings.allowed_origin],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(veo.router, prefix='/veo')
app.include_router(assets.router, prefix='/assets')


if __name__ == '__main__':
  uvicorn.run(app, host=env_settings.host, port=env_settings.port)
