import pytest
import pgn_parser

VALID_PGN = """
[Event "Test Event"]
[Site "Test Site"]
[Date "2023.10.01"]
[Round "1"]
[White "Alice"]
[Black "Bob"]
[Result "1-0"]
1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6
"""

INVALID_PGN_MISSING_MOVES = """
[Event "Test Event"]
[Site "Test Site"]
"""

INVALID_PGN_MALFORMED_METADATA = """
[Event "Test Event"
[Site "Test Site"]
1. e4 e5
"""

PGN_WITH_COMMENTS = """
[Event "Test Event"]
[Site "Test Site"]
{This is a comment}
1. e4 {Best move!} e5 2. Nf3 Nc6
"""


def test_parse_valid_pgn():
    """Test parsing a valid PGN string."""
    reader = pgn_parser.parse_pgn(VALID_PGN)

    assert len(reader.metadata) == 7
    assert ("Event", "Test Event") in reader.metadata
    assert ("Site", "Test Site") in reader.metadata
    assert ("Date", "2023.10.01") in reader.metadata
    assert ("Round", "1") in reader.metadata
    assert ("White", "Alice") in reader.metadata
    assert ("Black", "Bob") in reader.metadata

    assert len(reader.moves) == 8
    assert "e4" in reader.moves
    assert "e5" in reader.moves
    assert "Nf3" in reader.moves
    assert "Nc6" in reader.moves
    assert "Bb5" in reader.moves
    assert "a6" in reader.moves
    assert "Ba4" in reader.moves
    assert "Nf6" in reader.moves


def test_parse_pgn_with_comments():
    """Test parsing a PGN string with comments and annotations."""
    reader = pgn_parser.parse_pgn(PGN_WITH_COMMENTS)

    assert len(reader.metadata) == 2
    assert ("Event", "Test Event") in reader.metadata
    assert ("Site", "Test Site") in reader.metadata

    assert len(reader.moves) == 4
    assert "e4" in reader.moves
    assert "e5" in reader.moves
    assert "Nf3" in reader.moves
    assert "Nc6" in reader.moves


def test_parse_invalid_pgn_missing_moves():
    """Test parsing a PGN string with no moves."""
    with pytest.raises(ValueError, match="Invalid metadata format in PGN"):
        pgn_parser.parse_pgn(INVALID_PGN_MISSING_MOVES)


def test_parse_invalid_pgn_malformed_metadata():
    """Test parsing a PGN string with malformed metadata."""
    with pytest.raises(ValueError, match="Invalid metadata format in PGN"):
        pgn_parser.parse_pgn(INVALID_PGN_MALFORMED_METADATA)


def test_parse_empty_pgn():
    """Test parsing an empty PGN string."""
    with pytest.raises(ValueError, match="PGN is empty"):
        pgn_parser.parse_pgn("")


def test_parse_pgn_with_invalid_move_format():
    """Test parsing a PGN string with invalid move formats."""
    invalid_pgn = """
    [Event "Test Event"]
    [Site "Test Site"]
    1. e4 invalid_move 2. Nf3 Nc6
    """
    reader = pgn_parser.parse_pgn(invalid_pgn)

    assert len(reader.metadata) == 2
    assert ("Event", "Test Event") in reader.metadata
    assert ("Site", "Test Site") in reader.metadata

    assert len(reader.moves) == 3
    assert "e4" in reader.moves
    assert "Nf3" in reader.moves
    assert "Nc6" in reader.moves