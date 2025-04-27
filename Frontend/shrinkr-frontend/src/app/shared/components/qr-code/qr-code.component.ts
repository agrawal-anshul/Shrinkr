import { Component, Input, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
import { UrlService } from '../../../core/services/url.service';
import { catchError, of } from 'rxjs';

@Component({
  selector: 'app-qr-code',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatSelectModule,
    FormsModule
  ],
  templateUrl: './qr-code.component.html',
  styleUrl: './qr-code.component.scss'
})
export class QrCodeComponent implements OnInit {
  @Input() shortCode: string = '';
  
  private urlService = inject(UrlService);
  private snackBar = inject(MatSnackBar);
  
  isLoading = false;
  error: string | null = null;
  qrCodeUrl: string | null = null;
  
  sizes = [
    { value: 5, label: 'Small' },
    { value: 10, label: 'Medium' },
    { value: 15, label: 'Large' }
  ];
  selectedSize = 10;
  
  ngOnInit(): void {
    if (this.shortCode) {
      this.generateQrCode();
    }
  }
  
  generateQrCode(): void {
    if (!this.shortCode) return;
    
    this.isLoading = true;
    this.error = null;
    
    this.urlService.getQrCode(this.shortCode, this.selectedSize)
      .pipe(
        catchError(err => {
          this.error = 'Failed to generate QR code';
          this.isLoading = false;
          return of(null);
        })
      )
      .subscribe(blob => {
        this.isLoading = false;
        
        if (blob) {
          this.qrCodeUrl = URL.createObjectURL(blob);
        }
      });
  }
  
  onSizeChange(): void {
    this.generateQrCode();
  }
  
  downloadQrCode(): void {
    if (!this.qrCodeUrl) return;
    
    const a = document.createElement('a');
    a.href = this.qrCodeUrl;
    a.download = `qrcode-${this.shortCode}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    this.snackBar.open('QR code downloaded', 'Close', {
      duration: 3000
    });
  }
} 