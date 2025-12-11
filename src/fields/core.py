"""Core functionality for the Fields package."""


class Field:
    """A basic field class."""

    def __init__(self, name: str, value: any = None):
        """Initialize a field.

        Args:
            name: The name of the field
            value: The value of the field
        """
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"Field(name='{self.name}', value={self.value!r})"


