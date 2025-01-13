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
 * @file The VeoGenerateComponent, which is responsible for providing the user
 * interface to interact with the video generation API.
 */

import {CommonModule} from '@angular/common';
import {Component} from '@angular/core';
import {GenerateVideoResponse} from '../../models/api-models';
import {ApiService} from '../../services/api.service';

/**
 * A component that allows users to generate videos via Veo.
 */
@Component({
  selector: 'app-veo-generate',
  imports: [CommonModule],
  templateUrl: './veo-generate.component.html',
  styleUrls: ['./veo-generate.component.scss'],
})
export class VeoGenerateComponent {
  /**
   * The API response containing video generation information.
   */
  response: GenerateVideoResponse | undefined;
  /**
   * Indicates whether a video generation request is in progress.
   */
  isLoading = false;

  /**
   * @param apiService The service for making API requests.
   */
  constructor(private apiService: ApiService) {}

  /**
   * Sends a request to generate a video.
   */
  generateVideo() {
    this.isLoading = true;
    this.apiService.generateVideo().subscribe({
      next: (response: GenerateVideoResponse) => {
        this.response = response;
      },
      error: (error) => {
        console.error('Error fetching data:', error);
      },
      complete: () => {
        this.isLoading = false;
      },
    });
  }
}
