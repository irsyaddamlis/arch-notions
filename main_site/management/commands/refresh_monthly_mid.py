from django.core.management.base import BaseCommand

from main_site.dashboard_model import (broad_money, cpi, deposit_rate,
                                       lending_rate, loan_rate, oil_prc)
from main_site.refresh_utils import run_indicator_group


class Command(BaseCommand):
    help = (
        "Refreshes the mid-month indicators: oil price, lending/loan/deposit "
        "rates, broad money (M2), and CPI. Run on the 15th of each month."
    )

    def handle(self, *args, **options):
        run_indicator_group(self.stdout, {
            "oil_price": oil_prc,
            "lending_rate": lending_rate,
            "loan_rate": loan_rate,
            "deposit_rate": deposit_rate,
            "broad_money": broad_money,
            "cpi": cpi,
        })
