"""Advisory lexical lookup. Import submodules directly (lex.lookup, lex.contract)."""
from .contract import LexResult, LexEntry, Synonym
from .lookup import load_index, lookup

__all__ = ["LexResult", "LexEntry", "Synonym", "load_index", "lookup"]
