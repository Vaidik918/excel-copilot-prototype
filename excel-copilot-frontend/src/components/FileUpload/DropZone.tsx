'use client';

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Cloud, Upload, AlertCircle } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { useAppStore } from '@/stores/appStore';

interface DropZoneProps {
  sessionId: string;
  onFileUpload: (fileId: string) => void;
  onError?: (error: string) => void;
}

export function DropZone({ sessionId, onFileUpload, onError }: DropZoneProps) {
  const { setLoading, setError } = useAppStore();
  const [uploadProgress, setUploadProgress] = React.useState(0);

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      setLoading(true);
      try {
        const result = await apiClient.uploadFile(
          sessionId,
          file,
          (progress) => setUploadProgress(progress)
        );
        return result;
      } finally {
        setLoading(false);
      }
    },
    onSuccess: (data) => {
      setUploadProgress(0);
      onFileUpload(data.file_id);
    },
    onError: (error) => {
      const message = error instanceof Error ? error.message : 'Upload failed';
      setError(message);
      onError?.(message);
    },
  });

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file && (file.type.includes('spreadsheet') || file.name.endsWith('.xlsx'))) {
        uploadMutation.mutate(file);
      } else {
        const error = 'Please upload a valid Excel file (.xlsx)';
        setError(error);
        onError?.(error);
      }
    },
    [sessionId, uploadMutation, setError, onError]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    disabled: uploadMutation.isPending,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
        transition-all duration-200
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
        ${uploadMutation.isPending ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-400'}
      `}
    >
      <input {...getInputProps()} />

      <div className="flex flex-col items-center gap-4">
        {uploadMutation.isPending ? (
          <>
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-blue-600 animate-pulse" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">Uploading...</p>
              <p className="text-sm text-gray-600">{uploadProgress}%</p>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          </>
        ) : (
          <>
            <Cloud className="w-12 h-12 text-gray-400" />
            <div>
              <p className="font-semibold text-gray-800">
                {isDragActive ? 'Drop your file here' : 'Drag & drop your Excel file'}
              </p>
              <p className="text-sm text-gray-600">or click to select a file</p>
              <p className="text-xs text-gray-500 mt-2">Supports .xlsx and .xls files</p>
            </div>
          </>
        )}
      </div>

      {uploadMutation.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-700">
            {uploadMutation.error instanceof Error
              ? uploadMutation.error.message
              : 'Upload failed'}
          </p>
        </div>
      )}
    </div>
  );
}
