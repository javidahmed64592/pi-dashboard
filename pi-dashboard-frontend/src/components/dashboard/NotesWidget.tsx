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
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

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

  // Auto-select first note if none selected but notes exist
  useEffect(() => {
    if (!selectedNote && notes.length > 0) {
      selectNote(notes[0]!);
    }
  }, [notes, selectedNote, selectNote]);

  const handleNewNote = async () => {
    try {
      const newNote = await createNewNote({
        title: "New Note",
        content: "",
      });
      selectNote(newNote);
      setSaveMessage("Note created!");
      setTimeout(() => setSaveMessage(null), 2000);
    } catch {
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
    } catch {
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
    } catch {
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
        <h2 className="text-lg font-bold text-neon-green font-mono mb-4">
          NOTES
        </h2>
        <div className="flex items-center justify-center h-40 text-text-muted font-mono text-sm">
          Loading notes...
        </div>
      </div>
    );
  }

  if (notesError) {
    return (
      <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
        <h2 className="text-lg font-bold text-neon-green font-mono mb-4">
          NOTES
        </h2>
        <div className="flex items-center justify-center h-40 text-neon-red font-mono text-sm">
          Error: {notesError}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-neon-green font-mono">NOTES</h2>
        <button
          onClick={handleNewNote}
          className="px-3 py-1 text-xs font-mono bg-neon-green text-background rounded hover:bg-opacity-80 transition-all"
        >
          + New
        </button>
      </div>

      {notes.length === 0 && !selectedNote && (
        <div className="flex items-center justify-center h-40 text-text-muted font-mono text-sm">
          No notes yet. Click &quot;+ New&quot; to create one.
        </div>
      )}

      {(selectedNote || notes.length > 0) && (
        <div className="flex flex-col min-h-0">
          {/* Combined note selector and title editor */}
          <div className="mb-3 relative">
            {notes.length >= 1 ? (
              <div className="relative">
                {isEditingTitle ? (
                  <>
                    <input
                      type="text"
                      value={title}
                      onChange={e => setTitle(e.target.value)}
                      onBlur={() => setIsEditingTitle(false)}
                      onKeyDown={e => {
                        if (e.key === "Enter") {
                          setIsEditingTitle(false);
                          handleSave();
                        }
                        if (e.key === "Escape") {
                          setIsEditingTitle(false);
                          setTitle(selectedNote?.title || "");
                        }
                      }}
                      autoFocus
                      placeholder="Note title..."
                      className="w-full px-3 py-2 pr-8 text-sm font-mono bg-background-tertiary text-neon-green border border-border rounded focus:outline-none focus:border-neon-green transition-colors"
                    />
                    <button
                      onClick={() => {
                        setIsEditingTitle(false);
                        handleSave();
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-neon-green hover:text-text-secondary transition-colors"
                      title="Save title"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </button>
                  </>
                ) : (
                  <>
                    {notes.length > 1 ? (
                      <>
                        <div
                          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                          className="w-full px-3 py-2 pr-16 text-sm font-mono bg-background-tertiary text-neon-green border border-border rounded focus:outline-none focus:border-neon-green transition-colors cursor-pointer"
                        >
                          {selectedNote?.title || "Select a note..."}
                        </div>
                        {isDropdownOpen && (
                          <div className="absolute top-full left-0 right-0 mt-1 bg-background-tertiary border border-border rounded shadow-lg z-10 max-h-60 overflow-y-auto">
                            {notes.map(note => (
                              <div
                                key={note.id}
                                onClick={() => {
                                  handleNoteSelect(note.id);
                                  setIsDropdownOpen(false);
                                }}
                                className={`px-3 py-2 text-sm font-mono cursor-pointer transition-all ${
                                  selectedNote?.id === note.id
                                    ? "bg-neon-green text-background"
                                    : "text-neon-green hover:border-l-2 hover:border-neon-green hover:bg-background-tertiary"
                                }`}
                              >
                                {note.title}
                              </div>
                            ))}
                          </div>
                        )}
                        <div className="absolute right-8 top-1/2 -translate-y-1/2 flex items-center gap-1">
                          <button
                            onClick={() => setIsEditingTitle(true)}
                            className="text-text-muted hover:text-neon-green transition-colors"
                            title="Edit title"
                          >
                            <svg
                              className="w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                              />
                            </svg>
                          </button>
                        </div>
                        <button
                          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted"
                        >
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 9l-7 7-7-7"
                            />
                          </svg>
                        </button>
                      </>
                    ) : (
                      <>
                        <div className="w-full px-3 py-2 pr-8 text-sm font-mono bg-background-tertiary text-neon-green border border-border rounded">
                          {selectedNote?.title || "Untitled"}
                        </div>
                        <button
                          onClick={() => setIsEditingTitle(true)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted hover:text-neon-green transition-colors"
                          title="Edit title"
                        >
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                            />
                          </svg>
                        </button>
                      </>
                    )}
                  </>
                )}
              </div>
            ) : (
              <input
                type="text"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="Note title..."
                className="w-full px-3 py-2 text-sm font-mono bg-background-tertiary text-text-primary border border-border rounded focus:outline-none focus:border-neon-green transition-colors"
              />
            )}
          </div>

          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            className="w-full h-40 px-3 py-2 text-sm font-mono bg-background-tertiary text-text-primary border border-border rounded resize-none focus:outline-none focus:border-neon-green transition-colors mb-3"
            placeholder="Write your note here..."
          />

          <div className="flex gap-2">
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
        </div>
      )}
    </div>
  );
}
