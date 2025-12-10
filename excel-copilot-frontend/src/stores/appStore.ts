import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Session, UploadedFile, Operation } from '@/types';

interface AppStore {
  // State
  session: Session | null;
  currentFile: UploadedFile | null;
  operations: Operation[];
  isLoading: boolean;
  error: string | null;
  darkMode: boolean;

  // Session actions
  setSession: (session: Session) => void;
  clearSession: () => void;

  // File actions
  setCurrentFile: (file: UploadedFile) => void;
  clearCurrentFile: () => void;

  // Operations tracking
  addOperation: (operation: Operation) => void;
  clearOperations: () => void;

  // Loading & error states
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Theme
  toggleDarkMode: () => void;
  setDarkMode: (mode: boolean) => void;
}

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      session: null,
      currentFile: null,
      operations: [],
      isLoading: false,
      error: null,
      darkMode: false,

      setSession: (session) => set({ session }),
      clearSession: () => set({ session: null }),

      setCurrentFile: (file) => set({ currentFile: file }),
      clearCurrentFile: () => set({ currentFile: null }),

      addOperation: (operation) =>
        set((state) => ({
          operations: [operation, ...state.operations].slice(0, 50), // Keep last 50
        })),
      clearOperations: () => set({ operations: [] }),

      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),

      toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
      setDarkMode: (darkMode) => set({ darkMode }),
    }),
    {
      name: 'excel-copilot-store',
      partialize: (state) => ({
        darkMode: state.darkMode,
        operations: state.operations.slice(0, 10), // Only persist recent ops
      }),
    }
  )
);
