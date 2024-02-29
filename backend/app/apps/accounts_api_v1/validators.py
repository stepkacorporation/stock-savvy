import re

from django.core.exceptions import ValidationError


def validate_username(username):
    if not username:
        raise ValidationError('Username must be provided.')
    if len(username) < 4:
        raise ValidationError('Username must be at least 4 characters long.')
    if len(username) > 20:
        raise ValidationError('Username cannot exceed 20 characters in length.')
    if not re.match(r'^[a-zA-Z-_]+$', username):
        raise ValidationError('Username can only contain letters, hyphens, and underscores.')
