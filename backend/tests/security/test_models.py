import pytest
from django.core.exceptions import ValidationError
from security.models import SecurityPolicy


@pytest.mark.django_db
class TestSecurityPolicyModel:
    """Тестирование логики синглтона модели SecurityPolicy."""

    def test_create_single_policy_success(self, privacy_policy_data):
        """Успешное создание политики."""
        policy = SecurityPolicy.objects.create(**privacy_policy_data)
        assert SecurityPolicy.objects.count() == 1
        assert policy.pk == 1
        assert policy.text_ru == privacy_policy_data['text_ru']

    def test_create_duplicate_policy_raises_error(self, sample_policy):
        """Попытка создать вторую запись вызывает ValidationError из-за жесткого ID=1."""
        assert SecurityPolicy.objects.count() == 1
        
        with pytest.raises(ValidationError) as exc_info:
            duplicate = SecurityPolicy(text_ru='Другой текст')
            duplicate.save()
        
        assert 'id' in exc_info.value.message_dict