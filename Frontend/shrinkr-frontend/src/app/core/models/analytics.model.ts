import { URLResponse } from './url.model';

export interface TimeBasedStats {
  date: string;
  clicks: number;
}

export interface LocationStats {
  country: string;
  city?: string | null;
  clicks: number;
}

export interface DeviceStats {
  device_type: string;
  clicks: number;
}

export interface BrowserStats {
  browser: string;
  clicks: number;
}

export interface OSStats {
  os: string;
  clicks: number;
}

export interface ClickLog {
  clicked_at: string;
  ip_address?: string | null;
  user_agent?: string | null;
  referrer?: string | null;
  country?: string | null;
  city?: string | null;
  device_type?: string | null;
  browser?: string | null;
  os?: string | null;
  is_mobile?: boolean;
  is_bot?: boolean;
}

export interface DetailedAnalytics {
  total_clicks: number;
  unique_visitors: number;
  time_based: TimeBasedStats[];
  locations: LocationStats[];
  devices: DeviceStats[];
  browsers: BrowserStats[];
  operating_systems: OSStats[];
  is_mobile_percentage: number;
  is_bot_percentage: number;
}

export interface AnalyticsExport {
  url: URLResponse;
  analytics: DetailedAnalytics;
  raw_clicks: ClickLog[];
} 