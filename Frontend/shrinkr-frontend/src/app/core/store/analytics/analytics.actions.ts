import { createAction, props } from '@ngrx/store';
import { DetailedAnalytics, AnalyticsExport } from '../../models/analytics.model';

// Get Detailed Analytics Actions
export const getDetailedAnalytics = createAction(
  '[Analytics] Get Detailed Analytics',
  props<{ shortCode: string; days?: number }>()
);

export const getDetailedAnalyticsSuccess = createAction(
  '[Analytics] Get Detailed Analytics Success',
  props<{ shortCode: string; analytics: DetailedAnalytics }>()
);

export const getDetailedAnalyticsFailure = createAction(
  '[Analytics] Get Detailed Analytics Failure',
  props<{ error: any }>()
);

// Export Analytics Actions
export const exportAnalytics = createAction(
  '[Analytics] Export Analytics',
  props<{ shortCode: string; days?: number }>()
);

export const exportAnalyticsSuccess = createAction(
  '[Analytics] Export Analytics Success',
  props<{ shortCode: string; exportData: AnalyticsExport }>()
);

export const exportAnalyticsFailure = createAction(
  '[Analytics] Export Analytics Failure',
  props<{ error: any }>()
);

// Download Analytics CSV Actions
export const downloadAnalyticsCSV = createAction(
  '[Analytics] Download Analytics CSV',
  props<{ shortCode: string; days?: number }>()
);

export const downloadAnalyticsCSVSuccess = createAction(
  '[Analytics] Download Analytics CSV Success',
  props<{ shortCode: string }>()
);

export const downloadAnalyticsCSVFailure = createAction(
  '[Analytics] Download Analytics CSV Failure',
  props<{ error: any }>()
); 