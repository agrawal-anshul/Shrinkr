import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly THEME_KEY = 'shrinkr_theme';
  
  // Angular 17 signal-based state management
  private darkThemeSignal = signal<boolean>(false);
  
  // Expose readonly signal
  readonly isDarkTheme = this.darkThemeSignal.asReadonly();

  constructor() {
    this.loadThemeFromStorage();
  }

  private loadThemeFromStorage(): void {
    const savedTheme = localStorage.getItem(this.THEME_KEY);
    
    if (savedTheme) {
      // Parse saved theme value
      this.darkThemeSignal.set(savedTheme === 'dark');
    } else {
      // Check for system preference if no saved setting
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.darkThemeSignal.set(prefersDark);
      this.saveThemeToStorage(prefersDark);
    }
    
    // Apply theme to body
    this.applyTheme(this.darkThemeSignal());
    
    // Listen for system preference changes
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (localStorage.getItem(this.THEME_KEY) === null) {
          this.setDarkTheme(e.matches);
        }
      });
    }
  }

  private saveThemeToStorage(isDark: boolean): void {
    localStorage.setItem(this.THEME_KEY, isDark ? 'dark' : 'light');
  }

  private applyTheme(isDark: boolean): void {
    // Apply the theme to the document element for Material theming
    if (isDark) {
      document.documentElement.classList.add('dark-theme');
      document.documentElement.classList.remove('light-theme');
    } else {
      document.documentElement.classList.add('light-theme');
      document.documentElement.classList.remove('dark-theme');
    }
  }

  toggleTheme(): void {
    const newTheme = !this.darkThemeSignal();
    this.setDarkTheme(newTheme);
  }

  setDarkTheme(isDark: boolean): void {
    this.darkThemeSignal.set(isDark);
    this.saveThemeToStorage(isDark);
    this.applyTheme(isDark);
  }
} 