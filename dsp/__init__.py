"""DSP académico 3P+N: Clarke αβ0, PLL a tensión y extracción por secuencia."""

from .core import (
    CHANNEL_IA,
    CHANNEL_IB,
    CHANNEL_IC,
    CHANNEL_IN,
    CHANNEL_VA,
    CHANNEL_VB,
    CHANNEL_VC,
    NUM_CHANNELS,
    BlockDspController,
    DSPResult,
    clarke_ab0,
    inverse_clarke,
    rms,
    thdi_percent,
)
from .patterns import PatternSpec, generate_pattern_batch, pattern_catalog

__all__ = [
    "CHANNEL_IA",
    "CHANNEL_IB",
    "CHANNEL_IC",
    "CHANNEL_IN",
    "CHANNEL_VA",
    "CHANNEL_VB",
    "CHANNEL_VC",
    "NUM_CHANNELS",
    "BlockDspController",
    "DSPResult",
    "PatternSpec",
    "clarke_ab0",
    "generate_pattern_batch",
    "inverse_clarke",
    "pattern_catalog",
    "rms",
    "thdi_percent",
]
