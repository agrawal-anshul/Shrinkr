import { createFeatureSelector, createSelector } from '@ngrx/store';
import { URLState, selectAll, selectEntities } from './url.reducer';

export const selectUrlState = createFeatureSelector<URLState>('url');

export const selectAllUrls = createSelector(
  selectUrlState,
  selectAll
);

export const selectUrlEntities = createSelector(
  selectUrlState,
  selectEntities
);

export const selectUrlLoading = createSelector(
  selectUrlState,
  (state: URLState) => state.loading
);

export const selectUrlError = createSelector(
  selectUrlState,
  (state: URLState) => state.error
);

export const selectSelectedUrlStats = createSelector(
  selectUrlState,
  (state: URLState) => state.selectedUrlStats
);

export const selectUrlByShortCode = (shortCode: string) => createSelector(
  selectAllUrls,
  (urls) => urls.find(url => url.short_code === shortCode)
);

export const selectQrCodeForUrl = (shortCode: string) => createSelector(
  selectUrlState,
  (state: URLState) => state.selectedUrlQrCode?.get(shortCode) || null
);

export const selectTotalUrls = createSelector(
  selectAllUrls,
  (urls) => urls.length
);

export const selectTotalClicks = createSelector(
  selectAllUrls,
  (urls) => urls.reduce((total, url) => total + url.click_count, 0)
); 