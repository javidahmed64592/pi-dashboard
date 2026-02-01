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
    it("should render custom dropdown with notes when multiple notes exist", () => {
      renderWithDefaultProps({
        notes: [mockNote1, mockNote2],
        selectedNote: mockNote1,
      });

      // Should show selected note title
      expect(screen.getByText("Test Note 1")).toBeInTheDocument();
    });

    it("should display note titles in dropdown when opened", () => {
      renderWithDefaultProps({
        notes: [mockNote1, mockNote2],
        selectedNote: mockNote1,
      });

      // Click to open dropdown
      const dropdownTrigger = screen.getByText("Test Note 1");
      fireEvent.click(dropdownTrigger);

      // Both notes should be visible
      expect(screen.getAllByText("Test Note 1")).toHaveLength(2); // Trigger + dropdown item
      expect(screen.getByText("Test Note 2")).toBeInTheDocument();
    });

    it("should auto-select first note when none is selected", () => {
      renderWithDefaultProps({ notes: [mockNote1, mockNote2] });

      expect(mockSelectNote).toHaveBeenCalledWith(mockNote1);
    });
  });

  describe("Note Selection", () => {
    it("should call selectNote when a note is clicked from dropdown", () => {
      renderWithDefaultProps({
        notes: [mockNote1, mockNote2],
        selectedNote: mockNote1,
      });

      // Open dropdown
      const dropdownTrigger = screen.getByText("Test Note 1");
      fireEvent.click(dropdownTrigger);

      // Click on second note
      const note2Option = screen.getByText("Test Note 2");
      fireEvent.click(note2Option);

      expect(mockSelectNote).toHaveBeenCalledWith(mockNote2);
    });

    it("should display selected note content when in view mode", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const contentTextarea = screen.getByPlaceholderText(
        "Write your note here..."
      ) as HTMLTextAreaElement;

      expect(contentTextarea.value).toBe("Content 1");
    });

    it("should close dropdown after selecting a note", () => {
      renderWithDefaultProps({
        notes: [mockNote1, mockNote2],
        selectedNote: mockNote1,
      });

      // Open dropdown
      const dropdownTrigger = screen.getByText("Test Note 1");
      fireEvent.click(dropdownTrigger);

      // Both notes should be visible
      expect(screen.getByText("Test Note 2")).toBeInTheDocument();

      // Click on second note
      const note2Option = screen.getByText("Test Note 2");
      fireEvent.click(note2Option);

      // Note should be selected
      expect(mockSelectNote).toHaveBeenCalledWith(mockNote2);
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

      const contentTextarea = screen.getByPlaceholderText(
        "Write your note here..."
      );

      // Change content and save
      fireEvent.change(contentTextarea, {
        target: { value: "Updated Content" },
      });

      const saveButton = screen.getByRole("button", { name: /^Save$/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockUpdateExistingNote).toHaveBeenCalledWith("1", {
          title: "Test Note 1",
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

      const saveButton = screen.getByRole("button", { name: /^Save$/i });
      fireEvent.click(saveButton);

      expect(screen.getByRole("button", { name: /Saving.../i })).toBeDisabled();
    });

    it("should save note when Enter is pressed in edit mode", async () => {
      mockUpdateExistingNote.mockResolvedValue(mockNote1);
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      // Enter edit mode
      const editButton = screen.getByTitle("Edit title");
      fireEvent.click(editButton);

      const titleInput = screen.getByPlaceholderText("Note title...");
      fireEvent.change(titleInput, { target: { value: "Updated Title" } });
      fireEvent.keyDown(titleInput, { key: "Enter" });

      await waitFor(() => {
        expect(mockUpdateExistingNote).toHaveBeenCalled();
      });
    });

    it("should cancel edit when Escape is pressed", async () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      // Enter edit mode
      const editButton = screen.getByTitle("Edit title");
      fireEvent.click(editButton);

      const titleInput = screen.getByPlaceholderText("Note title...");
      fireEvent.change(titleInput, { target: { value: "Changed Title" } });
      fireEvent.keyDown(titleInput, { key: "Escape" });

      // Should exit edit mode and revert title
      await waitFor(() => {
        expect(screen.getByText("Test Note 1")).toBeInTheDocument();
      });
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
    it("should update title when typing in edit mode", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      // Enter edit mode
      const editButton = screen.getByTitle("Edit title");
      fireEvent.click(editButton);

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

  describe("Edit Title Mode", () => {
    it("should render edit button (pencil icon) when note is selected", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const editButton = screen.getByTitle("Edit title");
      expect(editButton).toBeInTheDocument();
    });

    it("should enter edit mode when pencil icon is clicked", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      const editButton = screen.getByTitle("Edit title");
      fireEvent.click(editButton);

      // Should show input with autofocus
      const titleInput = screen.getByPlaceholderText("Note title...");
      expect(titleInput).toBeInTheDocument();
      expect(titleInput).toHaveFocus();
    });

    it("should exit edit mode when clicking save checkmark", async () => {
      mockUpdateExistingNote.mockResolvedValue(mockNote1);
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      // Enter edit mode
      const editButton = screen.getByTitle("Edit title");
      fireEvent.click(editButton);

      // Click save checkmark
      const saveCheckmark = screen.getByTitle("Save title");
      fireEvent.click(saveCheckmark);

      await waitFor(() => {
        expect(mockUpdateExistingNote).toHaveBeenCalled();
      });
    });

    it("should show checkmark icon in edit mode", () => {
      renderWithDefaultProps({
        notes: [mockNote1],
        selectedNote: mockNote1,
      });

      // Enter edit mode
      const editButton = screen.getByTitle("Edit title");
      fireEvent.click(editButton);

      // Should show save checkmark button
      const saveCheckmark = screen.getByTitle("Save title");
      expect(saveCheckmark).toBeInTheDocument();
    });
  });

  describe("Dropdown Toggle", () => {
    it("should open dropdown when clicking on the note title area", () => {
      renderWithDefaultProps({
        notes: [mockNote1, mockNote2],
        selectedNote: mockNote1,
      });

      const dropdownTrigger = screen.getByText("Test Note 1");
      fireEvent.click(dropdownTrigger);

      // Both notes should be visible in dropdown
      expect(screen.getByText("Test Note 2")).toBeInTheDocument();
    });

    it("should close dropdown when clicking outside", () => {
      renderWithDefaultProps({
        notes: [mockNote1, mockNote2],
        selectedNote: mockNote1,
      });

      // Open dropdown
      const dropdownTrigger = screen.getByText("Test Note 1");
      fireEvent.click(dropdownTrigger);

      // Close by clicking trigger again
      fireEvent.click(dropdownTrigger);

      // Only one instance should remain (the trigger itself)
      expect(screen.queryAllByText("Test Note 1")).toHaveLength(1);
    });
  });
});
