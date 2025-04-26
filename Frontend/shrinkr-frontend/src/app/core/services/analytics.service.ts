import { Injectable, inject, signal, PLATFORM_ID, Inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { DetailedAnalytics, AnalyticsExport } from '../models/analytics.model';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private readonly API_URL = `${environment.apiUrl}/analytics`;
  
  // Angular 17 signal-based state management
  private analyticsSignal = signal<Map<string, DetailedAnalytics>>(new Map<string, DetailedAnalytics>());
  private exportDataSignal = signal<Map<string, AnalyticsExport>>(new Map<string, AnalyticsExport>());
  private loadingSignal = signal<boolean>(false);
  private errorSignal = signal<any>(null);
  
  // Expose readonly signals
  readonly analytics = this.analyticsSignal.asReadonly();
  readonly exportData = this.exportDataSignal.asReadonly();
  readonly loading = this.loadingSignal.asReadonly();
  readonly error = this.errorSignal.asReadonly();
  
  private http = inject(HttpClient);
  
  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  getDetailedAnalytics(shortCode: string, days: number = 30): Observable<DetailedAnalytics> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    let params = new HttpParams().set('days', days.toString());

    return this.http.get<DetailedAnalytics>(`${this.API_URL}/urls/${shortCode}/detailed`, { params })
      .pipe(
        tap(analytics => {
          // Store the analytics for this URL
          const newMap = new Map(this.analyticsSignal());
          newMap.set(shortCode, analytics);
          this.analyticsSignal.set(newMap);
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error(`Error fetching analytics for ${shortCode}`, error);
          this.errorSignal.set(error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  exportAnalytics(shortCode: string, days: number = 30): Observable<AnalyticsExport> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    let params = new HttpParams().set('days', days.toString());

    return this.http.get<AnalyticsExport>(`${this.API_URL}/urls/${shortCode}/export`, { params })
      .pipe(
        tap(exportData => {
          // Store the export data for this URL
          const newMap = new Map(this.exportDataSignal());
          newMap.set(shortCode, exportData);
          this.exportDataSignal.set(newMap);
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error(`Error exporting analytics for ${shortCode}`, error);
          this.errorSignal.set(error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  downloadAnalyticsCSV(shortCode: string, days: number = 30): Observable<Blob> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    let params = new HttpParams().set('days', days.toString());

    return this.http.get(`${this.API_URL}/urls/${shortCode}/export`, { 
      params, 
      responseType: 'blob',
      headers: { 'Accept': 'text/csv' }
    }).pipe(
      tap(blob => {
        this.loadingSignal.set(false);
      }),
      catchError(error => {
        console.error(`Error downloading CSV for ${shortCode}`, error);
        this.errorSignal.set(error);
        this.loadingSignal.set(false);
        return throwError(() => error);
      })
    );
  }

  // Helper method to convert analytics data to CSV format on the client-side
  convertToCSV(data: any): string {
    const items = data.raw_clicks;
    if (!items || !items.length) {
      return '';
    }
    const header = Object.keys(items[0]).join(',');
    const csv = items.map((item: Record<string, unknown>) => {
      return Object.values(item).map((value: unknown) => {
        if (value === null || value === undefined) {
          return '';
        }
        // Handle string values that might contain commas
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value;
      }).join(',');
    });
    
    return [header, ...csv].join('\n');
  }

  // Helper method to save a blob as a file
  saveAsFile(blob: Blob, filename: string): void {
    if (isPlatformBrowser(this.platformId)) {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } else {
      console.warn('Cannot save file: not in browser context');
    }
  }
  
  // Helper method to get analytics for a specific URL
  getAnalyticsForUrl(shortCode: string): DetailedAnalytics | undefined {
    return this.analyticsSignal().get(shortCode);
  }
  
  // Helper method to get export data for a specific URL
  getExportDataForUrl(shortCode: string): AnalyticsExport | undefined {
    return this.exportDataSignal().get(shortCode);
  }
} 