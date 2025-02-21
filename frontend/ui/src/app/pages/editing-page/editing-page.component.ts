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
import {CommonModule} from '@angular/common';
import {Component, inject} from '@angular/core';
import {map, Subscription} from 'rxjs';
import {AssetListComponent} from '../../components/shared/asset-list/asset-list.component';
import {VeoGetOperationStatusResponse} from '../../models/api.models';
import {Asset, ImageAsset, VideoAsset} from '../../models/asset.models';
import {ApiService} from '../../services/api.service';
import {BrandService} from '../../services/brand.service';

/**
 * The editing page component.
 *
 * This component is responsible for displaying the editing page, which is used
 * to edit assets, e.g. to overlay brand images on generated videos.
 */
@Component({
  selector: 'app-editing-page',
  imports: [AssetListComponent, CommonModule],
  templateUrl: './editing-page.component.html',
  styleUrl: './editing-page.component.scss',
})
export class EditingPageComponent {
  /*
   * A list of brand assets, e.g. logos. These are the assets that will be
   * overlaid on the generated assets.
   */
  brandAssets: ImageAsset[] = [];
  /**
   * A list of generated assets, e.g. videos. These are the assets that will be
   * edited.
   */
  generatedAssets: Asset[] = [];
  /**
   * A collection of subscriptions to observables.  This is used to manage
   * subscriptions and unsubscribe from them when the component is destroyed.
   */
  private subscriptions = new Subscription();
  /**
   * The `BrandService` for managing brand-related data.
   * @private
   */
  private brandService = inject(BrandService);
  /**
   * The `ApiService` for making API requests.
   */
  private apiService = inject(ApiService);

  /**
   * Lifecycle hook called when the component is initialised.  Fetches initial
   * data and sets up subscriptions.
   */
  ngOnInit(): void {
    this.loadBrandAssets();
    this.subscribeToGeneratedAssets();
  }

  /**
   * Lifecycle hook called when the component is destroyed.  Unsubscribes from
   * all active subscriptions to prevent memory leaks.
   */
  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  /**
   * Loads brand assets from the `BrandService`.
   */
  loadBrandAssets(): void {
    this.subscriptions.add(
      this.brandService.brandImages$.subscribe({
        next: (images) => {
          this.brandAssets = images;
        },
        error: (error) => {
          console.error(error);
        },
      }),
    );

    if (this.brandAssets.length === 0) {
      this.subscriptions.add(this.brandService.loadBrandImages().subscribe());
    }
  }

  /**
   * Subscribes to the `veoOperationStatus$` observable from the `ApiService`
   * to receive updates on generated video assets.
   */
  subscribeToGeneratedAssets(): void {
    this.subscriptions.add(
      this.apiService.veoOperationStatus$
        .pipe(
          map((response: VeoGetOperationStatusResponse | null) => {
            if (response && response.done && response.videos) {
              return response.videos.map(
                (video) =>
                  ({
                    id: this.generateId(),
                    signed_url: video.signed_uri,
                    type: 'video',
                    source: 'Veo',
                    date_created: new Date(),
                    selected: false,
                  }) as VideoAsset,
              );
            }
            return [];
          }),
          map((assets) => assets as Asset[]),
        )
        .subscribe({
          next: (assets) => {
            this.generatedAssets = assets;
          },
          error: (error) => {
            console.error(error);
          },
        }),
    );
  }

  /**
   * Generates a unique ID for assets.
   *
   * @return A string representing a random ID.
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15);
  }
}
