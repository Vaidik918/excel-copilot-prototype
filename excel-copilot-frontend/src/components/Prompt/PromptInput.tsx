import React, { useState } from 'react';
import { Send, Sparkles, AlertCircle } from 'lucide-react';
import { useAnalysis } from '@/hooks/useAnalysis';

interface PromptInputProps {
  sessionId: string;
  fileId: string;
  onAnalysisComplete: (code: string, explanation: string) => void;
  isLoading?: boolean;
}

export function PromptInput({
  sessionId,
  fileId,
  onAnalysisComplete,
  isLoading = false,
}: PromptInputProps) {
  const [prompt, setPrompt] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { analyze, isLoading: isAnalyzing, error } = useAnalysis();

  const suggestions = [
    'Filter rows where status is Active',
    'Calculate total amount per status',
    'Remove duplicates based on ID',
    'Add a new column with calculated values',
    'Sort by amount in descending order',
  ];

  const handleSubmit = () => {
    if (!prompt.trim()) return;

    analyze(
      { sessionId, fileId, prompt },
      {
        onSuccess: (data) => {
          onAnalysisComplete(data.code, data.explanation);
          setPrompt('');
        },
      }
    );
  };

  const handleSuggestionClick = (suggestion: string) => {
    setPrompt(suggestion);
    setShowSuggestions(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSubmit();
    }
  };

  return (
    <div className="space-y-4">
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          onKeyPress={handleKeyPress}
          placeholder="Describe what you want to do with your data... (Ctrl+Enter to submit)"
          className={`
            w-full p-4 border-2 rounded-lg resize-none focus:outline-none
            transition-colors duration-200
            ${error ? 'border-red-300 focus:border-red-500' : 'border-gray-300 focus:border-blue-500'}
          `}
          rows={4}
          disabled={isAnalyzing || isLoading}
        />

        <button
          onClick={handleSubmit}
          disabled={isAnalyzing || isLoading || !prompt.trim()}
          className={`
            absolute bottom-3 right-3 p-2 rounded-lg flex items-center gap-2
            transition-all duration-200
            ${
              isAnalyzing || isLoading || !prompt.trim()
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
            }
          `}
        >
          <Send className="w-5 h-5" />
        </button>

        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-300 rounded-lg shadow-lg z-10">
            <p className="px-4 py-2 text-sm text-gray-600 border-b">Suggestions:</p>
            <div className="space-y-1">
              {suggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-2 hover:bg-blue-50 text-sm text-gray-700 flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4 text-blue-500" />
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-700">
            {error instanceof Error ? error.message : 'Analysis failed'}
          </p>
        </div>
      )}

      {isAnalyzing && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          🤖 Analyzing your request with AI...
        </div>
      )}
    </div>
  );
}
