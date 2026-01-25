import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import NotesWidget from "@/components/dashboard/NotesWidget";
import * as DataContext from "@/contexts/DataContext";
import type { Note } from "@/lib/types";

// Mock the DataContext
jest.mock("@/contexts/DataContext", () => ({
  ...jest.requireActual("@/contexts/DataContext"),
  useData: jest.fn(),
}));

const mockNote1: Note = {
  id: "1",
  title: "Test Note 1",
  content: "Content 1",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

const mockNote2: Note = {
  id: "2",
  title: "Test Note 2",
  content: "Content 2",
  created_at: "2024-01-02T00:00:00Z",
  updated_at: "2024-01-02T00:00:00Z",
};

const mockUseData = DataContext.useData as jest.MockedFunction<
  typeof DataContext.useData
>;

describe("NotesWidget", () => {
  const mockSelectNote = jest.fn();
  const mockCreateNewNote = jest.fn();
  const mockUpdateExistingNote = jest.fn();
  const mockDeleteExistingNote = jest.fn();
  const mockFetchNotes = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    // Clear any pending timers
    jest.clearAllTimers();
  });

  const renderWithDefaultProps = (overrides = {}) => {
    mockUseData.mockReturnValue({
      notes: [],
      selectedNote: null,
      isLoadingNotes: false,
      notesError: null,
      fetchNotes: mockFetchNotes,
      selectNote: mockSelectNote,
      createNewNote: mockCreateNewNote,
      updateExistingNote: mockUpdateExistingNote,
      deleteExistingNote: mockDeleteExistingNote,
      ...overrides,
    });

    return render(<NotesWidget />);
  };

  describe("Loading State", () => {
    it("should display loading message when loading notes", () => {
      renderWithDefaultProps({ isLoadingNotes: true });

      expect(screen.getByText("Loading notes...")).toBeInTheDocument();
    });
  });

  describe("Error State", () => {
    it("should display error message when there is an error", () => {
      const errorMessage = "Failed to fetch notes";
      renderWithDefaultProps({ notesError: errorMessage });

      expect(screen.getByText(`Error: ${errorMessage}`)).toBeInTheDocument();
    });
  });

  describe("Empty State", () => {
    it("should display empty message when there are no notes", () => {
      renderWithDefaultProps();

      expect(
        screen.getByText(/No notes yet\. Click "\+ New" to create one\./i)
      ).toBeInTheDocument();
    });

    it("should render + New button", () => {
      renderWithDefaultProps();

      const newButton = screen.getByRole("button", { name: /\+ New/i });
      expect(newButton).toBeInTheDocument();
    });
  });

  describe("Notes List", () => {
    it("should render dropdown with notes when notes exist", () => {
      renderWithDefaultProps({ notes: [mockNote1, mockNote2] });

      const dropdown = screen.getByRole("combobox");
      expect(dropdown).toBeInTheDocument();

      const options = screen.getAllByRole("option");
      expect(options).toHaveLength(3); // "Select a note..." + 2 notes
    });

    it("should display note titles in dropdown", () => {
      renderWithDefaultProps({ notes: [mockNote1, mockNote2] });

      expect(screen.getByText("Test Note 1")).toBeInTheDocument();
      expect(screen.getByText("Test Note 2")).toBeInTheDocument();
    });
  });

  describe("Note Selection", () => {
    it("should call selectNote when a note is selected from dropdown", () => {
      renderWithDefaultProps({ notes: [mockNote1, mockNote2] });

      const dropdown = screen.getByRole("combobox");
      fireEvent.change(dropdown, { target: { value: "1" } });

      expect(mockSelectNote).toHaveBeenCalledWith(mockNote1);
    });

    it("should display selected note content", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const titleInput = screen.getByPlaceholderText(
        "Note title..."
      ) as HTMLInputElement;
      const contentTextarea = screen.getByPlaceholderText(
        "Write your note here..."
      ) as HTMLTextAreaElement;

      expect(titleInput.value).toBe("Test Note 1");
      expect(contentTextarea.value).toBe("Content 1");
    });
  });

  describe("Create New Note", () => {
    it("should call createNewNote when + New button is clicked", async () => {
      mockCreateNewNote.mockResolvedValue(mockNote1);
      renderWithDefaultProps();

      const newButton = screen.getByRole("button", { name: /\+ New/i });
      fireEvent.click(newButton);

      await waitFor(() => {
        expect(mockCreateNewNote).toHaveBeenCalledWith({
          title: "New Note",
          content: "",
        });
      });
    });
  });

  describe("Save Note", () => {
    it("should call updateExistingNote when Save button is clicked", async () => {
      mockUpdateExistingNote.mockResolvedValue(mockNote1);
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const titleInput = screen.getByPlaceholderText("Note title...");
      const contentTextarea = screen.getByPlaceholderText(
        "Write your note here..."
      );
      const saveButton = screen.getByRole("button", { name: /Save/i });

      fireEvent.change(titleInput, { target: { value: "Updated Title" } });
      fireEvent.change(contentTextarea, {
        target: { value: "Updated Content" },
      });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockUpdateExistingNote).toHaveBeenCalledWith("1", {
          title: "Updated Title",
          content: "Updated Content",
        });
      });
    });

    it("should disable Save button while saving", async () => {
      mockUpdateExistingNote.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockNote1), 100))
      );
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const saveButton = screen.getByRole("button", { name: /Save/i });
      fireEvent.click(saveButton);

      expect(screen.getByRole("button", { name: /Saving.../i })).toBeDisabled();
    });
  });

  describe("Delete Note", () => {
    it("should render Delete button when note is selected", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const deleteButton = screen.getByRole("button", { name: /Delete/i });
      expect(deleteButton).toBeInTheDocument();
    });

    it("should not render Delete button when no note is selected", () => {
      renderWithDefaultProps({ notes: [mockNote1] });

      const deleteButton = screen.queryByRole("button", { name: /Delete/i });
      expect(deleteButton).not.toBeInTheDocument();
    });

    it("should show confirmation dialog before deleting", () => {
      const confirmSpy = jest.spyOn(window, "confirm").mockReturnValue(false);
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const deleteButton = screen.getByRole("button", { name: /Delete/i });
      fireEvent.click(deleteButton);

      expect(confirmSpy).toHaveBeenCalledWith('Delete "Test Note 1"?');
      expect(mockDeleteExistingNote).not.toHaveBeenCalled();

      confirmSpy.mockRestore();
    });

    it("should call deleteExistingNote when confirmed", async () => {
      const confirmSpy = jest.spyOn(window, "confirm").mockReturnValue(true);
      mockDeleteExistingNote.mockResolvedValue(undefined);
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const deleteButton = screen.getByRole("button", { name: /Delete/i });
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(mockDeleteExistingNote).toHaveBeenCalledWith("1");
      });

      confirmSpy.mockRestore();
    });
  });

  describe("Form Inputs", () => {
    it("should update title when typing", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const titleInput = screen.getByPlaceholderText(
        "Note title..."
      ) as HTMLInputElement;
      fireEvent.change(titleInput, { target: { value: "New Title" } });

      expect(titleInput.value).toBe("New Title");
    });

    it("should update content when typing", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const contentTextarea = screen.getByPlaceholderText(
        "Write your note here..."
      ) as HTMLTextAreaElement;
      fireEvent.change(contentTextarea, {
        target: { value: "New content" },
      });

      expect(contentTextarea.value).toBe("New content");
    });
  });
});
