"use client";

import { useState, useEffect } from "react";

import { useData } from "@/contexts/DataContext";

export default function NotesWidget() {
  const {
    notes,
    selectedNote,
    isLoadingNotes,
    notesError,
    selectNote,
    createNewNote,
    updateExistingNote,
    deleteExistingNote,
  } = useData();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // Update form when selected note changes
  useEffect(() => {
    if (selectedNote) {
      setTitle(selectedNote.title);
      setContent(selectedNote.content);
    } else {
      setTitle("");
      setContent("");
    }
  }, [selectedNote]);

  const handleNewNote = async () => {
    try {
      const newNote = await createNewNote({
        title: "New Note",
        content: "",
      });
      selectNote(newNote);
      setSaveMessage("Note created!");
      setTimeout(() => setSaveMessage(null), 2000);
    } catch (error) {
      console.error("Failed to create note:", error);
      setSaveMessage("Failed to create note");
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };

  const handleSave = async () => {
    if (!selectedNote) {
      // Create new note if none selected
      await handleNewNote();
      return;
    }

    setIsSaving(true);
    setSaveMessage(null);
    try {
      await updateExistingNote(selectedNote.id, { title, content });
      setSaveMessage("Saved!");
      setTimeout(() => setSaveMessage(null), 2000);
    } catch (error) {
      console.error("Failed to save note:", error);
      setSaveMessage("Failed to save");
      setTimeout(() => setSaveMessage(null), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedNote) return;

    if (!confirm(`Delete "${selectedNote.title}"?`)) return;

    try {
      await deleteExistingNote(selectedNote.id);
      setSaveMessage("Deleted!");
      setTimeout(() => setSaveMessage(null), 2000);
    } catch (error) {
      console.error("Failed to delete note:", error);
      setSaveMessage("Failed to delete");
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };

  const handleNoteSelect = (noteId: string) => {
    const note = notes.find(n => n.id === noteId);
    selectNote(note || null);
  };

  if (isLoadingNotes) {
    return (
      <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
        <h2 className="text-lg font-bold text-neon-green font-mono mb-4">NOTES</h2>
        <div className="flex items-center justify-center h-40 text-text-muted font-mono text-sm">
          Loading notes...
        </div>
      </div>
    );
  }

  if (notesError) {
    return (
      <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
        <h2 className="text-lg font-bold text-neon-green font-mono mb-4">NOTES</h2>
        <div className="flex items-center justify-center h-40 text-neon-red font-mono text-sm">
          Error: {notesError}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-neon-green font-mono">NOTES</h2>
        <button
          onClick={handleNewNote}
          className="px-3 py-1 text-xs font-mono bg-neon-green text-background rounded hover:bg-opacity-80 transition-all"
        >
          + New
        </button>
      </div>

      {notes.length > 0 && (
        <div className="mb-3">
          <select
            value={selectedNote?.id || ""}
            onChange={e => handleNoteSelect(e.target.value)}
            className="w-full px-3 py-2 text-sm font-mono bg-background-tertiary text-text-primary border border-border rounded focus:outline-none focus:border-neon-green transition-colors"
          >
            <option value="" disabled>
              Select a note...
            </option>
            {notes.map(note => (
              <option key={note.id} value={note.id}>
                {note.title}
              </option>
            ))}
          </select>
        </div>
      )}

      {notes.length === 0 && !selectedNote && (
        <div className="flex items-center justify-center h-40 text-text-muted font-mono text-sm">
          No notes yet. Click &quot;+ New&quot; to create one.
        </div>
      )}

      {(selectedNote || notes.length > 0) && (
        <>
          <input
            type="text"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Note title..."
            className="w-full px-3 py-2 mb-3 text-sm font-mono bg-background-tertiary text-text-primary border border-border rounded focus:outline-none focus:border-neon-green transition-colors"
          />

          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            className="w-full h-40 px-3 py-2 text-sm font-mono bg-background-tertiary text-text-primary border border-border rounded resize-none focus:outline-none focus:border-neon-green transition-colors"
            placeholder="Write your note here..."
          />

          <div className="flex gap-2 mt-3">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex-1 px-3 py-2 text-xs font-mono bg-neon-green text-background rounded hover:bg-opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? "Saving..." : "Save"}
            </button>
            {selectedNote && (
              <button
                onClick={handleDelete}
                className="px-3 py-2 text-xs font-mono bg-neon-red text-background rounded hover:bg-opacity-80 transition-all"
              >
                Delete
              </button>
            )}
          </div>

          {saveMessage && (
            <div
              className={`mt-2 text-xs font-mono text-center ${
                saveMessage.includes("Failed") || saveMessage.includes("Error")
                  ? "text-neon-red"
                  : "text-neon-green"
              }`}
            >
              {saveMessage}
            </div>
          )}
        </>
      )}
    </div>
  );
}
