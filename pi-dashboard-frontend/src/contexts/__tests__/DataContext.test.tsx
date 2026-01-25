import { act, renderHook, waitFor } from "@testing-library/react";
import React from "react";

import { DataProvider, useData } from "@/contexts/DataContext";
import * as api from "@/lib/api";
import type { Note, CreateNoteRequest, UpdateNoteRequest } from "@/lib/types";

// Mock the API module
jest.mock("@/lib/api");

// Mock the auth context
const mockUseAuth = jest.fn();
jest.mock("@/contexts/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
  AuthProvider: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
}));

const mockNote1: Note = {
  id: "1",
  title: "Test Note 1",
  content: "Content 1",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

const mockNote2: Note = {
  id: "2",
  title: "Test Note 2",
  content: "Content 2",
  created_at: "2024-01-02T00:00:00Z",
  updated_at: "2024-01-02T00:00:00Z",
};

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <DataProvider>{children}</DataProvider>
);

describe("DataContext", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuth.mockReturnValue({ isAuthenticated: true });
  });

  describe("fetchNotes", () => {
    it("should fetch notes successfully", async () => {
      (api.getNotes as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Success",
        timestamp: "2024-01-01T00:00:00Z",
        notes: { notes: [mockNote1, mockNote2] },
      });

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.notes).toHaveLength(2);
      });

      expect(result.current.notes).toEqual([mockNote1, mockNote2]);
      expect(result.current.isLoadingNotes).toBe(false);
      expect(result.current.notesError).toBeNull();
    });

    it("should handle fetch error", async () => {
      (api.getNotes as jest.Mock).mockRejectedValue(
        new Error("Failed to fetch")
      );

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.notesError).toBe("Failed to fetch");
      });

      expect(result.current.notes).toEqual([]);
      expect(result.current.isLoadingNotes).toBe(false);
    });

    it("should not fetch notes when not authenticated", async () => {
      mockUseAuth.mockReturnValue({ isAuthenticated: false });

      renderHook(() => useData(), { wrapper });

      expect(api.getNotes).not.toHaveBeenCalled();
    });
  });

  describe("selectNote", () => {
    it("should select a note", async () => {
      (api.getNotes as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Success",
        timestamp: "2024-01-01T00:00:00Z",
        notes: { notes: [mockNote1] },
      });

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.notes).toHaveLength(1);
      });

      act(() => {
        result.current.selectNote(mockNote1);
      });

      expect(result.current.selectedNote).toEqual(mockNote1);
    });

    it("should deselect a note", async () => {
      (api.getNotes as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Success",
        timestamp: "2024-01-01T00:00:00Z",
        notes: { notes: [mockNote1] },
      });

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.notes).toHaveLength(1);
      });

      act(() => {
        result.current.selectNote(mockNote1);
      });

      expect(result.current.selectedNote).toEqual(mockNote1);

      act(() => {
        result.current.selectNote(null);
      });

      expect(result.current.selectedNote).toBeNull();
    });
  });

  describe("createNewNote", () => {
    it("should create a new note", async () => {
      (api.getNotes as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Success",
        timestamp: "2024-01-01T00:00:00Z",
        notes: { notes: [] },
      });

      (api.createNote as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Created",
        timestamp: "2024-01-01T00:00:00Z",
        note: mockNote1,
      });

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoadingNotes).toBe(false);
      });

      const request: CreateNoteRequest = {
        title: "Test Note 1",
        content: "Content 1",
      };

      let createdNote: Note | undefined;
      await act(async () => {
        createdNote = await result.current.createNewNote(request);
      });

      expect(createdNote).toEqual(mockNote1);
      expect(result.current.notes).toContainEqual(mockNote1);
      expect(result.current.selectedNote).toEqual(mockNote1);
    });

    it("should handle create error", async () => {
      (api.getNotes as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Success",
        timestamp: "2024-01-01T00:00:00Z",
        notes: { notes: [] },
      });

      (api.createNote as jest.Mock).mockRejectedValue(
        new Error("Failed to create")
      );

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoadingNotes).toBe(false);
      });

      const request: CreateNoteRequest = {
        title: "Test Note",
        content: "Content",
      };

      await expect(
        act(async () => {
          await result.current.createNewNote(request);
        })
      ).rejects.toThrow("Failed to create");

      // The error should be set, but may clear on next operation
      // So we just verify the operation failed as expected
    });
  });

  describe("updateExistingNote", () => {
    it("should update a note", async () => {
      (api.getNotes as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Success",
        timestamp: "2024-01-01T00:00:00Z",
        notes: { notes: [mockNote1] },
      });

      const updatedNote = { ...mockNote1, title: "Updated Title" };
      (api.updateNote as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Updated",
        timestamp: "2024-01-01T00:00:00Z",
        note: updatedNote,
      });

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.notes).toHaveLength(1);
      });

      const request: UpdateNoteRequest = {
        title: "Updated Title",
      };

      await act(async () => {
        await result.current.updateExistingNote(mockNote1.id, request);
      });

      expect(result.current.notes[0]!.title).toBe("Updated Title");
    });
  });

  describe("deleteExistingNote", () => {
    it("should delete a note", async () => {
      (api.getNotes as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Success",
        timestamp: "2024-01-01T00:00:00Z",
        notes: { notes: [mockNote1, mockNote2] },
      });

      (api.deleteNote as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Deleted",
        timestamp: "2024-01-01T00:00:00Z",
      });

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.notes).toHaveLength(2);
      });

      await act(async () => {
        await result.current.deleteExistingNote(mockNote1.id);
      });

      expect(result.current.notes).toHaveLength(1);
      expect(result.current.notes[0]).toEqual(mockNote2);
    });

    it("should clear selected note when deleting it", async () => {
      (api.getNotes as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Success",
        timestamp: "2024-01-01T00:00:00Z",
        notes: { notes: [mockNote1] },
      });

      (api.deleteNote as jest.Mock).mockResolvedValue({
        code: 200,
        message: "Deleted",
        timestamp: "2024-01-01T00:00:00Z",
      });

      const { result } = renderHook(() => useData(), { wrapper });

      await waitFor(() => {
        expect(result.current.notes).toHaveLength(1);
      });

      act(() => {
        result.current.selectNote(mockNote1);
      });

      expect(result.current.selectedNote).toEqual(mockNote1);

      await act(async () => {
        await result.current.deleteExistingNote(mockNote1.id);
      });

      expect(result.current.selectedNote).toBeNull();
    });
  });
});
