import { createReducer, on } from '@ngrx/store';
import { createEntityAdapter, EntityAdapter, EntityState } from '@ngrx/entity';
import { URLResponse } from '../../models/url.model';
import * as URLActions from './url.actions';

export interface URLState extends EntityState<URLResponse> {
  loading: boolean;
  error: any;
  selectedUrlStats: any | null;
  selectedUrlQrCode: Map<string, Blob> | null;
}

export const urlAdapter: EntityAdapter<URLResponse> = createEntityAdapter<URLResponse>({
  selectId: (url: URLResponse) => url.id,
  sortComparer: (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
});

export const initialState: URLState = urlAdapter.getInitialState({
  loading: false,
  error: null,
  selectedUrlStats: null,
  selectedUrlQrCode: new Map<string, Blob>()
});

export const urlReducer = createReducer(
  initialState,

  // Create URL
  on(URLActions.createUrl, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(URLActions.createUrlSuccess, (state, { url }) => 
    urlAdapter.addOne(url, {
      ...state,
      loading: false
    })
  ),
  on(URLActions.createUrlFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Bulk Create URLs
  on(URLActions.bulkCreateUrls, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(URLActions.bulkCreateUrlsSuccess, (state, { response }) =>
    urlAdapter.addMany(response.urls, {
      ...state,
      loading: false
    })
  ),
  on(URLActions.bulkCreateUrlsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Load URLs
  on(URLActions.loadUrls, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(URLActions.loadUrlsSuccess, (state, { urls }) =>
    urlAdapter.setAll(urls, {
      ...state,
      loading: false
    })
  ),
  on(URLActions.loadUrlsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Get URL Stats
  on(URLActions.getUrlStats, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(URLActions.getUrlStatsSuccess, (state, { stats }) => ({
    ...state,
    selectedUrlStats: stats,
    loading: false
  })),
  on(URLActions.getUrlStatsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Update URL
  on(URLActions.updateUrl, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(URLActions.updateUrlSuccess, (state, { url }) =>
    urlAdapter.updateOne(
      { id: url.id, changes: url },
      {
        ...state,
        loading: false
      }
    )
  ),
  on(URLActions.updateUrlFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Delete URL
  on(URLActions.deleteUrl, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(URLActions.deleteUrlSuccess, (state, { shortCode }) => {
    // Find the URL entity with the matching short_code
    const urlToDelete = Object.values(state.entities)
      .find(url => url?.short_code === shortCode);
    
    if (urlToDelete) {
      return urlAdapter.removeOne(urlToDelete.id, {
        ...state,
        loading: false
      });
    }
    
    return {
      ...state,
      loading: false
    };
  }),
  on(URLActions.deleteUrlFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Generate QR Code
  on(URLActions.generateQrCode, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(URLActions.generateQrCodeSuccess, (state, { shortCode, qrBlob }) => {
    // Create a new map with the updated QR code
    const newMap = new Map(state.selectedUrlQrCode);
    newMap.set(shortCode, qrBlob);
    
    return {
      ...state,
      selectedUrlQrCode: newMap,
      loading: false
    };
  }),
  on(URLActions.generateQrCodeFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  }))
);

// Export entity selectors
export const {
  selectIds,
  selectEntities,
  selectAll,
  selectTotal
} = urlAdapter.getSelectors(); 