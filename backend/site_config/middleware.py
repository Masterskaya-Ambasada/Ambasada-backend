import threading

_thread_locals = threading.local()


def get_current_user():
    """Возвращает текущего пользователя из thread-local storage."""
    return getattr(_thread_locals, 'user', None)


class CurrentUserMiddleware:
    """Middleware для сохранения текущего пользователя в thread-local storage."""

    def __init__(self, get_response):
        """Инициализирует middleware с функцией получения следующего обработчика."""
        self.get_response = get_response

    def __call__(self, request):
        """Сохраняет пользователя из запроса в thread-local storage и передаёт запрос дальше."""
        _thread_locals.user = getattr(request, 'user', None)
        response = self.get_response(request)
        return response
