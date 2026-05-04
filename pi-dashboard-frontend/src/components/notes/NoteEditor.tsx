import type { NoteEntry } from "@/lib/types";

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

interface NoteEditorProps {
  note: NoteEntry | null;
  onTitleChange: (title: string) => void;
  onContentChange: (content: string) => void;
  onSave: () => void;
  onDelete: () => void;
  onCopy: () => void;
  onPasteAndSave: () => void;
  onCreateNew: () => void;
  isSaving: boolean;
}

export default function NoteEditor({
  note,
  onTitleChange,
  onContentChange,
  onSave,
  onDelete,
  onCopy,
  onPasteAndSave,
  onCreateNew,
  isSaving,
}: NoteEditorProps) {
  if (!note) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-text-muted font-mono gap-4">
        <p>Select a note or create a new one to get started</p>
        <button
          onClick={onCreateNew}
          className="px-6 py-2 bg-neon-green text-background font-medium rounded hover:bg-neon-green/80 transition-colors"
        >
          + New Entry
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="mb-4 pb-4 border-b border-terminal-border">
        <input
          type="text"
          value={note.title}
          onChange={e => onTitleChange(e.target.value)}
          className="w-full bg-background-secondary border border-terminal-border rounded px-4 py-2 text-text-primary font-bold text-xl focus:outline-none focus:border-neon-green font-mono"
          placeholder="Note Title"
        />
        {note.id !== null && (
          <div className="mt-2 flex gap-4 text-xs text-text-muted font-mono opacity-60">
            <span>Created: {formatTimestamp(note.time_created)}</span>
            <span>Updated: {formatTimestamp(note.time_updated)}</span>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto min-h-0">
        <textarea
          value={note.content}
          onChange={e => onContentChange(e.target.value)}
          className="w-full h-full bg-background-secondary border border-terminal-border rounded px-4 py-3 text-text-secondary focus:outline-none focus:border-neon-green resize-none font-mono"
          placeholder="Note content..."
        />
      </div>

      <div className="mt-4 pt-4 border-t border-terminal-border flex gap-2">
        <button
          onClick={onCopy}
          className="px-4 py-2 bg-background-tertiary text-text-secondary border border-terminal-border rounded hover:border-text-primary transition-colors font-mono"
          disabled={isSaving}
        >
          Copy
        </button>
        {note.id === null && (
          <button
            onClick={onPasteAndSave}
            className="px-4 py-2 bg-background-tertiary text-text-secondary border border-terminal-border rounded hover:border-text-primary transition-colors font-mono disabled:opacity-50"
            disabled={isSaving}
            title="Paste clipboard content and save"
          >
            Paste + Save
          </button>
        )}
        <button
          onClick={onSave}
          className="px-6 py-2 bg-neon-green text-background font-medium rounded hover:bg-neon-green/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-mono"
          disabled={isSaving}
        >
          {isSaving ? "Saving..." : note.id === null ? "Create" : "Update"}
        </button>
        {note.id !== null && (
          <button
            onClick={onDelete}
            className="px-6 py-2 bg-neon-red text-background font-medium rounded hover:bg-neon-red/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-mono"
            disabled={isSaving}
          >
            {isSaving ? "Deleting..." : "Delete"}
          </button>
        )}
      </div>
    </>
  );
}
