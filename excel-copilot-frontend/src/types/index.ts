// Session & Auth
export interface Session {
  session_id: string;
  user_id: string;
  created_at: string;
  files: string[];
  operations: Operation[];
}

// File Management
export interface UploadedFile {
  file_id: string;
  filename: string;
  size_mb: number;
  sheet_names: string[];
  total_rows: number;
  total_columns: number;
  columns: string[];
  preview_data: Record<string, any>[];
  uploaded_at: string;
}

// Analysis & Code Generation
export interface AnalysisRequest {
  session_id: string;
  file_id: string;
  prompt: string;
}

export interface AnalysisResponse {
  success: boolean;
  code: string;
  explanation: string;
  risks: string[];
  estimated_rows_affected: string;
  code_suggestions?: string[];
}

// Execution
export interface ExecutionRequest {
  session_id: string;
  file_id: string;
  code: string;
}

export interface ExecutionResponse {
  success: boolean;
  execution_id: string;
  rows_before: number;
  rows_after: number;
  columns_before: number;
  columns_after: number;
  preview_data: Record<string, any>[];
  execution_time_ms: number;
  is_preview?: boolean;
  error?: string;
}

export interface PreviewResult {
  rows_before: number;
  rows_after: number;
  rows_removed: number;
  columns_before: number;
  columns_after: number;
  preview_data: Record<string, any>[];
}

// Operations History
export interface Operation {
  operation_id: string;
  type: 'upload' | 'analyze' | 'preview' | 'execute' | 'download';
  timestamp: string;
  status: 'success' | 'error' | 'pending';
  data?: Record<string, any>;
  error_message?: string;
}

// Download
export interface DownloadOptions {
  session_id: string;
  file_id: string;
  version: 'original' | 'modified';
}

export interface SessionFile {
  file_id: string;
  filename: string;
  versions: {
    original: string;
    modified?: string;
  };
  created_at: string;
  modified_at?: string;
}
