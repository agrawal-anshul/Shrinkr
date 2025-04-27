import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { UrlService } from '../../core/services/url.service';
import { tap, catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-create-url-dialog',
  templateUrl: './create-url-dialog.component.html',
  styleUrls: ['./create-url-dialog.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    FormsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule
  ]
})
export class CreateUrlDialogComponent {
  originalUrl: string = '';
  isSubmitting: boolean = false;
  
  constructor(
    private dialogRef: MatDialogRef<CreateUrlDialogComponent>,
    private urlService: UrlService,
    private snackBar: MatSnackBar
  ) {}
  
  createUrl(): void {
    if (!this.originalUrl) {
      return;
    }
    
    this.isSubmitting = true;
    this.urlService.createUrl({
      original_url: this.originalUrl
    }).pipe(
      tap(response => {
        this.isSubmitting = false;
        this.dialogRef.close(response);
      }),
      catchError(error => {
        this.isSubmitting = false;
        this.snackBar.open(error.error?.detail || 'Failed to create URL', 'Close', {
          duration: 3000
        });
        return of(null);
      })
    ).subscribe();
  }
  
  cancel(): void {
    this.dialogRef.close();
  }
}