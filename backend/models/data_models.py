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
"""Data models for the application.

This module defines Pydantic models used to represent data entities within the
application. These models are database-agnostic and can be used with various
data storage solutions.

The module includes a base `DataModel` class that serves as a foundation for all
other data models, promoting consistency and providing a central place for
common fields or methods.

These models are used for data validation, serialization, and type hinting
throughout, the application.  They help ensure data integrity and improve code
maintainability.
"""
import pydantic


class DataModel(pydantic.BaseModel):
  """Base class for all data models."""
  pass
