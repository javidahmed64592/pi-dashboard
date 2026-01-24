"use client";

import { useState } from "react";

export default function NotesWidget() {
  const [selectedNote, setSelectedNote] = useState("note-1");
  const [noteContent, setNoteContent] = useState(
    "This is a sample note. You can edit or create new notes here."
  );

  const notes = [
    { id: "note-1", title: "Sample Note" },
    { id: "note-2", title: "Todo List" },
    { id: "note-3", title: "Meeting Notes" },
  ];

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-neon-green font-mono">NOTES</h2>
        <button className="px-3 py-1 text-xs font-mono bg-neon-green text-background rounded hover:bg-opacity-80 transition-all">
          + New
        </button>
      </div>

      <div className="mb-3">
        <select
          value={selectedNote}
          onChange={e => setSelectedNote(e.target.value)}
          className="w-full px-3 py-2 text-sm font-mono bg-background-tertiary text-text-primary border border-border rounded focus:outline-none focus:border-neon-green transition-colors"
        >
          {notes.map(note => (
            <option key={note.id} value={note.id}>
              {note.title}
            </option>
          ))}
        </select>
      </div>

      <textarea
        value={noteContent}
        onChange={e => setNoteContent(e.target.value)}
        className="w-full h-40 px-3 py-2 text-sm font-mono bg-background-tertiary text-text-primary border border-border rounded resize-none focus:outline-none focus:border-neon-green transition-colors"
        placeholder="Write your note here..."
      />

      <div className="flex gap-2 mt-3">
        <button className="flex-1 px-3 py-2 text-xs font-mono bg-neon-green text-background rounded hover:bg-opacity-80 transition-all">
          Save
        </button>
        <button className="px-3 py-2 text-xs font-mono bg-neon-red text-background rounded hover:bg-opacity-80 transition-all">
          Delete
        </button>
      </div>
    </div>
  );
}
