import { createReducer, on } from '@ngrx/store';
import { DetailedAnalytics, AnalyticsExport } from '../../models/analytics.model';
import * as AnalyticsActions from './analytics.actions';

export interface AnalyticsState {
  detailedAnalytics: Map<string, DetailedAnalytics>;
  exportData: Map<string, AnalyticsExport>;
  loading: boolean;
  error: any;
}

export const initialState: AnalyticsState = {
  detailedAnalytics: new Map<string, DetailedAnalytics>(),
  exportData: new Map<string, AnalyticsExport>(),
  loading: false,
  error: null
};

export const analyticsReducer = createReducer(
  initialState,
  
  // Get Detailed Analytics
  on(AnalyticsActions.getDetailedAnalytics, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(AnalyticsActions.getDetailedAnalyticsSuccess, (state, { shortCode, analytics }) => {
    const newDetailedAnalytics = new Map(state.detailedAnalytics);
    newDetailedAnalytics.set(shortCode, analytics);
    
    return {
      ...state,
      detailedAnalytics: newDetailedAnalytics,
      loading: false
    };
  }),
  on(AnalyticsActions.getDetailedAnalyticsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Export Analytics
  on(AnalyticsActions.exportAnalytics, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(AnalyticsActions.exportAnalyticsSuccess, (state, { shortCode, exportData }) => {
    const newExportData = new Map(state.exportData);
    newExportData.set(shortCode, exportData);
    
    return {
      ...state,
      exportData: newExportData,
      loading: false
    };
  }),
  on(AnalyticsActions.exportAnalyticsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Download Analytics CSV
  on(AnalyticsActions.downloadAnalyticsCSV, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(AnalyticsActions.downloadAnalyticsCSVSuccess, state => ({
    ...state,
    loading: false
  })),
  on(AnalyticsActions.downloadAnalyticsCSVFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  }))
); 