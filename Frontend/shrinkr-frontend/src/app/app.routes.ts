import { Routes } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from './core/services/auth.service';
import { map } from 'rxjs/operators';

// Auth guard function
const authGuard = () => {
  const authService = inject(AuthService);
  return authService.isLoggedIn() ? true : { path: '/login' };
};

// Non-auth guard function (for login/register pages)
const nonAuthGuard = () => {
  const authService = inject(AuthService);
  return !authService.isLoggedIn() ? true : { path: '/dashboard' };
};

export const routes: Routes = [
  { 
    path: '', 
    loadComponent: () => import('./home/home.component').then(m => m.HomeComponent) 
  },
  { 
    path: 'login', 
    loadComponent: () => import('./auth/login/login.component').then(m => m.LoginComponent),
    canActivate: [nonAuthGuard]
  },
  { 
    path: 'register', 
    loadComponent: () => import('./auth/register/register.component').then(m => m.RegisterComponent),
    canActivate: [nonAuthGuard]
  },
  { 
    path: 'dashboard', 
    loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  { 
    path: 'urls/create', 
    loadComponent: () => import('./urls/create-url/create-url.component').then(m => m.CreateUrlComponent),
    canActivate: [authGuard]
  },
  { 
    path: 'urls', 
    loadComponent: () => import('./urls/url-list/url-list.component').then(m => m.UrlListComponent),
    canActivate: [authGuard]
  },
  { 
    path: 'analytics/:shortCode', 
    loadComponent: () => import('./analytics/analytics-detail/analytics-detail.component').then(m => m.AnalyticsDetailComponent),
    canActivate: [authGuard]
  },
  // Fallback route
  { 
    path: '**', 
    redirectTo: '' 
  }
];
