import { Injectable, inject, signal, PLATFORM_ID, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { User, UserCreate, TokenResponse } from '../models/user.model';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = `${environment.apiUrl}/auth`;
  private readonly TOKEN_KEY = 'shrinkr_token';
  private readonly USER_KEY = 'shrinkr_user';
  
  // Angular 17 signal-based state management
  private currentUserSignal = signal<User | null>(null);
  private isAuthenticatedSignal = signal<boolean>(false);
  private loadingSignal = signal<boolean>(false);
  
  // Expose readonly signals
  readonly currentUser = this.currentUserSignal.asReadonly();
  readonly isAuthenticated = this.isAuthenticatedSignal.asReadonly();
  readonly loading = this.loadingSignal.asReadonly();
  
  private http = inject(HttpClient);
  
  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    this.loadUserFromStorage();
  }

  private loadUserFromStorage(): void {
    if (isPlatformBrowser(this.platformId)) {
      const token = localStorage.getItem(this.TOKEN_KEY);
      const user = localStorage.getItem(this.USER_KEY);
      
      if (token && user) {
        this.currentUserSignal.set(JSON.parse(user));
        this.isAuthenticatedSignal.set(true);
      }
    }
  }

  register(userData: UserCreate): Observable<TokenResponse> {
    this.loadingSignal.set(true);
    return this.http.post<TokenResponse>(`${this.API_URL}/register`, userData)
      .pipe(
        tap(response => this.handleAuthentication(response)),
        catchError(error => {
          console.error('Registration failed', error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  login(email: string, password: string): Observable<TokenResponse> {
    this.loadingSignal.set(true);
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    return this.http.post<TokenResponse>(`${this.API_URL}/login`, formData)
      .pipe(
        tap(response => this.handleAuthentication(response)),
        catchError(error => {
          console.error('Login failed', error);
          this.loadingSignal.set(false);
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem(this.TOKEN_KEY);
      localStorage.removeItem(this.USER_KEY);
    }
    this.currentUserSignal.set(null);
    this.isAuthenticatedSignal.set(false);
  }

  getToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem(this.TOKEN_KEY);
    }
    return null;
  }

  getUserProfile(): Observable<User> {
    this.loadingSignal.set(true);
    return this.http.get<User>(`${this.API_URL}/me`)
      .pipe(
        tap(user => {
          if (isPlatformBrowser(this.platformId)) {
            localStorage.setItem(this.USER_KEY, JSON.stringify(user));
          }
          this.currentUserSignal.set(user);
          this.loadingSignal.set(false);
        }),
        catchError(error => {
          console.error('Error fetching user profile', error);
          this.loadingSignal.set(false);
          // If 401, logout
          if (error.status === 401) {
            this.logout();
          }
          return throwError(() => error);
        })
      );
  }

  private handleAuthentication(response: TokenResponse): void {
    if (response && response.access_token) {
      if (isPlatformBrowser(this.platformId)) {
        localStorage.setItem(this.TOKEN_KEY, response.access_token);
      }
      this.isAuthenticatedSignal.set(true);
      
      // Fetch user details after successful authentication
      this.getUserProfile().subscribe();
    }
    this.loadingSignal.set(false);
  }

  isLoggedIn(): boolean {
    return this.isAuthenticatedSignal();
  }
} 