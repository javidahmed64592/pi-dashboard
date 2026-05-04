"use client";

import { useState, useEffect, useMemo } from "react";

import { getNotes, performNoteAction } from "@/lib/api";
import type { NoteEntry } from "@/lib/types";
import { DatabaseAction } from "@/lib/types";

type SortCategory = "updated" | "created" | "title";
type SortDirection = "asc" | "desc";

// Helper function to format timestamps
const formatTimestamp = (timestamp: number): string => {
  if (!timestamp) return "Never";
  const date = new Date(timestamp * 1000);
  return date.toLocaleString("en-GB", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export default function NotesPage() {
  const [notes, setNotes] = useState<NoteEntry[]>([]);
  const [selectedNote, setSelectedNote] = useState<NoteEntry | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [sortBy, setSortBy] = useState<SortCategory>("updated");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

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

  // Sort notes based on current sort settings
  const sortedNotes = useMemo(() => {
    const sorted = [...notes].sort((a, b) => {
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
  }, [notes, sortBy, sortDirection]);

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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
      {/* Notes List - Left Side */}
      <div className="lg:col-span-3 min-h-0 flex flex-col">
        <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon h-full flex flex-col">
          <div className="mb-4 pb-4 border-b border-terminal-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <h2 className="text-lg font-bold text-neon-green font-mono">
                  NOTES
                </h2>
                <button
                  onClick={createNewNote}
                  className="p-2 bg-neon-green text-background rounded hover:bg-neon-green/80 transition-all hover:scale-110"
                  title="Create new note"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2.5}
                    stroke="currentColor"
                    className="w-4 h-4"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
                    />
                  </svg>
                </button>
              </div>

              {/* Sort Controls */}
              <div className="flex items-center gap-2 text-xs">
                <span className="text-text-muted font-mono">Sort:</span>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value as SortCategory)}
                  className="bg-background-tertiary border border-terminal-border rounded px-2 py-1 text-text-secondary font-mono focus:outline-none focus:border-neon-green cursor-pointer"
                >
                  <option value="updated">Date Updated</option>
                  <option value="created">Date Created</option>
                  <option value="title">Alphabetically</option>
                </select>
                <button
                  onClick={() =>
                    setSortDirection(prev => (prev === "asc" ? "desc" : "asc"))
                  }
                  className="bg-background-tertiary border border-terminal-border rounded px-2 py-1 text-text-secondary font-mono hover:border-text-primary transition-colors"
                  title={sortDirection === "asc" ? "Ascending" : "Descending"}
                >
                  {sortDirection === "asc" ? "↑" : "↓"}
                </button>
              </div>
            </div>
          </div>

          {isLoading && (
            <div className="text-text-secondary text-center font-mono text-sm">
              Loading...
            </div>
          )}

          {error && (
            <div className="text-neon-red text-sm mb-4 p-3 border border-neon-red rounded font-mono">
              {error}
            </div>
          )}

          <div className="flex-1 overflow-y-auto space-y-2 min-h-0">
            {sortedNotes.map(note => (
              <div
                key={note.id}
                onClick={() => handleNoteSelect(note)}
                className={`
                  p-4 border rounded cursor-pointer transition-all duration-200
                  ${
                    selectedNote?.id === note.id
                      ? "border-neon-green bg-background-tertiary"
                      : "border-terminal-border hover:border-text-secondary hover:bg-background-secondary"
                  }
                `}
              >
                <h3 className="font-bold text-text-primary truncate font-mono">
                  {note.title}
                </h3>
                <p className="text-text-muted text-sm mt-1 line-clamp-2 font-mono">
                  {note.content || "No content"}
                </p>
                <p className="text-text-muted text-xs mt-2 font-mono opacity-60">
                  {note.time_updated > 0
                    ? `Updated: ${formatTimestamp(note.time_updated)}`
                    : "Not saved"}
                </p>
              </div>
            ))}

            {!isLoading && notes.length === 0 && (
              <div className="text-text-muted text-center py-8 font-mono text-sm">
                No notes yet. Create your first one!
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Note Editor - Right Side */}
      <div className="lg:col-span-9 min-h-0 flex flex-col">
        <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon h-full flex flex-col">
          {selectedNote ? (
            <>
              <div className="mb-4 pb-4 border-b border-terminal-border">
                <input
                  type="text"
                  value={selectedNote.title}
                  onChange={e => handleTitleChange(e.target.value)}
                  className="w-full bg-background-secondary border border-terminal-border rounded px-4 py-2 text-text-primary font-bold text-xl focus:outline-none focus:border-neon-green font-mono"
                  placeholder="Note Title"
                />
                {selectedNote.id !== null && (
                  <div className="mt-2 flex gap-4 text-xs text-text-muted font-mono opacity-60">
                    <span>
                      Created: {formatTimestamp(selectedNote.time_created)}
                    </span>
                    <span>
                      Updated: {formatTimestamp(selectedNote.time_updated)}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex-1 overflow-y-auto min-h-0">
                <textarea
                  value={selectedNote.content}
                  onChange={e => handleContentChange(e.target.value)}
                  className="w-full h-full bg-background-secondary border border-terminal-border rounded px-4 py-3 text-text-secondary focus:outline-none focus:border-neon-green resize-none font-mono"
                  placeholder="Note content..."
                />
              </div>

              <div className="mt-4 pt-4 border-t border-terminal-border flex gap-2">
                <button
                  onClick={handleCopy}
                  className="px-4 py-2 bg-background-tertiary text-text-secondary border border-terminal-border rounded hover:border-text-primary transition-colors font-mono"
                  disabled={isSaving}
                >
                  Copy
                </button>
                <button
                  onClick={handleSave}
                  className="px-6 py-2 bg-neon-green text-background font-medium rounded hover:bg-neon-green/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-mono"
                  disabled={isSaving}
                >
                  {isSaving
                    ? "Saving..."
                    : selectedNote.id === null
                      ? "Create"
                      : "Update"}
                </button>
                {selectedNote.id !== null && (
                  <button
                    onClick={handleDelete}
                    className="px-6 py-2 bg-neon-red text-background font-medium rounded hover:bg-neon-red/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-mono"
                    disabled={isSaving}
                  >
                    {isSaving ? "Deleting..." : "Delete"}
                  </button>
                )}
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-text-muted font-mono gap-4">
              <p>Select a note or create a new one to get started</p>
              <button
                onClick={createNewNote}
                className="px-6 py-2 bg-neon-green text-background font-medium rounded hover:bg-neon-green/80 transition-colors"
              >
                + New Entry
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
