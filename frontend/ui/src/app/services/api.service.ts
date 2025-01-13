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
 * @file This file contains the `ApiService` which handles communication
 * between the frontend UI and the backend API. It provides methods for
 * making HTTP requests to the backend to perform actions like generating
 * videos.
 */

import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {GenerateVideoResponse} from '../models/api-models';

/**
 * A service that handles API requests to the backend.
 */
@Injectable({
  providedIn: 'root',
})
export class ApiService {
  /**
   * The base URL for the backend API.
   */
  private baseUrl = environment.backendUrl;

  /**
   * @param http The Angular HTTP client for making API requests.
   */
  constructor(private http: HttpClient) {}

  /**
   * Sends a request to generate a video via Veo.
   *
   * @return An Observable that emits the API response.
   */
  generateVideo(): Observable<GenerateVideoResponse> {
    const apiUrl = `${this.baseUrl}/veo/generate`;
    return this.http.get<GenerateVideoResponse>(apiUrl);
  }
}
