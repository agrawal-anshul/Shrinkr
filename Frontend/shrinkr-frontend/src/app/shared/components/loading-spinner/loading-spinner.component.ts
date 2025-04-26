import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule],
  template: `
    <div class="spinner-container" [class.overlay]="overlay" [class.inline]="!overlay">
      <mat-spinner [diameter]="diameter" [strokeWidth]="strokeWidth"></mat-spinner>
      @if (message) {
        <p class="spinner-message">{{ message }}</p>
      }
    </div>
  `,
  styles: `
    .spinner-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    
    .spinner-container.overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.3);
      z-index: 1000;
    }
    
    .spinner-container.inline {
      margin: 2rem 0;
    }
    
    .spinner-message {
      margin-top: 1rem;
      color: #333;
      font-weight: 500;
    }
    
    :host-context(.dark-theme) .spinner-message {
      color: #fff;
    }
  `
})
export class LoadingSpinnerComponent {
  @Input() diameter: number = 50;
  @Input() strokeWidth: number = 5;
  @Input() overlay: boolean = false;
  @Input() message: string = '';
} 