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
 * @file the Theme Toggle component: for switching between light and dark mode.
 */

import {DOCUMENT} from '@angular/common';
import {Component, inject, OnInit, Renderer2} from '@angular/core';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatTooltipModule} from '@angular/material/tooltip';

/**
 * Allows the user to toggle between light and dark mode.
 */
@Component({
  selector: 'app-theme-toggle',
  templateUrl: './theme-toggle.component.html',
  styleUrls: ['./theme-toggle.component.scss'],
  standalone: true,
  imports: [MatIconModule, MatButtonModule, MatTooltipModule],
})
export class ThemeToggleComponent implements OnInit {
  /**
   * Indicates whether the currently applied theme is dark mode (`true`) or
   * light mode (`false`).
   */
  isDarkMode = false;
  /**
   * A reference to the document object used for DOM manipulation.
   */
  private document;
  /**
   * A Renderer2 instance used for applying or removing classes to the document
   * body to change the theme.
   */
  private renderer;

  constructor() {
    this.document = inject(DOCUMENT);
    this.renderer = inject(Renderer2);
  }

  /**
   * Initializes the component and applies the saved theme from local storage,
   * or the default theme if no preference is found.
   */
  ngOnInit(): void {
    this.isDarkMode = localStorage.getItem('theme') === 'dark';
    this.applyTheme();
  }

  /**
   * Toggles the theme between dark and light mode.
   * Updates the `isDarkMode` flag, saves the preference to local storage, and
   * calls `applyTheme()` to update the UI.
   */
  toggleTheme(): void {
    this.isDarkMode = !this.isDarkMode;
    localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
    this.applyTheme();
  }

  /**
   * Applies the selected theme by adding or removing the `dark-mode` class
   * to the document body.
   */
  private applyTheme(): void {
    if (this.isDarkMode) {
      this.renderer.addClass(this.document.body, 'dark-mode');
    } else {
      this.renderer.removeClass(this.document.body, 'dark-mode');
    }
  }
}
