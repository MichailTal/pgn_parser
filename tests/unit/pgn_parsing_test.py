from pgn

pgn_test_01 = """
[Event "Casual Game"]
[Site "Hamburg"]
[Date "2023.12.01"]
[White "Alice"]
[Black "Bob"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0
"""

invalid_pgn = """[Event "Invalid Game"]
1. e4 ?? Nc6 ?"""

empty_pgn = ""

def test_parse_pgn(pgn: str) -> None:
    """Test the ability to parse a valid pgn file"""
    assert pgn.metadata[0] == ("Event", "Casual Game")
    assert pgn.metadata[1] == ("Site", "Hamburg")
    assert "e4" in pgn.moves
    assert "Nc6" in pgn.moves