# from rest_framework import serializers


"""
...

Anti-spam techniques (for public forms):

    Honeypot field — hidden via CSS (display: none), NOT type="hidden".
    Bots fill all visible fields automatically; humans never touch it.
    If the field arrives non-empty — silently reject the submission.

    class ContactSerializer(serializers.Serializer):
        # Regular fields...

        website = serializers.CharField(
            required=False,
            allow_blank=True,
            write_only=True,  # never returned in response
        )

        def validate_website(self, value):
            if value and value.strip():
                raise serializers.ValidationError('Invalid submission.')
            return value

    Frontend (React/Vue/vanilla):
        <input name="website" style="display:none" tabindex="-1" autocomplete="off" />
        # Never fill it programmatically — must stay empty on submit.

...
"""


