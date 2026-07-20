from django.core.management.base import BaseCommand

from main_site.dashboard_model import bi_rate
from main_site.refresh_utils import run_indicator_group


class Command(BaseCommand):
    help = "Refreshes the BI Rate. Run weekly, Monday 9am WIB."

    def handle(self, *args, **options):
        run_indicator_group(self.stdout, {
            "bi_rate": bi_rate,
        })
