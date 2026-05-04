import { render, screen, fireEvent } from "@testing-library/react";

import NotesHeader from "@/components/notes/NotesHeader";

describe("NotesHeader", () => {
  const mockProps = {
    onCreateNew: jest.fn(),
    sortBy: "updated" as const,
    setSortBy: jest.fn(),
    sortDirection: "desc" as const,
    setSortDirection: jest.fn(),
    searchQuery: "",
    setSearchQuery: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the NOTES header", () => {
    render(<NotesHeader {...mockProps} />);

    expect(screen.getByText("NOTES")).toBeInTheDocument();
  });

  it("renders the create new note button", () => {
    render(<NotesHeader {...mockProps} />);

    const button = screen.getByTitle("Create new note");
    expect(button).toBeInTheDocument();
  });

  it("calls onCreateNew when create button is clicked", () => {
    render(<NotesHeader {...mockProps} />);

    const button = screen.getByTitle("Create new note");
    fireEvent.click(button);

    expect(mockProps.onCreateNew).toHaveBeenCalledTimes(1);
  });

  it("renders the search input", () => {
    render(<NotesHeader {...mockProps} />);

    const searchInput = screen.getByPlaceholderText("Search notes...");
    expect(searchInput).toBeInTheDocument();
  });

  it("calls setSearchQuery when search input changes", () => {
    render(<NotesHeader {...mockProps} />);

    const searchInput = screen.getByPlaceholderText("Search notes...");
    fireEvent.change(searchInput, { target: { value: "test query" } });

    expect(mockProps.setSearchQuery).toHaveBeenCalledWith("test query");
  });

  it("renders sort dropdown with correct value", () => {
    render(<NotesHeader {...mockProps} />);

    const sortSelect = screen.getByDisplayValue("Date Updated");
    expect(sortSelect).toBeInTheDocument();
  });

  it("calls setSortBy when sort option changes", () => {
    render(<NotesHeader {...mockProps} />);

    const sortSelect = screen.getByDisplayValue("Date Updated");
    fireEvent.change(sortSelect, { target: { value: "title" } });

    expect(mockProps.setSortBy).toHaveBeenCalled();
  });

  it("renders sort direction button with correct symbol", () => {
    render(<NotesHeader {...mockProps} />);

    const directionButton = screen.getByTitle("Descending");
    expect(directionButton).toHaveTextContent("↓");
  });

  it("calls setSortDirection when direction button is clicked", () => {
    render(<NotesHeader {...mockProps} />);

    const directionButton = screen.getByTitle("Descending");
    fireEvent.click(directionButton);

    expect(mockProps.setSortDirection).toHaveBeenCalled();
  });

  it("shows ascending symbol when sortDirection is asc", () => {
    render(<NotesHeader {...mockProps} sortDirection="asc" />);

    const directionButton = screen.getByTitle("Ascending");
    expect(directionButton).toHaveTextContent("↑");
  });
});
