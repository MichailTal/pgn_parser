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

def test_pgn_file_read():
    """Test the ability to open and read a .pgn file"""

    pgn_file_path: str = r"tests\pgn_files\Tal_Botvinnik.pgn"
    file_reader = pgn_parser.parse_single_pgn_file(pgn_file_path)

    assert "e4" in file_reader.moves
    assert "Nc3" in file_reader.moves
    assert "Qxg8" in file_reader.moves

    assert ("Event", "Wch23") in file_reader.metadata
    assert ("Site", "Moscow RUS") in file_reader.metadata

def test_unvalid_file_path():
    """Tests handing over an unvalid file path"""

    pgn_file_path: str = r"tests\pgn_files\Taaaaaal_Botvinnik.pgn"

    with pytest.raises(OSError):
        pgn_parser.parse_single_pgn_file(pgn_file_path)

def test_unvalid_file_extension():
    """Test the opening of an unsupported file type"""

    pgn_file_path: str = r"tests\pgn_files\Tal_Botvinnik.txt"

    with pytest.raises(OSError):
        pgn_parser.parse_single_pgn_file(pgn_file_path)