import { useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { useAppStore } from '@/stores/appStore';
import { Session } from '@/types';

export function useSession() {
  const { session, setSession, clearSession } = useAppStore();

  // Get or create session
  const createSessionMutation = useMutation({
    mutationFn: async () => {
      const { session_id } = await apiClient.createSession();
      
      // Get full session data
      const sessionData = await apiClient.getSession(session_id);
      return sessionData.session;
    },
    onSuccess: (sessionData) => {
      setSession(sessionData);
      localStorage.setItem('sessionId', sessionData.session_id);
    },
  });

  // Fetch session from API
  const getSessionQuery = useQuery({
    queryKey: ['session', session?.session_id],
    queryFn: () => {
      if (!session?.session_id) throw new Error('No session ID');
      return apiClient.getSession(session.session_id);
    },
    enabled: !!session?.session_id,
    refetchInterval: 30000, // Refetch every 30s
  });

  // Initialize or restore session
  useEffect(() => {
    const initializeSession = async () => {
      const savedSessionId = localStorage.getItem('sessionId');

      if (savedSessionId && !session) {
        try {
          const sessionData = await apiClient.getSession(savedSessionId);
          setSession(sessionData.session);
        } catch {
          // Session expired, create new one
          createSessionMutation.mutate();
        }
      } else if (!session) {
        createSessionMutation.mutate();
      }
    };

    initializeSession();
  }, []);

  return {
    session,
    isLoading: createSessionMutation.isPending || getSessionQuery.isLoading,
    error: createSessionMutation.error || getSessionQuery.error,
    createSession: () => createSessionMutation.mutate(),
    refetchSession: () => getSessionQuery.refetch(),
  };
}
