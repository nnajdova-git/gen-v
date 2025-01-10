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

import os
from typing import Any
import flask
import flask_cors


HOST = os.environ.get('HOST', '0.0.0.0')
PORT = os.environ.get('PORT', 8080)
DEBUG = os.environ.get('DEBUG', True)


app = flask.Flask(__name__)
flask_cors.CORS(app)


@app.route('/veo/generate', methods=['GET'])
def veo_generate_video() -> dict[str, Any]:
  """Generates a video using Veo and returns the operation name."""
  # TODO: b/389066523 - Remove mock logic.
  operation_name = 'projects/PROJECT_ID/operations/OPERATION_ID'
  return {'operation_name': operation_name}


if __name__ == '__main__':
  app.run(debug=DEBUG, host=HOST, port=int(os.environ.get('PORT', PORT)))
