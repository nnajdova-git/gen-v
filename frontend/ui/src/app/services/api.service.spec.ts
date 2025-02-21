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
import {fakeAsync, TestBed, tick} from '@angular/core/testing';
import {first, of} from 'rxjs';
import {environment} from '../../environments/environment';
import {
  VeoGenerateVideoRequest,
  VeoGenerateVideoResponse,
  VeoGetOperationStatusRequest,
  VeoGetOperationStatusResponse,
} from '../models/api.models';
import {ImageAsset} from '../models/asset.models';
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

  it('generateVideo should make a POST request to the correct URL and update veoOperationName', () => {
    const mockRequest: VeoGenerateVideoRequest = {prompt: 'test prompt'};
    const mockResponse: VeoGenerateVideoResponse = {
      operation_name: 'test-operation-name',
    };

    service.veoOperationName$.pipe(first()).subscribe((operationName) => {
      expect(operationName).toBeNull();
    });

    service.generateVideo(mockRequest).subscribe((response) => {
      expect(response.operation_name).toEqual(mockResponse.operation_name);
    });

    const req = httpMock.expectOne(`${environment.backendUrl}/veo/generate`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);

    service.veoOperationName$.pipe(first()).subscribe((operationName) => {
      expect(operationName).toEqual(mockResponse.operation_name);
    });
  });

  it('generateVideo should clear veoOperationName before making a new request', () => {
    const mockRequest: VeoGenerateVideoRequest = {prompt: 'test prompt'};
    const mockResponse: VeoGenerateVideoResponse = {
      operation_name: 'test-operation-name',
    };

    const clearSpy = spyOn(service, 'clearVeoOperationName');

    service.generateVideo(mockRequest).subscribe();

    const req = httpMock.expectOne(`${environment.backendUrl}/veo/generate`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);

    expect(clearSpy).toHaveBeenCalled();
  });

  it('getVeoOperationStatus should make a POST request with correct URL and parameters', () => {
    const mockOperationName = 'projects/PROJECT_ID/operations/OPERATION_ID';
    const mockRequest: VeoGetOperationStatusRequest = {
      operation_name: mockOperationName,
    };
    const mockResponse: VeoGetOperationStatusResponse = {
      name: mockOperationName,
      done: true,
      videos: [{
        uri: 'gs://BUCKET_NAME/TIMESTAMPED_FOLDER/sample_0.mp4',
        encoding: 'video/mp4',
        signed_uri: 'https://storage.googleapis.com/mock-bucket/mock-object2?signature=1234',
      }]
    };

    service.getVeoOperationStatus(mockRequest).subscribe((response) => {
      expect(response.name).toEqual(mockResponse.name);
      expect(response.done).toEqual(mockResponse.done);
      expect(response.videos).toEqual(mockResponse.videos);
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
      videos: null,
    };

    service.getVeoOperationStatus(mockRequest).subscribe((response) => {
      expect(response.name).toEqual(mockResponse.name);
      expect(response.done).toEqual(mockResponse.done);
      expect(response.videos).toBeNull();
    });

    const req = httpMock.expectOne(
      `${environment.backendUrl}/veo/operation/status`,
    );
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('clearVeoOperationName should clear the operation name', () => {
    service['veoOperationNameSubject'].next('test-operation-name');

    service.clearVeoOperationName();

    service.veoOperationName$.pipe(first()).subscribe((operationName) => {
      expect(operationName).toBeNull();
    });
  });

  it('startPollingVeoOperationStatus should poll for operation status and update veoOperationStatus$', fakeAsync(() => {
    const mockOperationName = 'test-operation-name';
    const mockResponses: VeoGetOperationStatusResponse[] = [
      {name: mockOperationName, done: false, videos: null},
      {name: mockOperationName, done: false, videos: null},
      {
        name: mockOperationName,
        done: true,
        videos: [{
          uri: 'gs://BUCKET_NAME/TIMESTAMPED_FOLDER/sample_0.mp4',
          encoding: 'video/mp4',
          signed_uri: 'https://storage.googleapis.com/mock-bucket/mock-object2?signature=1234',
        }]
      },
    ];

    let callCount = 0;
    spyOn(service, 'getVeoOperationStatus').and.callFake(() => {
      return of(mockResponses[callCount++]);
    });

    const statusUpdates: Array<VeoGetOperationStatusResponse | null> = [];
    service.veoOperationStatus$.subscribe((status) => {
      statusUpdates.push(status);
    });

    service.startPollingVeoOperationStatus(mockOperationName, 100).subscribe();

    tick(100);
    expect(statusUpdates.length).toBe(2);
    expect(statusUpdates[1]).toEqual(mockResponses[0]);

    tick(100);
    expect(statusUpdates.length).toBe(3);
    expect(statusUpdates[2]).toEqual(mockResponses[1]);

    tick(100);
    expect(statusUpdates.length).toBe(4);
    expect(statusUpdates[3]).toEqual(mockResponses[2]);

    expect(service.getVeoOperationStatus).toHaveBeenCalledTimes(3);

    tick(100);
    expect(statusUpdates.length).toBe(4);
  }));

  it('startPollingVeoOperationStatus should timeout after totalTimeoutMs', fakeAsync(() => {
    const mockOperationName = 'test-operation-name';
    const totalTimeoutMs = 180;
    const intervalMs = 50;

    spyOn(service, 'getVeoOperationStatus').and.returnValue(
      of({name: mockOperationName, done: false, videos: null}),
    );

    const statusUpdates: VeoGetOperationStatusResponse[] = [];
    service.veoOperationStatus$.subscribe((status) => {
      statusUpdates.push(status!);
    });

    service
      .startPollingVeoOperationStatus(
        mockOperationName,
        intervalMs,
        totalTimeoutMs,
      )
      .subscribe({
        error: (error: Error) => {
          expect(error.message).toBe(
            `Polling timed out after ${totalTimeoutMs}ms.`,
          );
        },
      });

    tick(totalTimeoutMs);

    expect(service.getVeoOperationStatus).toHaveBeenCalled();
    expect(service.getVeoOperationStatus).toHaveBeenCalledTimes(3);
  }));

  it('getBrandImages should return an array of ImageAsset', (done) => {
    const mockImages: ImageAsset[] = [
      {
        id: '123',
        type: 'image',
        source: 'Brand',
        image_name: 'image1.jpg',
        context: 'Logo',
        date_created: new Date(),
        signed_url: 'http://example.com/image1.jpg',
        selected: false,
      },
      {
        id: '456',
        type: 'image',
        source: 'Brand',
        image_name: 'image2.png',
        context: 'Icon',
        date_created: new Date(),
        signed_url: 'http://example.com/image2.png',
        selected: true,
      },
    ];

    service.getBrandImages().subscribe((images) => {
      expect(images.length).toBe(2);
      expect(images).toEqual(
        jasmine.arrayContaining([
          jasmine.objectContaining({ image_name: 'image1.jpg' }),
          jasmine.objectContaining({ image_name: 'image2.png' }),
        ]),
      );
      done();
    });

    const req = httpMock.expectOne(
      `${environment.backendUrl}/assets/images/type/Brand`,
    );
    expect(req.request.method).toBe('GET');

    req.flush(
      mockImages.map((img) => {
        const {id, selected, type, ...rest} = img;
        return rest;
      }),
    );
  });
});
