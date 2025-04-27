import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { Store } from '@ngrx/store';
import * as URLActions from '../../core/store/url/url.actions';
import * as fromUrl from '../../core/store/url/url.selectors';

@Component({
  selector: 'app-create-url',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatSlideToggleModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './create-url.component.html',
  styleUrls: ['./create-url.component.scss']
})
export class CreateUrlComponent {
  private fb = inject(FormBuilder);
  private store = inject(Store);
  private snackBar = inject(MatSnackBar);
  
  loading$ = this.store.select(fromUrl.selectLoading);
  error$ = this.store.select(fromUrl.selectError);
  
  urlForm: FormGroup = this.fb.group({
    original_url: ['', [Validators.required, Validators.pattern('https?://.*')]],
    custom_short_code: [''],
    expires_at: [null],
    is_private: [false]
  });
  
  useCustomCode = false;
  
  toggleCustomCode(): void {
    this.useCustomCode = !this.useCustomCode;
    if (!this.useCustomCode) {
      this.urlForm.get('custom_short_code')?.setValue('');
    }
  }
  
  onSubmit(): void {
    if (this.urlForm.valid) {
      const urlData = {
        original_url: this.urlForm.value.original_url,
        custom_short_code: this.urlForm.value.custom_short_code || undefined,
        expires_at: this.urlForm.value.expires_at ? new Date(this.urlForm.value.expires_at).toISOString() : undefined,
        is_private: this.urlForm.value.is_private
      };
      
      this.store.dispatch(URLActions.createUrl({ urlData }));
    } else {
      this.snackBar.open('Please fix the errors in the form', 'Close', {
        duration: 3000
      });
    }
  }
}
