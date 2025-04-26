import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { of } from 'rxjs';
import { catchError, map, switchMap } from 'rxjs/operators';
import { UrlService } from '../../../core/services/url.service';
import * as URLActions from './url.actions';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable()
export class URLEffects {
  private actions$ = inject(Actions);
  private urlService = inject(UrlService);
  private snackBar = inject(MatSnackBar);

  createUrl$ = createEffect(() =>
    this.actions$.pipe(
      ofType(URLActions.createUrl),
      switchMap(({ urlData }) =>
        this.urlService.createUrl(urlData).pipe(
          map(url => {
            this.snackBar.open('URL shortening successful!', 'Close', { duration: 3000 });
            return URLActions.createUrlSuccess({ url });
          }),
          catchError(error => of(URLActions.createUrlFailure({ error })))
        )
      )
    )
  );

  bulkCreateUrls$ = createEffect(() =>
    this.actions$.pipe(
      ofType(URLActions.bulkCreateUrls),
      switchMap(({ urlsData }) =>
        this.urlService.bulkCreateUrls(urlsData).pipe(
          map(response => {
            this.snackBar.open(`Created ${response.urls.length} URLs successfully!`, 'Close', { duration: 3000 });
            return URLActions.bulkCreateUrlsSuccess({ response });
          }),
          catchError(error => of(URLActions.bulkCreateUrlsFailure({ error })))
        )
      )
    )
  );

  loadUrls$ = createEffect(() =>
    this.actions$.pipe(
      ofType(URLActions.loadUrls),
      switchMap(({ skip, limit }) =>
        this.urlService.listUrls(skip, limit).pipe(
          map(urls => URLActions.loadUrlsSuccess({ urls })),
          catchError(error => of(URLActions.loadUrlsFailure({ error })))
        )
      )
    )
  );

  getUrlStats$ = createEffect(() =>
    this.actions$.pipe(
      ofType(URLActions.getUrlStats),
      switchMap(({ shortCode }) =>
        this.urlService.getUrlStats(shortCode).pipe(
          map(stats => URLActions.getUrlStatsSuccess({ stats })),
          catchError(error => of(URLActions.getUrlStatsFailure({ error })))
        )
      )
    )
  );

  updateUrl$ = createEffect(() =>
    this.actions$.pipe(
      ofType(URLActions.updateUrl),
      switchMap(({ shortCode, urlData }) =>
        this.urlService.updateUrl(shortCode, urlData).pipe(
          map(url => {
            this.snackBar.open('URL updated successfully!', 'Close', { duration: 3000 });
            return URLActions.updateUrlSuccess({ url });
          }),
          catchError(error => of(URLActions.updateUrlFailure({ error })))
        )
      )
    )
  );

  deleteUrl$ = createEffect(() =>
    this.actions$.pipe(
      ofType(URLActions.deleteUrl),
      switchMap(({ shortCode }) =>
        this.urlService.deleteUrl(shortCode).pipe(
          map(() => {
            this.snackBar.open('URL deleted successfully!', 'Close', { duration: 3000 });
            return URLActions.deleteUrlSuccess({ shortCode });
          }),
          catchError(error => of(URLActions.deleteUrlFailure({ error })))
        )
      )
    )
  );

  generateQrCode$ = createEffect(() =>
    this.actions$.pipe(
      ofType(URLActions.generateQrCode),
      switchMap(({ shortCode, size }) =>
        this.urlService.getQrCode(shortCode, size).pipe(
          map(qrBlob => URLActions.generateQrCodeSuccess({ shortCode, qrBlob })),
          catchError(error => of(URLActions.generateQrCodeFailure({ error })))
        )
      )
    )
  );
} 