"""
    Annotes annotator
"""

from engine.annotators.annotator_confidence_heat import AnnotatorConfidenceHeat
from engine.annotators.annotator_default import AnnotatorDefault
from engine.annote import Annote
from engine.annote_enums import AnnotatorType


class Annotator:
    """Annotes annotator"""

    @staticmethod
    def QtDraw(
        annote: Annote,
        painter,
        annotator_type: AnnotatorType = AnnotatorType.Default,
        highlight: bool = False,
        isConfidence: bool = True,
        isLabel: bool = True,
    ):
        """Draw self."""
        if annotator_type == AnnotatorType.Default:
            AnnotatorDefault.Draw(annote, painter, highlight, isConfidence, isLabel)
        elif annotator_type == AnnotatorType.ConfidenceHeat:
            AnnotatorConfidenceHeat.Draw(
                annote, painter, highlight, isConfidence, isLabel
            )
