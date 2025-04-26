import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoadingSpinnerComponent } from './components/loading-spinner/loading-spinner.component';
import { ConfirmDialogComponent } from './components/confirm-dialog/confirm-dialog.component';
import { DialogService } from './services/dialog.service';
import { ToastService } from './components/toast/toast.service';

/**
 * Shared module containing common components, directives, and pipes
 */
@NgModule({
  imports: [
    CommonModule,
    LoadingSpinnerComponent,
    ConfirmDialogComponent
  ],
  exports: [
    // Components
    LoadingSpinnerComponent,
    ConfirmDialogComponent
  ],
  providers: [
    DialogService,
    ToastService
  ]
})
export class SharedModule { } 