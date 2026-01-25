"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";

import { getNotes, createNote, updateNote, deleteNote } from "@/lib/api";
import type { Note, CreateNoteRequest, UpdateNoteRequest } from "@/lib/types";

import { useAuth } from "./AuthContext";

interface DataContextType {
  // Notes
  notes: Note[];
  selectedNote: Note | null;
  isLoadingNotes: boolean;
  notesError: string | null;
  fetchNotes: () => Promise<void>;
  selectNote: (note: Note | null) => void;
  createNewNote: (request: CreateNoteRequest) => Promise<Note>;
  updateExistingNote: (
    noteId: string,
    request: UpdateNoteRequest
  ) => Promise<Note>;
  deleteExistingNote: (noteId: string) => Promise<void>;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const DataProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { isAuthenticated } = useAuth();
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [isLoadingNotes, setIsLoadingNotes] = useState(false);
  const [notesError, setNotesError] = useState<string | null>(null);

  // Fetch all notes
  const fetchNotes = useCallback(async () => {
    if (!isAuthenticated) return;

    setIsLoadingNotes(true);
    setNotesError(null);
    try {
      const response = await getNotes();
      setNotes(response.notes.notes);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to fetch notes";
      setNotesError(errorMessage);
    } finally {
      setIsLoadingNotes(false);
    }
  }, [isAuthenticated]);

  // Select a note
  const selectNote = useCallback((note: Note | null) => {
    setSelectedNote(note);
  }, []);

  // Create a new note
  const createNewNote = useCallback(
    async (request: CreateNoteRequest): Promise<Note> => {
      try {
        const response = await createNote(request);
        const newNote = response.note;
        setNotes(prev => [...prev, newNote]);
        setSelectedNote(newNote);
        return newNote;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Failed to create note";
        setNotesError(errorMessage);
        throw error;
      }
    },
    []
  );

  // Update an existing note
  const updateExistingNote = useCallback(
    async (noteId: string, request: UpdateNoteRequest): Promise<Note> => {
      try {
        const response = await updateNote(noteId, request);
        const updatedNote = response.note;
        setNotes(prev =>
          prev.map(note => (note.id === noteId ? updatedNote : note))
        );
        if (selectedNote?.id === noteId) {
          setSelectedNote(updatedNote);
        }
        return updatedNote;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Failed to update note";
        setNotesError(errorMessage);
        throw error;
      }
    },
    [selectedNote]
  );

  // Delete a note
  const deleteExistingNote = useCallback(
    async (noteId: string): Promise<void> => {
      try {
        await deleteNote(noteId);
        setNotes(prev => prev.filter(note => note.id !== noteId));
        if (selectedNote?.id === noteId) {
          setSelectedNote(null);
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Failed to delete note";
        setNotesError(errorMessage);
        throw error;
      }
    },
    [selectedNote]
  );

  // Fetch notes on mount and when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchNotes();
    } else {
      // Clear notes when logged out
      setNotes([]);
      setSelectedNote(null);
    }
  }, [isAuthenticated, fetchNotes]);

  const value: DataContextType = {
    notes,
    selectedNote,
    isLoadingNotes,
    notesError,
    fetchNotes,
    selectNote,
    createNewNote,
    updateExistingNote,
    deleteExistingNote,
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

export const useData = (): DataContextType => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error("useData must be used within a DataProvider");
  }
  return context;
};
