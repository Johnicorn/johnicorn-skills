"""B1 spelling + B2 form-existence over a prepared index.
Import submodules directly (b.index, b.spelling, b.morphology, b.analyze, b.gate)."""
from .index import norm, Lexicon, WordformIndex, build_index, load_index, FORMAT_VERSION
from .spelling import spell_check
from .morphology import form_check, B2Result
from .analyze import analyze
from .gate import gate

__all__ = ["norm", "Lexicon", "WordformIndex", "build_index", "load_index", "FORMAT_VERSION",
           "spell_check", "form_check", "B2Result", "analyze", "gate"]
