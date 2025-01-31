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
 * @file the topbar component for the application.
 */

import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {ActivatedRoute, NavigationEnd, Router} from '@angular/router';
import {filter, map, Subject, takeUntil} from 'rxjs';

/**
 * The topbar component.
 */
@Component({
  selector: 'app-topbar',
  imports: [],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.scss',
})
export class TopbarComponent implements OnInit, OnDestroy {
  /**
   * The page title to display in the topbar.
   */
  pageTitle = 'Gen V';
  /**
   * A Subject used to manage unsubscribing from Observables to prevent memory
   * leaks.
   */
  private destroy$ = new Subject<void>();
  /**
   * The activated route for the current page.
   */
  private route: ActivatedRoute;
  /**
   * The Angular Router service.
   */
  private router: Router;

  constructor() {
    this.route = inject(ActivatedRoute);
    this.router = inject(Router);
  }

  /**
   * Initialises the component & sets up the logic to display the correct title.
   */
  ngOnInit() {
    this.router.events
      .pipe(
        filter((event) => event instanceof NavigationEnd),
        map(() => {
          let currentRoute = this.route.root;
          while (currentRoute.firstChild) {
            currentRoute = currentRoute.firstChild;
          }
          return currentRoute.snapshot.data['topbarTitle'] || this.pageTitle;
        }),
        takeUntil(this.destroy$),
      )
      .subscribe((title) => {
        this.pageTitle = title;
      });
  }

  /**
   * Unsubscribes to prevent memory leaks
   */
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
