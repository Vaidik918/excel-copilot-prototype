import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useSession } from '@/hooks/useSession';
import { apiClient } from '@/services/api';

vi.mock('@/services/api');

describe('useSession', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should create a new session on initialization', async () => {
    const mockSessionId = 'test-session-123';
    const mockSession = {
      session_id: mockSessionId,
      user_id: 'default',
      created_at: '2024-01-01T00:00:00Z',
      files: [],
      operations: [],
    };

    vi.mocked(apiClient.createSession).mockResolvedValue({
      session_id: mockSessionId,
    });
    vi.mocked(apiClient.getSession).mockResolvedValue({
      session: mockSession,
    });

    const { result } = renderHook(() => useSession());

    await waitFor(() => {
      expect(result.current.session).toBeDefined();
    });

    expect(result.current.session?.session_id).toBe(mockSessionId);
  });

  it('should restore session from localStorage', async () => {
    const mockSessionId = 'saved-session-456';
    const mockSession = {
      session_id: mockSessionId,
      user_id: 'default',
      created_at: '2024-01-01T00:00:00Z',
      files: [],
      operations: [],
    };

    localStorage.setItem('sessionId', mockSessionId);

    vi.mocked(apiClient.getSession).mockResolvedValue({
      session: mockSession,
    });

    const { result } = renderHook(() => useSession());

    await waitFor(() => {
      expect(result.current.session).toBeDefined();
    });

    expect(result.current.session?.session_id).toBe(mockSessionId);
  });
});
