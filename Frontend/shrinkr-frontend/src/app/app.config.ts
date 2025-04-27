import { ApplicationConfig, isDevMode } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideStore } from '@ngrx/store';
import { provideEffects } from '@ngrx/effects';
import { provideStoreDevtools } from '@ngrx/store-devtools';
import { isPlatformBrowser } from '@angular/common';
import { Inject, PLATFORM_ID } from '@angular/core';

import { routes } from './app.routes';
import { reducers, metaReducers } from './core/store';
import { AuthEffects } from './core/store/auth/auth.effects';
import { URLEffects } from './core/store/url/url.effects';
import { AnalyticsEffects } from './core/store/analytics/analytics.effects';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { errorInterceptor } from './core/interceptors/error.interceptor';
import { corsInterceptor } from './core/interceptors/cors.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(
      withInterceptors([corsInterceptor, authInterceptor, errorInterceptor])
    ),
    provideAnimations(),
    provideStore(reducers, { metaReducers }),
    provideEffects([AuthEffects, URLEffects, AnalyticsEffects]),
    provideStoreDevtools({
      maxAge: 25,
      logOnly: !isDevMode(),
      autoPause: true,
      trace: false,
      traceLimit: 75
    }),
    { provide: PLATFORM_ID, useValue: 'browser' }
  ]
};
