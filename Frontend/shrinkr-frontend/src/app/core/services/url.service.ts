import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { 
  URLCreate, 
  URLResponse, 
  URLUpdate, 
  BulkURLCreate, 
  BulkURLResponse 
} from '../models/url.model';

@Injectable({
  providedIn: 'root'
})
export class UrlService {
  private readonly API_URL = `${environment.apiUrl}/urls`;
  
  // Angular 17 signal-based state management
  private urlsSignal = signal<URLResponse[]>([]);
  private selectedUrlStatsSignal = signal<any | null>(null);
  private loadingSignal = signal<boolean>(false);
  private errorSignal = signal<any>(null);
  
  // QR code blob storage
  private qrCodesSignal = signal<Map<string, Blob>>(new Map<string, Blob>());
  
  // Expose readonly signals
  readonly urls = this.urlsSignal.asReadonly();
  readonly selectedUrlStats = this.selectedUrlStatsSignal.asReadonly();
  readonly loading = this.loadingSignal.asReadonly();
  readonly error = this.errorSignal.asReadonly();
  readonly qrCodes = this.qrCodesSignal.asReadonly();
  
  private http = inject(HttpClient);

  createUrl(urlData: URLCreate): Observable<URLResponse> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    return this.http.post<URLResponse>(`${this.API_URL}/create`, urlData)
      .pipe(
        tap(url => {
          // Add the new URL to the list
          this.urlsSignal.update(urls => [url, ...urls]);
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error('Error creating URL', error);
          this.errorSignal.set(error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  bulkCreateUrls(urlsData: BulkURLCreate): Observable<BulkURLResponse> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    return this.http.post<BulkURLResponse>(`${this.API_URL}/bulk-create`, urlsData)
      .pipe(
        tap(response => {
          // Add the new URLs to the list
          this.urlsSignal.update(urls => [...response.urls, ...urls]);
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error('Error bulk creating URLs', error);
          this.errorSignal.set(error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  listUrls(skip: number = 0, limit: number = 100): Observable<URLResponse[]> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    return this.http.get<URLResponse[]>(`${this.API_URL}/list`, { params })
      .pipe(
        tap(urls => {
          this.urlsSignal.set(urls);
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error('Error listing URLs', error);
          this.errorSignal.set(error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  getUrlStats(shortCode: string): Observable<any> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    return this.http.get<any>(`${this.API_URL}/${shortCode}/stats`)
      .pipe(
        tap(stats => {
          this.selectedUrlStatsSignal.set(stats);
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error(`Error fetching stats for ${shortCode}`, error);
          this.errorSignal.set(error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  updateUrl(shortCode: string, urlData: URLUpdate): Observable<URLResponse> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    return this.http.patch<URLResponse>(`${this.API_URL}/${shortCode}`, urlData)
      .pipe(
        tap(updatedUrl => {
          // Update the URL in the list
          this.urlsSignal.update(urls => 
            urls.map(url => url.short_code === shortCode ? updatedUrl : url)
          );
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error(`Error updating URL ${shortCode}`, error);
          this.errorSignal.set(error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  deleteUrl(shortCode: string): Observable<any> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    return this.http.delete<any>(`${this.API_URL}/${shortCode}`)
      .pipe(
        tap(() => {
          // Remove the URL from the list
          this.urlsSignal.update(urls => 
            urls.filter(url => url.short_code !== shortCode)
          );
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error(`Error deleting URL ${shortCode}`, error);
          this.errorSignal.set(error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  getQrCode(shortCode: string, size: number = 10): Observable<Blob> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);
    
    let params = new HttpParams().set('size', size.toString());
    
    return this.http.get(`${this.API_URL}/${shortCode}/qr`, { 
      params, 
      responseType: 'blob' 
    }).pipe(
      tap(blob => {
        // Store the QR code blob
        const newMap = new Map(this.qrCodesSignal());
        newMap.set(shortCode, blob);
        this.qrCodesSignal.set(newMap);
        this.loadingSignal.set(false);
      }),
      catchError(error => {
        console.error(`Error generating QR code for ${shortCode}`, error);
        this.errorSignal.set(error);
        this.loadingSignal.set(false);
        return throwError(() => error);
      })
    );
  }

  getFullShortenedUrl(shortCode: string): string {
    // Use window.location to get the base URL or use environment config
    const baseUrl = environment.redirectBaseUrl || `${window.location.protocol}//${window.location.host}/redirect/`;
    return `${baseUrl}${shortCode}`;
  }
  
  // Helper method to find a URL by short code
  getUrlByShortCode(shortCode: string): URLResponse | undefined {
    return this.urlsSignal().find(url => url.short_code === shortCode);
  }
  
  // Helper method to get a QR code URL for a short code
  getQrCodeUrl(shortCode: string): string | null {
    const qrBlob = this.qrCodesSignal().get(shortCode);
    if (qrBlob) {
      return URL.createObjectURL(qrBlob);
    }
    return null;
  }
} 