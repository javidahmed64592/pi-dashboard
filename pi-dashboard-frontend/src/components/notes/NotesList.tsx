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

interface NotesListProps {
  notes: NoteEntry[];
  selectedNote: NoteEntry | null;
  onSelectNote: (note: NoteEntry) => void;
  isLoading: boolean;
  error: string | null;
}

export default function NotesList({
  notes,
  selectedNote,
  onSelectNote,
  isLoading,
  error,
}: NotesListProps) {
  return (
    <>
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
        {notes.map(note => (
          <div
            key={note.id}
            onClick={() => onSelectNote(note)}
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
    </>
  );
}
