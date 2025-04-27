import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTableModule } from '@angular/material/table';
import { FormsModule } from '@angular/forms';
import { AnalyticsService } from '../../core/services/analytics.service';
import { DetailedAnalytics } from '../../core/models/analytics.model';
import { finalize, catchError, of } from 'rxjs';
import { Clipboard } from '@angular/cdk/clipboard';
import { QrCodeComponent } from '../../shared/components/qr-code/qr-code.component';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-analytics-detail',
  templateUrl: './analytics-detail.component.html',
  styleUrl: './analytics-detail.component.scss',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatSelectModule,
    MatTooltipModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTableModule,
    FormsModule,
    QrCodeComponent
  ]
})
export class AnalyticsDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private analyticsService = inject(AnalyticsService);
  private snackBar = inject(MatSnackBar);
  private clipboard = inject(Clipboard);

  shortCode: string = '';
  analytics: DetailedAnalytics | null = null;
  isLoading = true;
  error: string | null = null;
  
  // Time range filter
  timeRanges = [
    { value: 7, label: 'Last 7 days' },
    { value: 14, label: 'Last 14 days' },
    { value: 30, label: 'Last 30 days' },
    { value: 60, label: 'Last 60 days' },
    { value: 90, label: 'Last 90 days' }
  ];
  selectedTimeRange = 30;

  ngOnInit(): void {
    this.shortCode = this.route.snapshot.paramMap.get('shortCode') || '';
    
    if (!this.shortCode) {
      this.router.navigate(['/dashboard']);
      return;
    }
    
    this.loadAnalytics();
  }

  loadAnalytics(): void {
    this.isLoading = true;
    this.error = null;
    
    this.analyticsService.getDetailedAnalytics(this.shortCode, this.selectedTimeRange)
      .pipe(
        catchError(err => {
          this.error = err.error?.detail || 'Failed to load analytics';
          return of(null);
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe(response => {
        if (response) {
          this.analytics = response;
        }
      });
  }

  onTimeRangeChange(): void {
    this.loadAnalytics();
  }

  exportAnalytics(): void {
    this.analyticsService.exportAnalytics(this.shortCode, this.selectedTimeRange)
      .pipe(
        catchError(err => {
          this.snackBar.open('Failed to export analytics', 'Close', {
            duration: 3000
          });
          return of(null);
        })
      )
      .subscribe(data => {
        if (data) {
          const dataStr = JSON.stringify(data, null, 2);
          const dataBlob = new Blob([dataStr], { type: 'application/json' });
          const filename = `analytics_${this.shortCode}_${new Date().toISOString().split('T')[0]}.json`;
          
          this.analyticsService.saveAsFile(dataBlob, filename);
          
          this.snackBar.open('Analytics exported successfully', 'Close', {
            duration: 3000
          });
        }
      });
  }

  exportCSV(): void {
    this.analyticsService.downloadAnalyticsCSV(this.shortCode, this.selectedTimeRange)
      .subscribe({
        next: (blob) => {
          const filename = `analytics_${this.shortCode}_${new Date().toISOString().split('T')[0]}.csv`;
          this.analyticsService.saveAsFile(blob, filename);
          
          this.snackBar.open('CSV exported successfully', 'Close', {
            duration: 3000
          });
        },
        error: (err) => {
          this.snackBar.open('Failed to export CSV', 'Close', {
            duration: 3000
          });
        }
      });
  }

  getFullShortUrl(): string {
    return `${environment.redirectBaseUrl}${this.shortCode}`;
  }

  copyToClipboard(text: string): void {
    this.clipboard.copy(text);
    this.snackBar.open('Copied to clipboard', 'Close', {
      duration: 2000
    });
  }

  retry(): void {
    this.loadAnalytics();
  }
}
