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

/**
 * @file The VeoGenerateComponent, which is responsible for providing the user
 * interface to interact with the video generation API.
 */

import {CommonModule} from '@angular/common';
import {Component} from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSnackBar, MatSnackBarModule} from '@angular/material/snack-bar';
import {
  GenerateVideoRequest,
  GenerateVideoResponse,
} from '../../models/api-models';
import {SnackbarType} from '../../models/material-design.enums';
import {ApiService} from '../../services/api.service';

/**
 * A component that allows users to generate videos via Veo.
 */
@Component({
  selector: 'app-veo-generate',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
  templateUrl: './veo-generate.component.html',
  styleUrls: ['./veo-generate.component.scss'],
})
export class VeoGenerateComponent {
  /**
   * Indicates whether a video generation request is in progress.
   */
  isLoading = false;
  /**
   * The form group for the video generation form.
   */
  form: FormGroup = new FormGroup({
    prompt: new FormControl('', [Validators.required]),
  });

  /**
   * @param apiService The service for making API requests.
   * @param snackBar The service for displaying snackbar notifications
   */
  constructor(
    private apiService: ApiService,
    private snackBar: MatSnackBar,
  ) {}

  /**
   * Shows Material Design snackbar notification.
   * @param message The message to display in the snackbar.
   * @param messageType The type of message to display in the snackbar.
   * @param duration The duration in milliseconds to display the snackbar.
   */
  showSnackbar(
    message: string,
    messageType: SnackbarType,
    duration = 5000,
  ) {
    this.snackBar.open(message, 'X', {
      duration,
      panelClass: [messageType],
    });
  }

  /**
   * Sends a request to generate a video.
   * Displays a snackbar notification with the result.
   */
  generateVideo() {
    if (this.form.invalid) {
      return;
    }
    this.isLoading = true;
    const request: GenerateVideoRequest = this.form.value;

    this.apiService.generateVideo(request).subscribe({
      next: (response: GenerateVideoResponse) => {
        this.showSnackbar(
          `Success: ${response.operation_name}`,
          SnackbarType.SUCCESS,
        );
      },
      error: (error) => {
        console.error('Error fetching data:', error);
        this.showSnackbar(`Error: ${error.message}`, SnackbarType.ERROR);
        this.isLoading = false;
      },
      complete: () => {
        this.isLoading = false;
      },
    });
  }
}
