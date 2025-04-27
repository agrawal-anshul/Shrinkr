import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PageEvent } from '@angular/material/paginator';
import { UrlService } from '../../core/services/url.service';
import { CreateUrlDialogComponent } from '../create-url-dialog/create-url-dialog.component';
import { ConfirmDialogComponent } from '../../shared/components/confirm-dialog/confirm-dialog.component';
import { Clipboard } from '@angular/cdk/clipboard';
import { catchError, finalize, tap } from 'rxjs/operators';
import { of } from 'rxjs';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { environment } from '../../../environments/environment';

interface UrlData {
  id: string;
  shortUrl: string;
  originalUrl: string;
  clicks: number;
  createdAt: Date;
}

@Component({
  selector: 'app-url-list',
  templateUrl: './url-list.component.html',
  styleUrls: ['./url-list.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatTableModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule
  ]
})
export class UrlListComponent implements OnInit {
  displayedColumns: string[] = ['shortUrl', 'originalUrl', 'clicks', 'createdAt', 'actions'];
  dataSource: UrlData[] = [];
  isLoading = true;
  error: string | null = null;
  
  // Pagination
  totalItems = 0;
  pageSize = 10;
  pageSizeOptions = [5, 10, 25, 50];
  currentPage = 0;

  constructor(
    private urlService: UrlService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private clipboard: Clipboard
  ) {}

  ngOnInit(): void {
    this.loadUrls();
  }

  loadUrls(): void {
    this.isLoading = true;
    this.error = null;

    this.urlService.listUrls(this.currentPage * this.pageSize, this.pageSize)
      .pipe(
        tap(urls => {
          this.dataSource = urls.map(url => ({
            id: url.short_code,
            shortUrl: url.short_code,
            originalUrl: url.original_url,
            clicks: url.click_count || 0,
            createdAt: new Date(url.created_at)
          }));
          this.totalItems = urls.length;
        }),
        catchError(err => {
          this.error = err.message || 'Failed to load URLs';
          return of(null);
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe();
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(CreateUrlDialogComponent, {
      width: '500px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadUrls();
      }
    });
  }

  onPageChange(event: PageEvent): void {
    this.pageSize = event.pageSize;
    this.currentPage = event.pageIndex;
    this.loadUrls();
  }

  copyToClipboard(url: string): void {
    const fullUrl = this.getFullShortUrl(url);
    this.clipboard.copy(fullUrl);
    this.snackBar.open('URL copied to clipboard', 'Close', {
      duration: 3000
    });
  }

  deleteUrl(id: string): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete URL',
        message: 'Are you sure you want to delete this shortened URL? This action cannot be undone.',
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.urlService.deleteUrl(id)
          .pipe(
            tap(() => {
              this.loadUrls();
              this.snackBar.open('URL deleted successfully', 'Close', {
                duration: 3000
              });
            }),
            catchError(err => {
              this.snackBar.open(err.message || 'Failed to delete URL', 'Close', {
                duration: 5000
              });
              return of(null);
            })
          )
          .subscribe();
      }
    });
  }

  getFullShortUrl(shortUrl: string): string {
    return `${environment.redirectBaseUrl}${shortUrl}`;
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  retry(): void {
    this.loadUrls();
  }
}
