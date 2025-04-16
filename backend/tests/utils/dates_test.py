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
"""Unit tests for date utility functions."""
from datetime import date
import pytest
from gen_v.utils import dates


@pytest.mark.parametrize(
    'test_date, expected_week',
    [
        (date(2024, 12, 29), 'week52-2024'),
        (date(2025, 1, 1), 'week1-2025'),
        (date(2025, 4, 16), 'week16-2025'),
    ],
)
def test_get_current_week_year_str(test_date, expected_week):
  """Tests that the function returns the correct week-year string."""
  response = dates.get_current_week_year_str(test_date)
  assert response == expected_week
