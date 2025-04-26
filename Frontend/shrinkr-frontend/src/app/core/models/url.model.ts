export interface URLBase {
  original_url: string;
  custom_alias?: string;
  expires_at?: string | null;
  click_limit?: number | null;
}

export interface URLCreate extends URLBase {
  expires_in_days?: number | null;
}

export interface URLUpdate {
  original_url?: string;
  expires_at?: string | null;
  click_limit?: number | null;
  expires_in_days?: number | null;
}

export interface URLResponse {
  id: number;
  short_code: string;
  original_url: string;
  created_at: string;
  expires_at: string | null;
  click_count: number;
  click_limit: number | null;
}

export interface BulkURLCreate {
  urls: URLCreate[];
}

export interface BulkURLResponse {
  urls: URLResponse[];
  failed_urls: { url: string; error: string }[];
} 