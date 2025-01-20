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
  VeoGenerateVideoRequest,
  VeoGenerateVideoResponse,
  VeoGetOperationStatusRequest,
  VeoGetOperationStatusResponse,
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

  it('generateVideo should make a POST request to the correct URL', () => {
    const mockRequest: VeoGenerateVideoRequest = {prompt: 'test prompt'};
    const mockResponse: VeoGenerateVideoResponse = {
      operation_name: 'test-operation-name',
    };

    service.generateVideo(mockRequest).subscribe((response) => {
      expect(response.operation_name).toEqual(mockResponse.operation_name);
    });

    const req = httpMock.expectOne(`${environment.backendUrl}/veo/generate`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('getVeoOperationStatus should make a POST request with correct URL and parameters', () => {
    const mockOperationName = 'projects/PROJECT_ID/operations/OPERATION_ID';
    const mockRequest: VeoGetOperationStatusRequest = {
      operation_name: mockOperationName,
    };
    const mockResponse: VeoGetOperationStatusResponse = {
      name: mockOperationName,
      done: true,
      response: {
        generated_samples: [
          {
            video: {
              uri: 'gs://BUCKET_NAME/TIMESTAMPED_FOLDER/sample_0.mp4',
              encoding: 'video/mp4',
            },
          },
        ],
      },
    };

    service.getVeoOperationStatus(mockRequest).subscribe((response) => {
      expect(response.name).toEqual(mockResponse.name);
      expect(response.done).toEqual(mockResponse.done);
      expect(response.response?.generated_samples).toEqual(
        mockResponse.response?.generated_samples,
      );
    });

    const req = httpMock.expectOne(
      `${environment.backendUrl}/veo/operation/status`,
    );
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('getVeoOperationStatus should handle incomplete operations correctly', () => {
    const mockOperationName = 'projects/PROJECT_ID/operations/OPERATION_ID';
    const mockRequest: VeoGetOperationStatusRequest = {
      operation_name: mockOperationName,
    };
    const mockResponse: VeoGetOperationStatusResponse = {
      name: mockOperationName,
      done: false,
      response: null,
    };

    service.getVeoOperationStatus(mockRequest).subscribe((response) => {
      expect(response.name).toEqual(mockResponse.name);
      expect(response.done).toEqual(mockResponse.done);
      expect(response.response).toBeNull();
    });

    const req = httpMock.expectOne(
      `${environment.backendUrl}/veo/operation/status`,
    );
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });
});
