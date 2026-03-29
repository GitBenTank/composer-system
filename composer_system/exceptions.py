class ComposerSystemError(Exception):
    """Base error for composer-system operations."""


class ProfileValidationError(ComposerSystemError):
    """Raised when profile data does not match the shared schema."""


class ProfileLoadError(ComposerSystemError):
    """Raised when a profile cannot be read safely from disk."""
