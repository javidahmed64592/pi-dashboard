import { render, screen, fireEvent } from "@testing-library/react";

import NotesList from "@/components/notes/NotesList";
import type { NoteEntry } from "@/lib/types";

describe("NotesList", () => {
  const mockNotes: NoteEntry[] = [
    {
      id: 1,
      title: "Test Note 1",
      content: "This is test content",
      time_created: 1715000000,
      time_updated: 1715100000,
    },
    {
      id: 2,
      title: "Test Note 2",
      content: "Another test note",
      time_created: 1715200000,
      time_updated: 1715300000,
    },
  ];

  const mockProps = {
    notes: mockNotes,
    selectedNote: null,
    onSelectNote: jest.fn(),
    isLoading: false,
    error: null,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders list of notes", () => {
    render(<NotesList {...mockProps} />);

    expect(screen.getByText("Test Note 1")).toBeInTheDocument();
    expect(screen.getByText("Test Note 2")).toBeInTheDocument();
  });

  it("displays note content preview", () => {
    render(<NotesList {...mockProps} />);

    expect(screen.getByText("This is test content")).toBeInTheDocument();
    expect(screen.getByText("Another test note")).toBeInTheDocument();
  });

  it("calls onSelectNote when a note is clicked", () => {
    render(<NotesList {...mockProps} />);

    const noteCard = screen.getByText("Test Note 1").closest("div");
    fireEvent.click(noteCard!);

    expect(mockProps.onSelectNote).toHaveBeenCalledWith(mockNotes[0]);
  });

  it("highlights selected note", () => {
    render(<NotesList {...mockProps} selectedNote={mockNotes[0]!} />);

    const selectedCard = screen.getByText("Test Note 1").closest("div");
    expect(selectedCard).toHaveClass("border-neon-green");
  });

  it("shows loading state", () => {
    render(<NotesList {...mockProps} isLoading={true} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("shows error message when error occurs", () => {
    render(<NotesList {...mockProps} error="Failed to load notes" />);

    expect(screen.getByText("Failed to load notes")).toBeInTheDocument();
  });

  it("shows empty state when no notes exist", () => {
    render(<NotesList {...mockProps} notes={[]} />);

    expect(
      screen.getByText("No notes yet. Create your first one!")
    ).toBeInTheDocument();
  });

  it("displays updated timestamp for notes", () => {
    render(<NotesList {...mockProps} />);

    expect(screen.getAllByText(/Updated:/)[0]).toBeInTheDocument();
  });
});
