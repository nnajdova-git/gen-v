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
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import {TestBed} from '@angular/core/testing';
import {environment} from '../../environments/environment';
import {
  GenerateVideoRequest,
  GenerateVideoResponse,
} from '../models/api-models';
import {ApiService} from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ApiService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should make a POST request to the correct URL', () => {
    const mockRequest: GenerateVideoRequest = {prompt: 'test prompt'};
    const mockResponse: GenerateVideoResponse = {
      operation_name: 'test-operation-name',
    };

    service.generateVideo(mockRequest).subscribe((response) => {
      expect(response.operation_name).toEqual(mockResponse.operation_name);
    });

    const req = httpMock.expectOne(`${environment.backendUrl}/veo/generate`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });
});
