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
 * @file Defines the data models used for interacting with the backend API.
 * It includes interfaces that represent the structure of requests and responses
 * exchanged between the Angular application and the API endpoints.
 */

/**
 * Represents a request to the Veo video generation API.
 */
export interface GenerateVideoRequest {
  /**
   * The prompt to provide to Veo.
   */
  prompt: string;
  /**
   * A base64-encoded image to use in the generated video.
   */
  image?: string;
}

/**
 * Represents the response from the Veo video generation API.
 */
export interface GenerateVideoResponse {
  /**
   * The name of the operation used to track the video generation process.
   */
  operation_name: string;
}
