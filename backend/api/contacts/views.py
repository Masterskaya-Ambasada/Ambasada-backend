from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.contacts.serializers import ContactRequestSerializer


class ContactCreateView(generics.CreateAPIView):
    """Вьюсет для формы обратной связи со встроенным антиспамом."""

    serializer_class = ContactRequestSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if request.data.get('contact_preference'):
            return Response({'detail': 'Received.'}, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({'detail': 'Received.'}, status=status.HTTP_201_CREATED)
