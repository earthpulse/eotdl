import re

from ..errors import (
    NameCharsValidationError,
    NameLengthValidationError,
    DescriptionLengthValidationError,
)

def validate_name(
    name: str,
    regex: str = "^[^a-zA-Z]{1}|[^a-zA-Z0-9-]",
    max_length: int = 45,
    min_length: int = 3,
) -> str:
    if re.findall(regex, name):
        raise NameCharsValidationError()
    if len(name) > max_length or len(name) < min_length:
        raise NameLengthValidationError(max_length, min_length)
    return name


def validate_description(
    description: str, max_length: int = 50, min_length: int = 5
) -> str:
    if len(description) > max_length or len(description) < min_length:
        raise DescriptionLengthValidationError(max_length, min_length)
    return description
