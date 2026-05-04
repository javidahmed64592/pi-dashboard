import { render, screen, fireEvent } from "@testing-library/react";

import NoteEditor from "@/components/notes/NoteEditor";
import type { NoteEntry } from "@/lib/types";

describe("NoteEditor", () => {
  const mockNote: NoteEntry = {
    id: 1,
    title: "Test Note",
    content: "Test content",
    time_created: 1715000000,
    time_updated: 1715100000,
  };

  const mockProps = {
    note: mockNote,
    onTitleChange: jest.fn(),
    onContentChange: jest.fn(),
    onSave: jest.fn(),
    onDelete: jest.fn(),
    onCopy: jest.fn(),
    onPasteAndSave: jest.fn(),
    onCreateNew: jest.fn(),
    isSaving: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("shows empty state when no note is selected", () => {
    render(<NoteEditor {...mockProps} note={null} />);

    expect(
      screen.getByText("Select a note or create a new one to get started")
    ).toBeInTheDocument();
    expect(screen.getByText("+ New Entry")).toBeInTheDocument();
  });

  it("calls onCreateNew when empty state button is clicked", () => {
    render(<NoteEditor {...mockProps} note={null} />);

    const button = screen.getByText("+ New Entry");
    fireEvent.click(button);

    expect(mockProps.onCreateNew).toHaveBeenCalledTimes(1);
  });

  it("renders title input with note title", () => {
    render(<NoteEditor {...mockProps} />);

    const titleInput = screen.getByDisplayValue("Test Note");
    expect(titleInput).toBeInTheDocument();
  });

  it("calls onTitleChange when title is edited", () => {
    render(<NoteEditor {...mockProps} />);

    const titleInput = screen.getByDisplayValue("Test Note");
    fireEvent.change(titleInput, { target: { value: "New Title" } });

    expect(mockProps.onTitleChange).toHaveBeenCalledWith("New Title");
  });

  it("renders content textarea with note content", () => {
    render(<NoteEditor {...mockProps} />);

    const contentTextarea = screen.getByDisplayValue("Test content");
    expect(contentTextarea).toBeInTheDocument();
  });

  it("calls onContentChange when content is edited", () => {
    render(<NoteEditor {...mockProps} />);

    const contentTextarea = screen.getByDisplayValue("Test content");
    fireEvent.change(contentTextarea, { target: { value: "New content" } });

    expect(mockProps.onContentChange).toHaveBeenCalledWith("New content");
  });

  it("displays timestamps for saved notes", () => {
    render(<NoteEditor {...mockProps} />);

    expect(screen.getByText(/Created:/)).toBeInTheDocument();
    expect(screen.getByText(/Updated:/)).toBeInTheDocument();
  });

  it("does not display timestamps for unsaved notes", () => {
    const unsavedNote = { ...mockNote, id: null };
    render(<NoteEditor {...mockProps} note={unsavedNote} />);

    expect(screen.queryByText(/Created:/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Updated:/)).not.toBeInTheDocument();
  });

  it("renders Copy button", () => {
    render(<NoteEditor {...mockProps} />);

    expect(screen.getByText("Copy")).toBeInTheDocument();
  });

  it("calls onCopy when Copy button is clicked", () => {
    render(<NoteEditor {...mockProps} />);

    const copyButton = screen.getByText("Copy");
    fireEvent.click(copyButton);

    expect(mockProps.onCopy).toHaveBeenCalledTimes(1);
  });

  it("shows Update button for saved notes", () => {
    render(<NoteEditor {...mockProps} />);

    expect(screen.getByText("Update")).toBeInTheDocument();
  });

  it("shows Create button for unsaved notes", () => {
    const unsavedNote = { ...mockNote, id: null };
    render(<NoteEditor {...mockProps} note={unsavedNote} />);

    expect(screen.getByText("Create")).toBeInTheDocument();
  });

  it("calls onSave when save button is clicked", () => {
    render(<NoteEditor {...mockProps} />);

    const saveButton = screen.getByText("Update");
    fireEvent.click(saveButton);

    expect(mockProps.onSave).toHaveBeenCalledTimes(1);
  });

  it("shows Delete button for saved notes", () => {
    render(<NoteEditor {...mockProps} />);

    expect(screen.getByText("Delete")).toBeInTheDocument();
  });

  it("does not show Delete button for unsaved notes", () => {
    const unsavedNote = { ...mockNote, id: null };
    render(<NoteEditor {...mockProps} note={unsavedNote} />);

    expect(screen.queryByText("Delete")).not.toBeInTheDocument();
  });

  it("calls onDelete when Delete button is clicked", () => {
    render(<NoteEditor {...mockProps} />);

    const deleteButton = screen.getByText("Delete");
    fireEvent.click(deleteButton);

    expect(mockProps.onDelete).toHaveBeenCalledTimes(1);
  });

  it("shows Paste + Save button for unsaved notes", () => {
    const unsavedNote = { ...mockNote, id: null };
    render(<NoteEditor {...mockProps} note={unsavedNote} />);

    expect(screen.getByText("Paste + Save")).toBeInTheDocument();
  });

  it("does not show Paste + Save button for saved notes", () => {
    render(<NoteEditor {...mockProps} />);

    expect(screen.queryByText("Paste + Save")).not.toBeInTheDocument();
  });

  it("calls onPasteAndSave when Paste + Save button is clicked", () => {
    const unsavedNote = { ...mockNote, id: null };
    render(<NoteEditor {...mockProps} note={unsavedNote} />);

    const pasteButton = screen.getByText("Paste + Save");
    fireEvent.click(pasteButton);

    expect(mockProps.onPasteAndSave).toHaveBeenCalledTimes(1);
  });

  it("shows Saving... text when isSaving is true", () => {
    render(<NoteEditor {...mockProps} isSaving={true} />);

    expect(screen.getByText("Saving...")).toBeInTheDocument();
  });

  it("disables buttons when isSaving is true", () => {
    render(<NoteEditor {...mockProps} isSaving={true} />);

    const copyButton = screen.getByText("Copy");
    const saveButton = screen.getByText("Saving...");

    expect(copyButton).toBeDisabled();
    expect(saveButton).toBeDisabled();
  });
});
