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
import {
  ComponentFixture,
  fakeAsync,
  TestBed,
  tick,
} from '@angular/core/testing';
import {provideRouter, Router, Routes} from '@angular/router';
import {TopbarComponent} from './topbar.component';

const testRoutes: Routes = [
  {
    path: '',
    component: TopbarComponent,
    data: {topbarTitle: 'Home Title'},
  },
  {
    path: 'generate-video',
    component: TopbarComponent,
    data: {topbarTitle: 'Generate Video Title'},
  },
];

describe('TopbarComponent', () => {
  let component: TopbarComponent;
  let fixture: ComponentFixture<TopbarComponent>;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TopbarComponent],
      providers: [provideRouter(testRoutes)],
    }).compileComponents();

    fixture = TestBed.createComponent(TopbarComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display the default title', () => {
    expect(component.pageTitle).toBe('Gen V');
  });

  it('should display the route title on navigation', fakeAsync(() => {
    router.navigate(['']);
    tick();
    fixture.detectChanges();
    expect(component.pageTitle).toBe('Home Title');

    router.navigate(['generate-video']);
    tick();
    fixture.detectChanges();
    expect(component.pageTitle).toBe('Generate Video Title');
  }));

  it('should unsubscribe on destroy', () => {
    const destroySpy = spyOn(component['destroy$'], 'next');
    fixture.destroy();
    expect(destroySpy).toHaveBeenCalled();
  });
});
