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

import {
  ComponentFixture,
  TestBed,
  fakeAsync,
  tick,
} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {BehaviorSubject, of} from 'rxjs';
import {VeoGetOperationStatusResponse} from '../../models/api-models';
import {ApiService} from '../../services/api.service';
import {VeoVideoDisplayComponent} from './veo-video-display.component';

describe('VeoVideoDisplayComponent', () => {
  let component: VeoVideoDisplayComponent;
  let fixture: ComponentFixture<VeoVideoDisplayComponent>;
  let apiService: jasmine.SpyObj<ApiService>;

  beforeEach(async () => {
    const apiServiceSpy = jasmine.createSpyObj('ApiService', [
      'startPollingVeoOperationStatus',
    ]);
    apiServiceSpy.veoOperationName$ = new BehaviorSubject<string | null>(null);

    await TestBed.configureTestingModule({
      imports: [VeoVideoDisplayComponent],
      providers: [{provide: ApiService, useValue: apiServiceSpy}],
    }).compileComponents();

    fixture = TestBed.createComponent(VeoVideoDisplayComponent);
    component = fixture.componentInstance;
    apiService = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show and hide the component based on veoOperationName', () => {
    expect(component.showComponent).toBeFalse();

    // Show component when operation name is set
    (apiService.veoOperationName$ as BehaviorSubject<string | null>).next(
      'test-operation',
    );
    fixture.detectChanges();
    expect(component.showComponent).toBeTrue();

    // Hide component when operation name is cleared
    (apiService.veoOperationName$ as BehaviorSubject<string | null>).next(null);
    fixture.detectChanges();
    expect(component.showComponent).toBeFalse();
  });

  it('should display videos when operation is done', fakeAsync(() => {
    const operationName = 'test-operation';
    const mockResponse: VeoGetOperationStatusResponse = {
      name: operationName,
      done: true,
      response: {
        generated_samples: [
          {video: {uri: 'test-uri-1', encoding: 'video/mp4'}},
          {video: {uri: 'test-uri-2', encoding: 'video/mp4'}},
        ],
      },
    };

    apiService.startPollingVeoOperationStatus.and.returnValue(of(mockResponse));

    (apiService.veoOperationName$ as BehaviorSubject<string | null>).next(
      operationName,
    );

    tick();
    fixture.detectChanges();

    expect(component.isLoading).toBeFalse();
    expect(component.videos).toEqual(mockResponse.response);

    const videoElements = fixture.debugElement.queryAll(By.css('video'));
    expect(videoElements.length).toBe(2);
  }));
});
