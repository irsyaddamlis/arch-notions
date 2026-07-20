from django.core.management.base import BaseCommand

from main_site.dashboard_model import gdp
from main_site.models import IndicatorSnapshot


class Command(BaseCommand):
    help = (
        "Refreshes GDP growth. Run in April, May, and June, since the "
        "government's release can slip between those months. Unlike the "
        "other commands, this skips saving when the fetch comes back N/A, "
        "so a delayed release doesn't overwrite last quarter's real value."
    )

    def handle(self, *args, **options):
        value = gdp()
        if value == "N/A":
            self.stdout.write("[gdp] no new data yet - keeping last stored value")
            return

        IndicatorSnapshot.objects.update_or_create(
            key="gdp", defaults={"value": value}
        )
        self.stdout.write(f"[gdp] -> {value}")
