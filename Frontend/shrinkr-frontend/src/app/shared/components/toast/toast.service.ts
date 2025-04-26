import { Injectable } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';

export enum ToastType {
  SUCCESS = 'success',
  ERROR = 'error',
  INFO = 'info',
  WARNING = 'warning'
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private defaultDuration = 3000; // in ms

  constructor(private snackBar: MatSnackBar) {}

  /**
   * Show a success toast message
   * @param message The message to display
   * @param duration Optional duration in ms
   */
  success(message: string, duration?: number): void {
    this.show(message, ToastType.SUCCESS, duration);
  }

  /**
   * Show an error toast message
   * @param message The message to display
   * @param duration Optional duration in ms
   */
  error(message: string, duration?: number): void {
    this.show(message, ToastType.ERROR, duration);
  }

  /**
   * Show an info toast message
   * @param message The message to display
   * @param duration Optional duration in ms
   */
  info(message: string, duration?: number): void {
    this.show(message, ToastType.INFO, duration);
  }

  /**
   * Show a warning toast message
   * @param message The message to display
   * @param duration Optional duration in ms
   */
  warning(message: string, duration?: number): void {
    this.show(message, ToastType.WARNING, duration);
  }

  /**
   * Show a toast message with the specified type
   * @param message The message to display
   * @param type The type of toast
   * @param duration Optional duration in ms
   */
  private show(message: string, type: ToastType, duration?: number): void {
    const config: MatSnackBarConfig = {
      duration: duration || this.defaultDuration,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
      panelClass: [`${type}-snackbar`]
    };

    this.snackBar.open(message, 'Close', config);
  }
} 