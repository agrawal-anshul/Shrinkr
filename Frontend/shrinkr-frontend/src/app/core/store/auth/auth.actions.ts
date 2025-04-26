import { createAction, props } from '@ngrx/store';
import { User, UserCreate, TokenResponse } from '../../models/user.model';

// Login Actions
export const login = createAction(
  '[Auth] Login',
  props<{ email: string; password: string }>()
);

export const loginSuccess = createAction(
  '[Auth] Login Success',
  props<{ tokenResponse: TokenResponse }>()
);

export const loginFailure = createAction(
  '[Auth] Login Failure',
  props<{ error: any }>()
);

// Register Actions
export const register = createAction(
  '[Auth] Register',
  props<{ userData: UserCreate }>()
);

export const registerSuccess = createAction(
  '[Auth] Register Success',
  props<{ tokenResponse: TokenResponse }>()
);

export const registerFailure = createAction(
  '[Auth] Register Failure',
  props<{ error: any }>()
);

// Logout Actions
export const logout = createAction('[Auth] Logout');
export const logoutComplete = createAction('[Auth] Logout Complete');

// Get User Profile Actions
export const getUserProfile = createAction('[Auth] Get User Profile');

export const getUserProfileSuccess = createAction(
  '[Auth] Get User Profile Success',
  props<{ user: User }>()
);

export const getUserProfileFailure = createAction(
  '[Auth] Get User Profile Failure',
  props<{ error: any }>()
); 