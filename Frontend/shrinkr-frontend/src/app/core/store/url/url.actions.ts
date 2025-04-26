import { createAction, props } from '@ngrx/store';
import { URLCreate, URLResponse, URLUpdate, BulkURLCreate, BulkURLResponse } from '../../models/url.model';

// Create URL Actions
export const createUrl = createAction(
  '[URL] Create URL',
  props<{ urlData: URLCreate }>()
);

export const createUrlSuccess = createAction(
  '[URL] Create URL Success',
  props<{ url: URLResponse }>()
);

export const createUrlFailure = createAction(
  '[URL] Create URL Failure',
  props<{ error: any }>()
);

// Bulk Create URLs Actions
export const bulkCreateUrls = createAction(
  '[URL] Bulk Create URLs',
  props<{ urlsData: BulkURLCreate }>()
);

export const bulkCreateUrlsSuccess = createAction(
  '[URL] Bulk Create URLs Success',
  props<{ response: BulkURLResponse }>()
);

export const bulkCreateUrlsFailure = createAction(
  '[URL] Bulk Create URLs Failure',
  props<{ error: any }>()
);

// Load URLs Actions
export const loadUrls = createAction(
  '[URL] Load URLs',
  props<{ skip?: number; limit?: number }>()
);

export const loadUrlsSuccess = createAction(
  '[URL] Load URLs Success',
  props<{ urls: URLResponse[] }>()
);

export const loadUrlsFailure = createAction(
  '[URL] Load URLs Failure',
  props<{ error: any }>()
);

// Get URL Stats Actions
export const getUrlStats = createAction(
  '[URL] Get URL Stats',
  props<{ shortCode: string }>()
);

export const getUrlStatsSuccess = createAction(
  '[URL] Get URL Stats Success',
  props<{ stats: any }>()
);

export const getUrlStatsFailure = createAction(
  '[URL] Get URL Stats Failure',
  props<{ error: any }>()
);

// Update URL Actions
export const updateUrl = createAction(
  '[URL] Update URL',
  props<{ shortCode: string; urlData: URLUpdate }>()
);

export const updateUrlSuccess = createAction(
  '[URL] Update URL Success',
  props<{ url: URLResponse }>()
);

export const updateUrlFailure = createAction(
  '[URL] Update URL Failure',
  props<{ error: any }>()
);

// Delete URL Actions
export const deleteUrl = createAction(
  '[URL] Delete URL',
  props<{ shortCode: string }>()
);

export const deleteUrlSuccess = createAction(
  '[URL] Delete URL Success',
  props<{ shortCode: string }>()
);

export const deleteUrlFailure = createAction(
  '[URL] Delete URL Failure',
  props<{ error: any }>()
);

// Generate QR Code Actions
export const generateQrCode = createAction(
  '[URL] Generate QR Code',
  props<{ shortCode: string; size?: number }>()
);

export const generateQrCodeSuccess = createAction(
  '[URL] Generate QR Code Success',
  props<{ shortCode: string; qrBlob: Blob }>()
);

export const generateQrCodeFailure = createAction(
  '[URL] Generate QR Code Failure',
  props<{ error: any }>()
); 