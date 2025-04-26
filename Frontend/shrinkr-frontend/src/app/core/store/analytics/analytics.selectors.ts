import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AnalyticsState } from './analytics.reducer';

export const selectAnalyticsState = createFeatureSelector<AnalyticsState>('analytics');

export const selectAnalyticsLoading = createSelector(
  selectAnalyticsState,
  (state: AnalyticsState) => state.loading
);

export const selectAnalyticsError = createSelector(
  selectAnalyticsState,
  (state: AnalyticsState) => state.error
);

export const selectDetailedAnalyticsByShortCode = (shortCode: string) => createSelector(
  selectAnalyticsState,
  (state: AnalyticsState) => state.detailedAnalytics.get(shortCode) || null
);

export const selectExportDataByShortCode = (shortCode: string) => createSelector(
  selectAnalyticsState,
  (state: AnalyticsState) => state.exportData.get(shortCode) || null
); 