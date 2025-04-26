import { createReducer, on } from '@ngrx/store';
import { User } from '../../models/user.model';
import * as AuthActions from './auth.actions';

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: any;
  isAuthenticated: boolean;
}

export const initialState: AuthState = {
  user: null,
  loading: false,
  error: null,
  isAuthenticated: false
};

export const authReducer = createReducer(
  initialState,
  
  // Login
  on(AuthActions.login, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(AuthActions.loginSuccess, state => ({
    ...state,
    loading: false,
    isAuthenticated: true,
    error: null
  })),
  on(AuthActions.loginFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Register
  on(AuthActions.register, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(AuthActions.registerSuccess, state => ({
    ...state,
    loading: false,
    isAuthenticated: true,
    error: null
  })),
  on(AuthActions.registerFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Logout
  on(AuthActions.logout, state => ({
    ...state,
    loading: true
  })),
  on(AuthActions.logoutComplete, state => ({
    ...state,
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null
  })),
  
  // Get User Profile
  on(AuthActions.getUserProfile, state => ({
    ...state,
    loading: true
  })),
  on(AuthActions.getUserProfileSuccess, (state, { user }) => ({
    ...state,
    user,
    loading: false,
    isAuthenticated: true
  })),
  on(AuthActions.getUserProfileFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  }))
); 