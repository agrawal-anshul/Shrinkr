import { ActionReducerMap, MetaReducer } from '@ngrx/store';
import { environment } from '../../../../src/environments/environment';

import * as fromAuth from './auth/auth.reducer';
import * as fromUrl from './url/url.reducer';
import * as fromAnalytics from './analytics/analytics.reducer';

export interface AppState {
  auth: fromAuth.AuthState;
  url: fromUrl.URLState;
  analytics: fromAnalytics.AnalyticsState;
}

export const reducers: ActionReducerMap<AppState> = {
  auth: fromAuth.authReducer,
  url: fromUrl.urlReducer,
  analytics: fromAnalytics.analyticsReducer
};

export const metaReducers: MetaReducer<AppState>[] = !environment.production ? [] : []; 