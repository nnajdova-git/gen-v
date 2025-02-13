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
"""Unit tests for main.py."""

import fastapi
from fastapi import routing
import main


def test_app_creation():
  """Test that the FastAPI app is created."""
  assert isinstance(main.app, fastapi.FastAPI)


def test_router_inclusion():
  """Test that routers are included in the app."""
  assert any(
      route.path == '/veo/generate'
      for route in main.app.routes
      if isinstance(route, routing.APIRoute)
  )
  assert any(
      route.path == '/assets/images'
      for route in main.app.routes
      if isinstance(route, routing.APIRoute)
  )
