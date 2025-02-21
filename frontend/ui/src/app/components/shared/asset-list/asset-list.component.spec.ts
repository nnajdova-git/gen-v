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
import {
  ComponentFixture,
  fakeAsync,
  TestBed,
  tick,
} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {Asset} from '../../../models/asset.models';
import {AssetListComponent} from './asset-list.component';

describe('AssetListComponent', () => {
  let component: AssetListComponent<Asset>;
  let fixture: ComponentFixture<AssetListComponent<Asset>>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommonModule, AssetListComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AssetListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display assets and toggle selection on click', fakeAsync(() => {
    const mockAssets: Asset[] = [
      {
        id: '1',
        signed_url: 'https://example-signed-url.com/image1.jpg',
        type: 'image',
        selected: false,
      },
      {
        id: '2',
        signed_url: 'https://example-signed-url.com/image2.jpg',
        type: 'image',
        selected: false,
      },
    ];
    component.assets = mockAssets;
    fixture.detectChanges();
    tick();

    const assetItems = fixture.debugElement.queryAll(
      By.css('.asset-list__item'),
    );
    expect(assetItems.length).toBe(2);

    const checkbox1 = assetItems[0].query(By.css('input[type="checkbox"]'));
    expect(checkbox1.nativeElement.checked).toBe(false);

    assetItems[0].triggerEventHandler('click', null);
    fixture.detectChanges();
    tick();

    expect(mockAssets[0].selected).toBe(true);
    expect(checkbox1.nativeElement.checked).toBe(true);
  }));
});
