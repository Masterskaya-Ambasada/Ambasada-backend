from django.core.validators import MaxLengthValidator
from django.db import models

from contacts.constants import MAX_MESSAGE_LENGTH, MAX_NAME_LENGTH, MAX_REASON_LENGTH


class ContactRequest(models.Model):
    '''Модель для формы обратной связи'''

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    email = models.EmailField()
    message = models.TextField(validators=[MaxLengthValidator(MAX_MESSAGE_LENGTH)])
    reason = models.CharField(max_length=MAX_REASON_LENGTH)

    def __str__(self):
        return f'{self.name} <{self.email}> - {self.reason}'
