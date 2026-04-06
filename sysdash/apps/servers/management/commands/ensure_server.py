import os
import uuid

from django.core.management.base import BaseCommand

from apps.servers.models import Server


class Command(BaseCommand):
    help = "Ensure a server record exists matching SERVER_API_KEY in the environment"

    def handle(self, *args, **options):
        raw_key = os.environ.get("SERVER_API_KEY", "")
        if not raw_key:
            self.stdout.write(self.style.WARNING("SERVER_API_KEY not set — skipping server registration."))
            return

        try:
            api_key = uuid.UUID(raw_key)
        except ValueError:
            self.stdout.write(self.style.ERROR(f"SERVER_API_KEY '{raw_key}' is not a valid UUID — skipping."))
            return

        server, created = Server.objects.get_or_create(
            api_key=api_key,
            defaults={"name": "linux-server-01"},
        )
        action = "Created" if created else "Already exists"
        self.stdout.write(self.style.SUCCESS(f"{action}: {server.name} (api_key={server.api_key})"))
