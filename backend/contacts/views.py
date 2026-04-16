from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from constants.models import ContactRequest
from constants.serializers import ContactRequestSerializer

class ContactCreateView(generics.CreateAPIView):
    '''Вьюсет для формы обратной связи со встроенным антиспамом'''

    def post(self, request):
        if request.data.get("contact_preference"):
            return Response({"detail": "Received."}, status=status.HTTP_201_CREATED)

        serializer = ContactRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ContactRequest.objects.create(**{
            k: v for k, v in serializer.validated_data.items()
        })
        return Response({"detail": "Received."}, status=status.HTTP_201_CREATED)
