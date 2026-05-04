type SortCategory = "updated" | "created" | "title";

interface NotesHeaderProps {
  onCreateNew: () => void;
  sortBy: SortCategory;
  setSortBy: (value: SortCategory) => void;
  sortDirection: "asc" | "desc";
  setSortDirection: (value: "asc" | "desc") => void;
  searchQuery: string;
  setSearchQuery: (value: string) => void;
}

export default function NotesHeader({
  onCreateNew,
  sortBy,
  setSortBy,
  sortDirection,
  setSortDirection,
  searchQuery,
  setSearchQuery,
}: NotesHeaderProps) {
  return (
    <div className="mb-4 pb-4 border-b border-terminal-border">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-bold text-neon-green font-mono">NOTES</h2>
          <button
            onClick={onCreateNew}
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
              setSortDirection(sortDirection === "asc" ? "desc" : "asc")
            }
            className="bg-background-tertiary border border-terminal-border rounded px-2 py-1 text-text-secondary font-mono hover:border-text-primary transition-colors"
            title={sortDirection === "asc" ? "Ascending" : "Descending"}
          >
            {sortDirection === "asc" ? "↑" : "↓"}
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <input
          type="text"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          placeholder="Search notes..."
          className="w-full bg-background-tertiary border border-terminal-border rounded px-3 py-2 pl-9 text-text-secondary text-sm font-mono focus:outline-none focus:border-neon-green"
        />
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
          className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
          />
        </svg>
      </div>
    </div>
  );
}
