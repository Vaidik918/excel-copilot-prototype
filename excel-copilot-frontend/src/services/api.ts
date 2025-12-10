import axios, { AxiosInstance, AxiosError } from 'axios';
import { Session, UploadedFile, AnalysisResponse, ExecutionResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

class APIClient {
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // ============ SESSION ENDPOINTS ============

  async createSession(): Promise<{ session_id: string }> {
    const response = await this.axiosInstance.post('/api/session/create');
    return response.data;
  }

  async getSession(sessionId: string): Promise<{ session: Session }> {
    const response = await this.axiosInstance.get(`/api/session/${sessionId}`);
    return response.data;
  }

  // ============ FILE UPLOAD ENDPOINTS ============

  async uploadFile(
    sessionId: string,
    file: File,
    onUploadProgress?: (progress: number) => void
  ): Promise<{ 
    success: boolean;
    file_id: string; 
    filename: string;
    metadata: {
      total_rows: number;
      total_columns: number;
      sheet_names: string[];
      columns: string[];
      preview_data: Record<string, any>[];
    };
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    const response = await this.axiosInstance.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onUploadProgress?.(percentCompleted);
        }
      },
    });

    return response.data;
  }

  // ============ ANALYSIS ENDPOINTS ============

  async analyzePrompt(
    sessionId: string,
    fileId: string,
    prompt: string
  ): Promise<AnalysisResponse> {
    const response = await this.axiosInstance.post('/api/analyze', {
      session_id: sessionId,
      file_id: fileId,
      prompt,
    });
    return response.data;
  }

  // ============ EXECUTION ENDPOINTS ============

  async executePreview(
    sessionId: string,
    fileId: string,
    code: string
  ): Promise<ExecutionResponse> {
    const response = await this.axiosInstance.post('/api/execute/preview', {
      session_id: sessionId,
      file_id: fileId,
      code,
    });
    return response.data;
  }

  async executeCode(
    sessionId: string,
    fileId: string,
    code: string
  ): Promise<ExecutionResponse> {
    const response = await this.axiosInstance.post('/api/execute', {
      session_id: sessionId,
      file_id: fileId,
      code,
    });
    return response.data;
  }

  // ============ DOWNLOAD ENDPOINTS ============

  async downloadFile(
    fileId: string,
    sessionId: string,
    version: 'original' | 'modified' = 'original'
  ): Promise<Blob> {
    const response = await this.axiosInstance.get(
      `/api/download/${fileId}`,
      {
        params: { session_id: sessionId, version },
        responseType: 'blob',
      }
    );
    return response.data;
  }

  async getSessionFiles(sessionId: string): Promise<{ files: any[] }> {
    const response = await this.axiosInstance.get(
      `/api/download/session/${sessionId}/files`
    );
    return response.data;
  }
}

export const apiClient = new APIClient();
