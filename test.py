import pgn_parser

INVALID_PGN_MALFORMED_METADATA = """
[Event "Test Event"
[Site "Test Site"]
1. e4 e5
"""

reader = pgn_parser.parse_pgn("")

print(reader.metadata)

