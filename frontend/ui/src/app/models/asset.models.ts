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
 * @file Defines the asset models used throughout the project.
 * For example, images & videos.
 */

/**
 * Represent the base class for asset types.
 */
export interface Asset {
  /**
   * The unique identifier of the asset.
   */
  id: string;
  /**
   * A signed URL to the file on GCS.
   */
  signed_url: string;
  /**
   * The type of the asset.
   */
  type: string;
  /**
   * Whether the asset is selected.
   */
  selected: boolean;
}

/**
 * Represent an image and associated metadata.
 */
export interface ImageAsset extends Asset {
  /**
   * The type of the asset.
   */
  type: 'image';
  /**
   * The source of the image, e.g. "Brand"
   */
  source: string;
  /**
   * Optional user-provided name for the image.
   */
  image_name?: string;
  /**
   * Optional context description for the image.
   */
  context?: string;
  /*
   * The datetime that this was created.
   */
  date_created: Date;
}

/**
 * Represent a video and associated metadata.
 */
export interface VideoAsset extends Asset {
  /**
   * The type of the asset.
   */
  type: 'video';
}
