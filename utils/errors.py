"""Domain exceptions presented by the desktop interface."""


class CaminhoNaoEncontradoError(Exception):
    """Raised when no configured XML path is accessible."""


class KNRNaoEncontradoError(Exception):
    """Raised when no XML filename matches the requested identifier."""
