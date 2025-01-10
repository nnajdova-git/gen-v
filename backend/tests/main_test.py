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
import main
import pytest


@pytest.fixture(name='client')
def client_fixture():
  main.app.config['TESTING'] = True
  with main.app.test_client() as test_client:
    yield test_client


def test_veo_generate_video(client):
  response = client.get('/veo/generate')
  assert response.status_code == 200
  assert response.json == {
      'operation_name': 'projects/PROJECT_ID/operations/OPERATION_ID'
  }
