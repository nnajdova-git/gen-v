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
import {
  BehaviorSubject,
  catchError,
  interval,
  map,
  Observable,
  race,
  switchMap,
  takeWhile,
  tap,
  throwError,
  timer,
} from 'rxjs';
import {environment} from '../../environments/environment';
import {
  VeoGenerateVideoRequest,
  VeoGenerateVideoResponse,
  VeoGetOperationStatusRequest,
  VeoGetOperationStatusResponse,
} from '../models/api.models';
import {ImageAsset} from '../models/asset.models';

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
   * A BehaviorSubject to store and emit the current veo operation name.
   * Using BehaviorSubject so that new subscribers will get the last emitted
   * value.
   */
  private veoOperationNameSubject = new BehaviorSubject<string | null>(null);

  /**
   * An Observable that emits the current veo operation name.
   * Components can subscribe to this to get updates on the operation name.
   */
  veoOperationName$ = this.veoOperationNameSubject.asObservable();

  /**
   * A BehaviorSubject to store and emit the Veo operation status.
   */
  private veoOperationStatusSubject =
    new BehaviorSubject<VeoGetOperationStatusResponse | null>(null);

  /**
   * An Observable that emits the current Veo operation status.
   */
  veoOperationStatus$ = this.veoOperationStatusSubject.asObservable();

  /**
   * @param http The Angular HTTP client for making API requests.
   */
  constructor(private http: HttpClient) {}

  /**
   * Sends a request to generate a video via Veo.
   *
   * Clears any previous operation names and stores the new operation name in
   * `veoOperationName$`.
   *
   * @param request The generate video request for the API, including
   *  information like the prompt.
   * @return An Observable that emits the API response.
   *  The response contains the operation name, which is also stored in
   * `veoOperationName$`.
   */
  generateVideo(
    request: VeoGenerateVideoRequest,
  ): Observable<VeoGenerateVideoResponse> {
    this.clearVeoOperationName();
    const apiUrl = `${this.baseUrl}/veo/generate`;
    return this.http
      .post<VeoGenerateVideoResponse>(apiUrl, request, {
        withCredentials: true,
      })
      .pipe(
        tap((response: VeoGenerateVideoResponse) => {
          this.veoOperationNameSubject.next(response.operation_name);
        }),
      );
  }

  /**
   * Sends a request to get the status of a video generation operation via Veo.
   *
   * When you generate a video using Veo, it happens asynchronously, and the
   * operation name is returned. This endpoint checks the status of the
   * operation, and if it is done, returns links to the generated videos.
   *
   * @param request The request for the API, including the operation name.
   * @return An Observable that emits the API response.
   */
  getVeoOperationStatus(
    request: VeoGetOperationStatusRequest,
  ): Observable<VeoGetOperationStatusResponse> {
    const apiUrl = `${this.baseUrl}/veo/operation/status`;
    return this.http.post<VeoGetOperationStatusResponse>(apiUrl, request, {
      withCredentials: true,
    });
  }

  /**
   * Clears the current veo operation name.
   *
   * Useful when you want to reset the operation, for example, when starting a
   * new veo generation job.
   */
  clearVeoOperationName() {
    this.veoOperationNameSubject.next(null);
  }

  /**
   * Starts polling for the status of a Veo operation.
   *
   * @param operationName The name of the operation to poll.
   * @param intervalMs The interval in milliseconds at which to poll.
   * @param totalTimeoutMs The maximum time in milliseconds to continue polling before giving up.
   * @return An Observable that emits the operation status each time it's
   *  polled. The Observable completes when the operation is done.
   */
  startPollingVeoOperationStatus(
    operationName: string,
    intervalMs = 5000,
    totalTimeoutMs = 60000,
  ): Observable<VeoGetOperationStatusResponse> {
    return race(
      interval(intervalMs).pipe(
        switchMap(() =>
          this.getVeoOperationStatus({operation_name: operationName}),
        ),
        tap((response: VeoGetOperationStatusResponse) =>
          this.veoOperationStatusSubject.next(response),
        ),
        takeWhile(
          (response: VeoGetOperationStatusResponse) => !response.done,
          true,
        ),
      ),
      timer(totalTimeoutMs).pipe(
        switchMap(() =>
          throwError(
            () =>
              new Error('Polling timed out after ' + totalTimeoutMs + 'ms.'),
          ),
        ),
      ),
    );
  }

  /**
   * Generates a random ID for an asset.
   *
   * @return A string representing a random ID.
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15);
  }

  /**
   * Get the brand images, e.g. logos, from the backend datastore.
   * @return A list of images including the metadata associated with them.
   */
  getBrandImages(): Observable<ImageAsset[]> {
    const url = `${this.baseUrl}/assets/images/type/Brand`;
    return this.http.get<ImageAsset[]>(url, {withCredentials: true}).pipe(
      map(
        (images) =>
          images.map((image) => ({
            ...image,
            id: this.generateId(),
            selected: false,
            type: 'image',
          })) as ImageAsset[],
      ),
      catchError((error) => {
        console.error('Error fetching brand images:', error);
        return throwError(() => error);
      }),
    );
  }
}
