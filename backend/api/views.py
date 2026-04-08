"""APIView для получения данных страницы 'О нас'."""

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Value, TeamMember, GalleryImage, AboutPage
from .serializers import ValueSerializer, TeamMemberSerializer, GalleryImageSerializer, AboutPageSerializer

class AboutAPIView(APIView):
    """Возвращает структуру страницы 'О сообществе' согласно ТЗ."""
    def get(self, request):
        about = AboutPage.objects.first()
        if not about:
            about = AboutPage.objects.create(
                hero_title="О сообществе",
                hero_description="Краткий вводный текст или слоган",
                about_title="О нас",
                paragraph_1="Первый сегмент текста о миссии сообщества...",
                paragraph_2="Второй сегмент текста о подходе к работе...",
                button_text="Перейти к проектам",
                button_link="/projects"
            )
        about_data = AboutPageSerializer(about).data

        values = ValueSerializer(Value.objects.all(), many=True).data
        team = TeamMemberSerializer(TeamMember.objects.all(), many=True).data
        images = GalleryImageSerializer(GalleryImage.objects.all(), many=True).data
        response = {
            "hero": {
                "title": about_data.get("hero_title", ""),
                "description": about_data.get("hero_description", "")
            },
            "about_section": {
                "title": about_data.get("about_title", ""),
                "paragraphs": [
                    about_data.get("paragraph_1", ""),
                    about_data.get("paragraph_2", "")
                ],
                "action_button": {
                    "text": about_data.get("button_text", ""),
                    "link": about_data.get("button_link", "")
                }
            },
            "values": {
                "title": "Наши ценности",
                "items": values
            },
            "team": {
                "title": "Наша команда",
                "members": team,
                "action_button": {
                    "label": "Присоединиться",
                    "link": "/contacts"
                }
            },
            "gallery_carousel": {
                "title": "Галерея",
                "images": [{"id": f"img_{img['id']}", **img} for img in images]
            }
        }

        return Response(response)
