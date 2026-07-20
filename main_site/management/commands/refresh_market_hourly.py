from django.core.management.base import BaseCommand

from main_site.dashboard_model import (aud_exc, cny_exc, eur_exc, ihsg,
                                       jpy_exc, pond_exc, sgd_exc, trend,
                                       usd_exc)
from main_site.models import TrendSnapshot
from main_site.refresh_utils import run_indicator_group


class Command(BaseCommand):
    help = "Refreshes currency exchange rates, IHSG, and the trend chart. Run hourly, 9am-3pm WIB, weekdays."

    def handle(self, *args, **options):
        run_indicator_group(self.stdout, {
            "usd_idr": usd_exc,
            "gbp_idr": pond_exc,
            "eur_idr": eur_exc,
            "sgd_idr": sgd_exc,
            "cny_idr": cny_exc,
            "aud_idr": aud_exc,
            "jpy_idr": jpy_exc,
            "ihsg": ihsg,
        })

        try:
            trend_df = trend()
            # Rename to match what TrendChart.jsx expects: date/ihsg/exchange
            records = trend_df.rename(
                columns={"Date": "date", "IHSG": "ihsg", "$-Exchange": "exchange"}
            ).to_dict(orient="records")
        except Exception as exc:
            self.stdout.write(f"[trend] FAILED: {exc}")
            return

        snapshot, _ = TrendSnapshot.objects.get_or_create(pk=1)
        snapshot.data = records
        snapshot.save()
        self.stdout.write(f"[trend] -> {len(records)} points stored")