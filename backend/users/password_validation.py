from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MaximumLengthValidator:
    def __init__(self, max_length=150):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _('Пароль должен быть не более чем %(max_length)d символов.'),
                code='password_too_short',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return _(
            'Ваш пароль должен быть максимум %(max_length)d символов.'
            % {'max_length': self.max_length}
        )
