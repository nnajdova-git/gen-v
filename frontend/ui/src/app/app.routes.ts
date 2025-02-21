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

import {Routes} from '@angular/router';
import {EditingPageComponent} from './pages/editing-page/editing-page.component';
import {GenerateVideoPageComponent} from './pages/generate-video-page/generate-video-page.component';
import {LandingPageComponent} from './pages/landing-page/landing-page.component';

/**
 * The application's routing configuration.
 *
 * This array defines the routes for the Gen V application, mapping URL paths
 * to specific components.
 */
export const routes: Routes = [
  {
    path: '',
    component: LandingPageComponent,
    pathMatch: 'full',
    title: 'Gen V | Ad Generation using Imagen & Veo',
    data: {topbarTitle: 'Gen V: Ad Generation using Imagen & Veo'},
  },
  {
    path: 'generate-videos',
    component: GenerateVideoPageComponent,
    title: 'Gen V | Generate Videos',
    data: {topbarTitle: 'Gen V: Generate Videos'},
  },
  {
    path: 'editing',
    component: EditingPageComponent,
    title: 'Gen V | Editing',
    data: {topbarTitle: 'Gen V: Editing - Turn videos and images into Ads'},
  },
];
