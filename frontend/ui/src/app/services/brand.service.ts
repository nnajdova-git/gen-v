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
 * @file This file contains the `BrandService` which is responsible for managing
 * brand level assets and data (e.g. brand logos) to components. It uses the
 * `ApiService` to fetch the data.
 */

import {inject, Injectable} from '@angular/core';
import {BehaviorSubject, catchError, Observable, shareReplay, tap} from 'rxjs';
import {ImageAsset} from '../models/asset.models';
import {ApiService} from './api.service';

/**
 * Service for managing brand-related assets and data, such as brand logos.
 *
 * This service provides a central point for accessing brand information,
 * abstracting the data fetching logic from components.
 */
@Injectable({
  providedIn: 'root',
})
export class BrandService {
  /**
   * The service for making API requests.
   */
  private apiService: ApiService = inject(ApiService);

  /**
   * Hold the current array of `ImageAsset` objects.
   */
  private brandImagesSubject = new BehaviorSubject<ImageAsset[]>([]);

  /**
   * Observable stream of `ImageAsset` objects representing the brand images.
   * Components should subscribe to this to receive updates.
   */
  brandImages$: Observable<ImageAsset[]> =
    this.brandImagesSubject.asObservable();

  /**
   * Loads and caches brand images from the API.
   *
   * Uses `shareReplay(1)` to ensure a single API request and immediate data for
   * late subscribers.
   *
   * @return An Observable emitting cached `ImageAsset` objects.
   */
  loadBrandImages(): Observable<ImageAsset[]> {
    return this.apiService.getBrandImages().pipe(
      tap((images) => this.brandImagesSubject.next(images)),
      catchError((err) => {
        console.error('Error loading brand images', err);
        return [];
      }),
      shareReplay(1),
    );
  }
}
