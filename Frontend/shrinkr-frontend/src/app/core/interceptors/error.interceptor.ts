import { HttpRequest, HttpHandlerFn, HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>, 
  next: HttpHandlerFn
) => {
  const snackBar = inject(MatSnackBar);
  
  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'An error occurred';
      
      // Check for different error scenarios
      if (error.error instanceof ErrorEvent) {
        // Client-side error
        errorMessage = `Error: ${error.error.message}`;
      } else {
        // Server-side error
        if (error.status === 0) {
          errorMessage = 'Could not connect to the server. Please check your internet connection.';
        } else if (error.status === 401) {
          // We'll handle 401 in the auth interceptor
          return throwError(() => error);
        } else if (error.status === 403) {
          errorMessage = 'You do not have permission to perform this action';
        } else if (error.status === 404) {
          errorMessage = 'Resource not found';
        } else if (error.status === 429) {
          // Rate limiting error
          if (error.error && error.error.detail && typeof error.error.detail === 'object') {
            const detail = error.error.detail;
            errorMessage = `Rate limit exceeded. Please try again in ${detail.reset_in_seconds} seconds.`;
          } else {
            errorMessage = 'Rate limit exceeded. Please try again later.';
          }
        } else if (error.status >= 500) {
          errorMessage = 'A server error occurred. Please try again later.';
        } else if (error.error && error.error.detail) {
          // Try to get specific error message from the API
          errorMessage = typeof error.error.detail === 'string' 
            ? error.error.detail 
            : 'An error occurred';
        }
      }
      
      // Show the error message in a snackbar
      snackBar.open(errorMessage, 'Close', {
        duration: 5000,
        horizontalPosition: 'center',
        verticalPosition: 'bottom',
        panelClass: ['error-snackbar']
      });
      
      // Pass along the error for further processing
      return throwError(() => error);
    })
  );
};