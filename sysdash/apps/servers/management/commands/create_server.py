from django.core.management.base import BaseCommand
from apps.servers.models import Server


class Command(BaseCommand):
    help = "Create a server entry and print its API key"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Name for the server (e.g. linux-server-01)")
        parser.add_argument("--description", type=str, default="", help="Optional description")

    def handle(self, *args, **options):
        server, created = Server.objects.get_or_create(
            name=options["name"],
            defaults={"description": options["description"]},
        )
        action = "Created" if created else "Already exists"
        self.stdout.write(self.style.SUCCESS(f"{action}: {server.name}"))
        self.stdout.write(f"API Key: {server.api_key}")
        self.stdout.write(
            self.style.WARNING(
                "\nCopy the API key above into your .env file as SERVER_API_KEY="
            )
        )
