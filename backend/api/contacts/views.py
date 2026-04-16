from rest_framework import generics
from rest_framework.response import Response

from rest_framework import status

from api.constants.serializers import ContactRequestSerializer

class ContactCreateView(generics.CreateAPIView):
    '''Вьюсет для формы обратной связи со встроенным антиспамом'''

    serializer_class = ContactRequestSerializer

    def create(self, request, *args, **kwargs):
        if request.data.get('contact_preference'):
            return Response({'detail': 'Received.'}, status=status.HTTP_201_CREATED)

        return super().create(request, *args, **kwargs)