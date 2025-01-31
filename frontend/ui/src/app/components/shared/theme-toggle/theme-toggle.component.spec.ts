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
import {DOCUMENT} from '@angular/common';
import {Renderer2} from '@angular/core';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatTooltipModule} from '@angular/material/tooltip';
import {ThemeToggleComponent} from './theme-toggle.component';

describe('ThemeToggleComponent', () => {
  let component: ThemeToggleComponent;
  let fixture: ComponentFixture<ThemeToggleComponent>;
  let renderer: Renderer2;
  let document: Document;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ThemeToggleComponent,
        MatIconModule,
        MatButtonModule,
        MatTooltipModule,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ThemeToggleComponent);
    component = fixture.componentInstance;
    renderer = fixture.componentRef.injector.get(Renderer2);
    document = fixture.componentRef.injector.get(DOCUMENT);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should toggle theme and update local storage', () => {
    spyOn(localStorage, 'setItem').and.callThrough();
    spyOn(renderer, 'addClass').and.callThrough();
    spyOn(renderer, 'removeClass').and.callThrough();

    expect(component.isDarkMode).toBeFalse();
    expect(renderer.addClass).not.toHaveBeenCalled();
    expect(renderer.removeClass).not.toHaveBeenCalled();

    component.toggleTheme();
    expect(component.isDarkMode).toBeTrue();
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
    expect(renderer.addClass).toHaveBeenCalledWith(document.body, 'dark-mode');
    expect(renderer.removeClass).not.toHaveBeenCalledWith(
      document.body,
      'dark-mode',
    );

    component.toggleTheme();
    expect(component.isDarkMode).toBeFalse();
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
    expect(renderer.removeClass).toHaveBeenCalledWith(
      document.body,
      'dark-mode',
    );
  });

  it('should load theme from local storage on init', () => {
    spyOn(localStorage, 'getItem').and.returnValue('dark');
    spyOn(renderer, 'addClass').and.callThrough();

    fixture.detectChanges();

    expect(component.isDarkMode).toBeTrue();
    expect(localStorage.getItem).toHaveBeenCalledWith('theme');
    expect(renderer.addClass).toHaveBeenCalledWith(document.body, 'dark-mode');
  });
});
