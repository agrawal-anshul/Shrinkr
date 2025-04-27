import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { Store } from '@ngrx/store';
import * as URLActions from '../core/store/url/url.actions';
import * as fromUrl from '../core/store/url/url.selectors';
import { UrlService } from '../core/services/url.service';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatDividerModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  private store = inject(Store);
  private urlService = inject(UrlService);
  
  urls$ = this.store.select(fromUrl.selectAllUrls);
  loading$ = this.store.select(fromUrl.selectLoading);
  error$ = this.store.select(fromUrl.selectError);
  
  totalUrls = 0;
  totalClicks = 0;
  
  ngOnInit(): void {
    // Load user's URLs
    this.store.dispatch(URLActions.loadUrls({ skip: 0, limit: 10 }));
    
    // Subscribe to the URLs to calculate total clicks
    this.urls$.subscribe(urls => {
      if (urls && urls.length) {
        this.totalUrls = urls.length;
        this.totalClicks = urls.reduce((total, url) => total + (url.click_count || 0), 0);
      }
    });
  }
  
  getShortUrl(shortCode: string): string {
    return `${environment.redirectBaseUrl}${shortCode}`;
  }
  
  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text);
  }
}
