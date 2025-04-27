import { HttpRequest, HttpHandlerFn, HttpInterceptorFn } from '@angular/common/http';

export const corsInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>, 
  next: HttpHandlerFn
) => {
  // Clone the request but don't add CORS headers as they're set by the server
  // The client shouldn't set CORS headers - that's the server's job
  // We'll just pass through the request without modification
  
  return next(request);
}; 