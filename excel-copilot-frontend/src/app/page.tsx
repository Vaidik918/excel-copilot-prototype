'use client';

import React, { useState } from 'react';
import { useSession } from '@/hooks/useSession';
import { useAppStore } from '@/stores/appStore';
import { DropZone } from '@/components/FileUpload/DropZone';
import { PromptInput } from '@/components/Prompt/PromptInput';
import { CodeDisplay } from '@/components/CodePreview/CodeDisplay';
import { PreviewTable } from '@/components/Results/PreviewTable';
import { Spinner } from '@/components/Common/Spinner';
import { AlertCircle } from 'lucide-react';

export default function Home() {
  const { session, isLoading: sessionLoading } = useSession();
  const { currentFile, isLoading, error } = useAppStore();
  const [analysisResult, setAnalysisResult] = useState<{
    code: string;
    explanation: string;
  } | null>(null);
  const [previewResult, setPreviewResult] = useState<any | null>(null);

  if (sessionLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Failed to initialize session</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Excel Copilot</h1>
          <p className="text-gray-600 mt-1">AI-powered Excel data analysis</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Upload & Prompt */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                1. Upload File
              </h2>
              {!currentFile ? (
                <DropZone
                  sessionId={session.session_id}
                  onFileUpload={(fileId) => {
                    // Update store with file
                    console.log('File uploaded:', fileId);
                  }}
                />
              ) : (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm font-medium text-green-900">
                    ✓ {currentFile.filename} uploaded
                  </p>
                  <p className="text-xs text-green-700 mt-1">
                    {currentFile.total_rows} rows × {currentFile.total_columns} columns
                  </p>
                </div>
              )}
            </div>

            {currentFile && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  2. Describe Changes
                </h2>
                <PromptInput
                  sessionId={session.session_id}
                  fileId={currentFile.file_id}
                  onAnalysisComplete={(code, explanation) => {
                    setAnalysisResult({ code, explanation });
                  }}
                  isLoading={isLoading}
                />
              </div>
            )}
          </div>

          {/* Right Column: Code & Results */}
          <div className="lg:col-span-2 space-y-6">
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {analysisResult && (
              <>
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    3. Generated Code
                  </h2>
                  <CodeDisplay code={analysisResult.code} />
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Explanation
                  </h2>
                  <p className="text-gray-700">{analysisResult.explanation}</p>
                </div>
              </>
            )}

            {previewResult && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  4. Preview Results
                </h2>
                <PreviewTable data={previewResult.preview_data} />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
