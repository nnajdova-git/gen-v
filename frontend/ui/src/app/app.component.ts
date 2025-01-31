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
import {Component} from '@angular/core';
import {MatSidenavModule} from '@angular/material/sidenav';
import {RouterOutlet} from '@angular/router';
import {SidenavComponent} from './components/shared/sidenav/sidenav.component';
import {TopbarComponent} from './components/shared/topbar/topbar.component';

/**
 * The root component of the Gen V application.
 * This component serves as the main container for the application's content and
 * provides the basic layout structure.
 */
@Component({
  selector: 'app-root',
  imports: [
    CommonModule,
    MatSidenavModule,
    RouterOutlet,
    SidenavComponent,
    TopbarComponent,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {}
