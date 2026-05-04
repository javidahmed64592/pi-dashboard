"use client";

import { useState, useEffect, useMemo } from "react";

import NoteEditor from "@/components/notes/NoteEditor";
import NotesHeader from "@/components/notes/NotesHeader";
import NotesList from "@/components/notes/NotesList";
import { getNotes, performNoteAction } from "@/lib/api";
import type { NoteEntry } from "@/lib/types";
import { DatabaseAction } from "@/lib/types";

type SortCategory = "updated" | "created" | "title";
type SortDirection = "asc" | "desc";

export default function NotesPage() {
  const [notes, setNotes] = useState<NoteEntry[]>([]);
  const [selectedNote, setSelectedNote] = useState<NoteEntry | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [sortBy, setSortBy] = useState<SortCategory>("updated");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [searchQuery, setSearchQuery] = useState("");

  // Load notes on mount
  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await getNotes();
      setNotes(response.notes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load notes");
    } finally {
      setIsLoading(false);
    }
  };

  // Sort and filter notes based on current sort settings and search query
  const filteredAndSortedNotes = useMemo(() => {
    // Filter notes based on search query
    let filtered = notes;
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = notes.filter(
        note =>
          note.title.toLowerCase().includes(query) ||
          note.content.toLowerCase().includes(query)
      );
    }

    // Sort the filtered notes
    const sorted = [...filtered].sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case "created":
          comparison = a.time_created - b.time_created;
          break;
        case "updated":
          comparison = a.time_updated - b.time_updated;
          break;
        case "title":
          comparison = a.title.localeCompare(b.title);
          break;
      }

      return sortDirection === "asc" ? comparison : -comparison;
    });

    return sorted;
  }, [notes, sortBy, sortDirection, searchQuery]);

  const createNewNote = () => {
    const newNote: NoteEntry = {
      id: null,
      title: "New Entry",
      content: "",
      time_created: 0,
      time_updated: 0,
    };
    setSelectedNote(newNote);
  };

  const handleNoteSelect = (note: NoteEntry) => {
    setSelectedNote({ ...note });
  };

  const handleTitleChange = (title: string) => {
    if (selectedNote) {
      setSelectedNote({ ...selectedNote, title });
    }
  };

  const handleContentChange = (content: string) => {
    if (selectedNote) {
      setSelectedNote({ ...selectedNote, content });
    }
  };

  const handleSave = async () => {
    if (!selectedNote) return;

    try {
      setIsSaving(true);
      setError(null);

      const action =
        selectedNote.id === null
          ? DatabaseAction.CREATE
          : DatabaseAction.UPDATE;

      const response = await performNoteAction({
        action,
        note: selectedNote,
      });

      // Reload notes
      const notesResponse = await getNotes();
      setNotes(notesResponse.notes);

      // Keep the note selected by finding it in the refreshed list
      const savedNote = notesResponse.notes.find(
        n => n.id === response.note_id
      );
      if (savedNote) {
        setSelectedNote({ ...savedNote });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save note");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedNote || selectedNote.id === null) return;

    if (!confirm("Are you sure you want to delete this note?")) return;

    try {
      setIsSaving(true);
      setError(null);

      await performNoteAction({
        action: DatabaseAction.DELETE,
        note: selectedNote,
      });

      await loadNotes();
      setSelectedNote(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete note");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopy = () => {
    if (selectedNote) {
      navigator.clipboard.writeText(
        `${selectedNote.title}\n\n${selectedNote.content}`
      );
    }
  };

  const handlePasteAndSave = async () => {
    if (!selectedNote || selectedNote.id !== null) return;

    try {
      // Read clipboard content
      const clipboardText = await navigator.clipboard.readText();

      // Update note content
      const updatedNote = { ...selectedNote, content: clipboardText };
      setSelectedNote(updatedNote);

      // Save immediately
      setIsSaving(true);
      setError(null);

      const response = await performNoteAction({
        action: DatabaseAction.CREATE,
        note: updatedNote,
      });

      // Reload notes
      const notesResponse = await getNotes();
      setNotes(notesResponse.notes);

      // Keep the note selected
      const savedNote = notesResponse.notes.find(
        n => n.id === response.note_id
      );
      if (savedNote) {
        setSelectedNote({ ...savedNote });
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to paste and save note"
      );
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
      {/* Notes List - Left Side */}
      <div className="lg:col-span-3 min-h-0 flex flex-col">
        <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon h-full flex flex-col">
          <NotesHeader
            onCreateNew={createNewNote}
            sortBy={sortBy}
            setSortBy={setSortBy}
            sortDirection={sortDirection}
            setSortDirection={setSortDirection}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
          />
          <NotesList
            notes={filteredAndSortedNotes}
            selectedNote={selectedNote}
            onSelectNote={handleNoteSelect}
            isLoading={isLoading}
            error={error}
          />
        </div>
      </div>

      {/* Note Editor - Right Side */}
      <div className="lg:col-span-9 min-h-0 flex flex-col">
        <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon h-full flex flex-col">
          <NoteEditor
            note={selectedNote}
            onTitleChange={handleTitleChange}
            onContentChange={handleContentChange}
            onSave={handleSave}
            onDelete={handleDelete}
            onCopy={handleCopy}
            onPasteAndSave={handlePasteAndSave}
            onCreateNew={createNewNote}
            isSaving={isSaving}
          />
        </div>
      </div>
    </div>
  );
}
