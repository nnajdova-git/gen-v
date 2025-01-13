/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Environment configuration for production.
 */
export const environment = {
  /**
   * Whether the application is running in production mode.
   */
  production: true,
  /**
   * The base URL for the backend API.
   * This placeholder is replaced as part of the deployment process.
   */
  backendUrl: '{{BACKEND_URL}}'
};
