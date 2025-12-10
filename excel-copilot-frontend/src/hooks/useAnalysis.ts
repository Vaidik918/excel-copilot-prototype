import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { useAppStore } from '@/stores/appStore';
import { AnalysisResponse } from '@/types';

export function useAnalysis() {
  const { setLoading, setError, addOperation } = useAppStore();

  const analyzeMutation = useMutation({
    mutationFn: async ({
      sessionId,
      fileId,
      prompt,
    }: {
      sessionId: string;
      fileId: string;
      prompt: string;
    }): Promise<AnalysisResponse> => {
      setLoading(true);
      try {
        const result = await apiClient.analyzePrompt(sessionId, fileId, prompt);
        
        addOperation({
          operation_id: Math.random().toString(36).substring(7),
          type: 'analyze',
          timestamp: new Date().toISOString(),
          status: 'success',
          data: { prompt, code: result.code },
        });

        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Analysis failed';
        setError(errorMessage);
        
        addOperation({
          operation_id: Math.random().toString(36).substring(7),
          type: 'analyze',
          timestamp: new Date().toISOString(),
          status: 'error',
          error_message: errorMessage,
        });

        throw error;
      } finally {
        setLoading(false);
      }
    },
  });

  return {
    analyze: analyzeMutation.mutate,
    isLoading: analyzeMutation.isPending,
    error: analyzeMutation.error,
    data: analyzeMutation.data,
    isSuccess: analyzeMutation.isSuccess,
  };
}
