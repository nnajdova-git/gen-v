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

import {provideHttpClient} from '@angular/common/http';
import {provideHttpClientTesting} from '@angular/common/http/testing';
import {TestBed} from '@angular/core/testing';
import {provideNoopAnimations} from '@angular/platform-browser/animations';
import {of} from 'rxjs';
import {ImageAsset} from '../models/asset.models';
import {ApiService} from './api.service';
import {BrandService} from './brand.service';

describe('BrandService', () => {
  let service: BrandService;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  beforeEach(() => {
    apiServiceSpy = jasmine.createSpyObj('ApiService', ['getBrandImages']);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideNoopAnimations(),
        BrandService,
        {provide: ApiService, useValue: apiServiceSpy},
      ],
    });
    service = TestBed.inject(BrandService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should load brand images and update brandImages$', (done: DoneFn) => {
    const now = new Date();
    const mockImages: ImageAsset[] = [
      {
        id: '1',
        type: 'image',
        source: 'Brand',
        image_name: 'Logo 1',
        context: 'Primary logo',
        date_created: now,
        signed_url: 'http://example.com/image1.png',
        selected: false,
      },
      {
        id: '2',
        type: 'image',
        source: 'Brand',
        image_name: 'Logo 2',
        context: 'Primary logo',
        date_created: now,
        signed_url: 'http://example.com/image2.png',
        selected: false,
      },
    ];

    apiServiceSpy.getBrandImages.and.returnValue(of(mockImages));
    service.loadBrandImages().subscribe();
    expect(apiServiceSpy.getBrandImages).toHaveBeenCalledTimes(1);

    service.brandImages$.subscribe((images) => {
      expect(images).toEqual(mockImages);
      done();
    });
  });
});
