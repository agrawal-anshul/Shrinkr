import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { of } from 'rxjs';
import { catchError, map, switchMap, tap } from 'rxjs/operators';
import { AnalyticsService } from '../../../core/services/analytics.service';
import * as AnalyticsActions from './analytics.actions';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable()
export class AnalyticsEffects {
  private actions$ = inject(Actions);
  private analyticsService = inject(AnalyticsService);
  private snackBar = inject(MatSnackBar);

  getDetailedAnalytics$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AnalyticsActions.getDetailedAnalytics),
      switchMap(({ shortCode, days }) =>
        this.analyticsService.getDetailedAnalytics(shortCode, days).pipe(
          map(analytics => AnalyticsActions.getDetailedAnalyticsSuccess({ shortCode, analytics })),
          catchError(error => of(AnalyticsActions.getDetailedAnalyticsFailure({ error })))
        )
      )
    )
  );

  exportAnalytics$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AnalyticsActions.exportAnalytics),
      switchMap(({ shortCode, days }) =>
        this.analyticsService.exportAnalytics(shortCode, days).pipe(
          map(exportData => AnalyticsActions.exportAnalyticsSuccess({ shortCode, exportData })),
          catchError(error => of(AnalyticsActions.exportAnalyticsFailure({ error })))
        )
      )
    )
  );

  downloadAnalyticsCSV$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AnalyticsActions.downloadAnalyticsCSV),
      switchMap(({ shortCode, days }) =>
        this.analyticsService.exportAnalytics(shortCode, days).pipe(
          tap(exportData => {
            // Generate CSV from the export data
            const csv = this.analyticsService.convertToCSV(exportData);
            
            // Create a Blob from the CSV data
            const blob = new Blob([csv], { type: 'text/csv' });
            
            // Save the file
            this.analyticsService.saveAsFile(blob, `analytics_${shortCode}_${new Date().toISOString().split('T')[0]}.csv`);
            
            this.snackBar.open('Analytics CSV downloaded successfully!', 'Close', { duration: 3000 });
          }),
          map(() => AnalyticsActions.downloadAnalyticsCSVSuccess({ shortCode })),
          catchError(error => of(AnalyticsActions.downloadAnalyticsCSVFailure({ error })))
        )
      )
    )
  );
} 