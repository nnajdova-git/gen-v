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
import {of} from 'rxjs';
import {GenerateVideoResponse} from '../../models/api-models';
import {ApiService} from '../../services/api.service';
import {VeoGenerateComponent} from './veo-generate.component';

describe('VeoGenerateComponent', () => {
  let component: VeoGenerateComponent;
  let fixture: ComponentFixture<VeoGenerateComponent>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  beforeEach(async () => {
    apiServiceSpy = jasmine.createSpyObj('ApiService', ['generateVideo']);

    await TestBed.configureTestingModule({
      imports: [VeoGenerateComponent],
      providers: [{provide: ApiService, useValue: apiServiceSpy}],
    }).compileComponents();

    fixture = TestBed.createComponent(VeoGenerateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should call generateVideo and set response', () => {
    const mockResponse: GenerateVideoResponse = {
      operation_name: 'test-operation-name',
    };
    apiServiceSpy.generateVideo.and.returnValue(of(mockResponse));

    component.generateVideo();

    expect(apiServiceSpy.generateVideo).toHaveBeenCalled();
    expect(component.response).toEqual(mockResponse);
    expect(component.isLoading).toBeFalse();
  });
});
