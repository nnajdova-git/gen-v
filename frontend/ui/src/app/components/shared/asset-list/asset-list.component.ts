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
import {Component, Input} from '@angular/core';
import {Asset} from '../../../models/asset.models';

/**
 * AssetListComponent is a generic component for displaying a list of assets.
 * It takes an array of assets as input and displays them in a grid, allowing a
 * user to select them.
 */
@Component({
  selector: 'app-asset-list',
  imports: [CommonModule],
  templateUrl: './asset-list.component.html',
  styleUrl: './asset-list.component.scss',
})
export class AssetListComponent<T extends Asset> {
  /**
   * The list of assets to display.
   */
  @Input() assets: T[] = [];

  /**
   * When an asset is clicked, this function is called to update its selection
   * state.
   * @param asset The asset that was clicked.
   */
  onAssetClick(asset: T): void {
    asset.selected = !asset.selected;
  }

  /**
   * Track by function for the asset list.
   * @param _index The index of the asset.
   * @param item The asset to track.
   * @return The id of the asset.
   */
  trackByFn(_index: number, item: Asset): string {
    return item.id;
  }

  /**
   * Checks if an asset is selected.
   * @param asset The asset to check.
   * @return True if the asset is selected, false otherwise.
   */
  isSelected(asset: T): boolean {
    return asset.selected;
  }
}
