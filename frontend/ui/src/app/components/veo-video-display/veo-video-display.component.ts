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
 * @file The Veo Video Display component. Generating videos from Veo happens
 * aysncronously, and can take ~30-60s to complete. This component displays a
 * spinner while the videos are being generated, and then displays the videos
 * once they are ready.
 */
import {CommonModule} from '@angular/common';
import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {MatGridList, MatGridTile} from '@angular/material/grid-list';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {Subscription} from 'rxjs';
import {
  GeneratedSamples,
  VeoGetOperationStatusResponse,
} from '../../models/api-models';
import {ApiService} from '../../services/api.service';

/**
 * A component that displays videos generated by Veo.
 */
@Component({
  selector: 'app-veo-video-display',
  imports: [CommonModule, MatGridList, MatGridTile, MatProgressSpinner],
  templateUrl: './veo-video-display.component.html',
  styleUrl: './veo-video-display.component.scss',
})
export class VeoVideoDisplayComponent implements OnInit, OnDestroy {
  /**
   * Whether the component should be shown. If a request hasn't been made yet,
   * the component should not be shown.
   */
  showComponent = false;
  /**
   * True if waiting for the videos to be generated, false when they are ready
   * to be displayed.
   */
  isLoading = true;
  /**
   * The videos generated that need to be displayed to the user.
   */
  videos: GeneratedSamples | null = null;
  /**
   * The name of the current Veo operation.
   */
  veoOperationName: string | null = null;
  /**
   * Subscription to the Veo operation name observable.
   * Used to initiate polling when a new operation name is received.
   */
  veoOperationNameSubscription: Subscription = new Subscription();
  /**
   * Subscription to the Veo operation status observable.
   * Used to receive updates on the video generation process.
   */
  veoOperationStatusSubscription: Subscription = new Subscription();
  /**
   * The interval in milliseconds to poll the operation status.
   */
  POLLING_INTERVAL_MS = 5000;
  /**
   * The service for making API requests.
   */
  private apiService: ApiService;

  constructor() {
    this.apiService = inject(ApiService);
  }

  /**
   * Initializes the component and subscribes to necessary observables.
   *
   * Subscribes to `veoOperationName$` to detect when a new Veo operation is
   * initiated. When an operation name is received, it starts polling for the
   * operation status using `startPollingVeoOperationStatus()`.
   *
   * Also subscribes to `veoOperationStatus$` to receive updates on the video
   * generation process. When the operation is complete, `isLoading` is set to
   * `false`, and the generated videos are stored in `videos`.
   */
  ngOnInit() {
    this.veoOperationNameSubscription =
      this.apiService.veoOperationName$.subscribe((name: string | null) => {
        this.veoOperationName = name;
        if (name) {
          this.showComponent = true;
          this.isLoading = true;
          this.veoOperationStatusSubscription = this.apiService
            .startPollingVeoOperationStatus(name, this.POLLING_INTERVAL_MS)
            .subscribe((response: VeoGetOperationStatusResponse) => {
              this.isLoading = !response.done;
              this.videos = response.response;
            });
        } else {
          this.showComponent = false;
          this.isLoading = true;
          this.videos = null;
        }
      });
  }

  /**
   * Cleans up subscriptions when the component is destroyed.
   *
   * Unsubscribes from `veoOperationNameSubscription` and
   * `veoOperationStatusSubscription` to prevent memory leaks.
   */
  ngOnDestroy() {
    this.veoOperationNameSubscription.unsubscribe();
    this.veoOperationStatusSubscription.unsubscribe();
  }
}
