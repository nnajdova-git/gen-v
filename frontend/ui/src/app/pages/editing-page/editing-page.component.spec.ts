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
import {ComponentFixture, TestBed} from '@angular/core/testing';

import {provideHttpClient} from '@angular/common/http';
import {provideHttpClientTesting} from '@angular/common/http/testing';
import {provideNoopAnimations} from '@angular/platform-browser/animations';
import {BehaviorSubject, EMPTY, of} from 'rxjs';
import {VeoGetOperationStatusResponse} from '../../models/api.models';
import {ApiService} from '../../services/api.service';
import {BrandService} from '../../services/brand.service';
import {EditingPageComponent} from './editing-page.component';

describe('EditingPageComponent', () => {
  let component: EditingPageComponent;
  let fixture: ComponentFixture<EditingPageComponent>;
  let brandService: jasmine.SpyObj<BrandService>;
  let apiService: jasmine.SpyObj<ApiService>;

  beforeEach(async () => {
    const brandServiceSpy = jasmine.createSpyObj<BrandService>('BrandService', [
      'loadBrandImages',
    ]);
    const apiServiceSpy = jasmine.createSpyObj<ApiService>('ApiService', [], {
      veoOperationStatus$: EMPTY,
    });
    brandServiceSpy.loadBrandImages.and.returnValue(of([]));

    await TestBed.configureTestingModule({
      imports: [EditingPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideNoopAnimations(),
        {
          provide: BrandService,
          useFactory: () => {
            return {
              ...brandServiceSpy,
              brandImages$: of([]),
            };
          },
        },
        {provide: ApiService, useValue: apiServiceSpy},
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(EditingPageComponent);
    component = fixture.componentInstance;
    brandService = TestBed.inject(BrandService) as jasmine.SpyObj<BrandService>;
    apiService = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should load brand assets when brandAssets is empty', () => {
    component.brandAssets = [];
    component.loadBrandAssets();
    expect(brandService.loadBrandImages).toHaveBeenCalledTimes(1);
  });

  it('should set up a subscription to veoOperationStatus$', () => {
    const veoOperationStatusSubject =
      new BehaviorSubject<VeoGetOperationStatusResponse | null>(null);
    Object.defineProperty(apiService, 'veoOperationStatus$', {
      value: veoOperationStatusSubject.asObservable(),
      configurable: true,
    });

    spyOn(component['subscriptions'], 'add').and.callThrough();
    component.subscribeToGeneratedAssets();
    expect(component['subscriptions'].add).toHaveBeenCalled();
  });
});
