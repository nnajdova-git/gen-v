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
"""Date related utility functions."""
from datetime import date


def get_current_week_year_str(date_obj: date | None = None) -> str:
  """Generates a string representing the current ISO week and year.

  Format: "weekW-YYYY" (e.g., "week16-2025") based on the current date.

  Args:
    date_obj: The date object to format.

  Returns:
    The formatted week and year string.
  """
  date_obj = date_obj or date.today()
  current_year, current_week, _ = date_obj.isocalendar()
  week_and_year = f"week{current_week}-{current_year}"
  return week_and_year
