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
import {By} from '@angular/platform-browser';
import {NoopAnimationsModule} from '@angular/platform-browser/animations';
import {of, throwError} from 'rxjs';
import {
  VeoGenerateVideoRequest,
  VeoGenerateVideoResponse,
} from '../../../models/api.models';
import {SnackbarType} from '../../../models/material-design.enums';
import {ApiService} from '../../../services/api.service';
import {VeoGenerateComponent} from './veo-generate.component';

describe('VeoGenerateComponent', () => {
  let component: VeoGenerateComponent;
  let fixture: ComponentFixture<VeoGenerateComponent>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;
  let mockRequest: VeoGenerateVideoRequest;
  let mockResponse: VeoGenerateVideoResponse;

  beforeEach(async () => {
    mockRequest = {prompt: 'test prompt', image: undefined};
    mockResponse = {operation_name: 'test-operation-name'};

    apiServiceSpy = jasmine.createSpyObj('ApiService', ['generateVideo']);

    await TestBed.configureTestingModule({
      imports: [VeoGenerateComponent, NoopAnimationsModule],
      providers: [{provide: ApiService, useValue: apiServiceSpy}],
    }).compileComponents();

    fixture = TestBed.createComponent(VeoGenerateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should call generateVideo and handle success', () => {
    apiServiceSpy.generateVideo.and.returnValue(of(mockResponse));

    spyOn(component, 'showSnackbar');

    component.form.patchValue({prompt: mockRequest.prompt});
    component.generateVideo();

    expect(apiServiceSpy.generateVideo).toHaveBeenCalledWith(mockRequest);
    expect(component.showSnackbar).toHaveBeenCalledWith(
      jasmine.any(String),
      SnackbarType.SUCCESS,
    );
    expect(component.isLoading).toBeFalse();
  });

  it('should call generateVideo and handle error', () => {
    const mockError = new Error('test error');
    apiServiceSpy.generateVideo.and.returnValue(throwError(() => mockError));

    spyOn(component, 'showSnackbar');

    component.form.patchValue({prompt: mockRequest.prompt});
    component.generateVideo();

    expect(apiServiceSpy.generateVideo).toHaveBeenCalledWith(mockRequest);
    expect(component.showSnackbar).toHaveBeenCalledWith(
      jasmine.any(String),
      SnackbarType.ERROR,
    );
    expect(component.isLoading).toBeFalse();
  });

  it('should display loading spinner while loading', () => {
    component.isLoading = true;
    fixture.detectChanges();
    const spinner = fixture.nativeElement.querySelector('mat-spinner');
    expect(spinner).toBeTruthy();
  });

  it('should trigger file selection on upload button click', () => {
    const uploadButton = fixture.debugElement.query(By.css('button[mat-fab]'));
    const fileInput = fixture.debugElement.query(
      By.css('input[type="file"]'),
    ).nativeElement;

    spyOn(fileInput, 'click');
    spyOn(component, 'onFileSelected');

    uploadButton.triggerEventHandler('click');
    expect(fileInput.click).toHaveBeenCalled();

    fileInput.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    expect(component.onFileSelected).toHaveBeenCalled();
  });

  it('should update form and preview with the base64 encoded image', () => {
    const mockFile = new File(['(mock image data)'], 'test-image.jpg', {
      type: 'image/jpeg',
    });
    const fileList = new DataTransfer();
    fileList.items.add(mockFile);
    const mockEvent = jasmine.createSpyObj('Event', ['preventDefault'], {
      target: {files: fileList.files},
    });

    const mockFileReader = jasmine.createSpyObj('FileReader', [
      'readAsDataURL',
      'onload',
    ]);
    spyOn(window, 'FileReader').and.returnValue(mockFileReader);

    component.onFileSelected(mockEvent);
    mockFileReader.onload({
      target: {result: 'data:image/jpeg;base64,(mock image data)'},
    } as ProgressEvent<FileReader>);

    expect(component.image).toEqual('data:image/jpeg;base64,(mock image data)');
    expect(component.form.get('image')?.value).toEqual(
      'data:image/jpeg;base64,(mock image data)',
    );
  });

  it('should remove preview and clear image form when removing an image', () => {
    component.image = 'test-image-data';
    component.form.get('image')?.setValue('test-image-data');
    fixture.detectChanges();

    const closeButton = fixture.debugElement.query(
      By.css('.veo-generate__close-button'),
    );
    closeButton.triggerEventHandler('click');

    expect(component.image).toBeUndefined();
    expect(component.form.get('image')?.value).toBeUndefined();
    expect(component.form.get('file')?.value).toBeUndefined();
  });

  it('should include prompt and image in API request', () => {
    mockRequest.image = 'test-image-data';
    component.image = 'test-image-data';

    apiServiceSpy.generateVideo.and.returnValue(of(mockResponse));
    component.form.patchValue({
      prompt: mockRequest.prompt,
      image: mockRequest.image,
    });

    component.generateVideo();
    expect(apiServiceSpy.generateVideo).toHaveBeenCalledWith(mockRequest);
  });

  it('should disable the image upload button when an image is present', () => {
    component.image = 'mock-image-data';
    fixture.detectChanges();

    const button = fixture.debugElement.query(By.css('button[mat-fab]'));

    expect(button).toBeNull();
  });
});
