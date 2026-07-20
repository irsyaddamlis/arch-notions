from django.core.management.base import BaseCommand

from main_site.dashboard_model import id_debt
from main_site.refresh_utils import run_indicator_group


class Command(BaseCommand):
    help = (
        "Refreshes Indonesian external debt (SULNI). Run quarterly, mid-month. "
        "Double-check with BI's actual SULNI release calendar which months "
        "count as 'quarterly' for this report before finalizing the cron months."
    )

    def handle(self, *args, **options):
        run_indicator_group(self.stdout, {
            "id_debt": id_debt,
        })
