import csv
import re
from datetime import datetime

from django.core.management.base import BaseCommand

from main_site.models import Article, Category


def extract_drive_file_id(value: str) -> str:
    """
    Accepts either:
      - Google Drive URL
      - Raw Drive File ID

    Returns only the file ID.
    """

    value = value.strip()

    if not value:
        return ""

    # Already looks like a Drive file ID
    if re.fullmatch(r"[A-Za-z0-9_-]{20,}", value):
        return value

    # https://drive.google.com/file/d/FILE_ID/view
    m = re.search(r"/d/([A-Za-z0-9_-]+)", value)
    if m:
        return m.group(1)

    # https://drive.google.com/open?id=FILE_ID
    m = re.search(r"[?&]id=([A-Za-z0-9_-]+)", value)
    if m:
        return m.group(1)

    return value


class Command(BaseCommand):
    help = "Import Articles from CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="CSV file path",
        )

    def handle(self, *args, **options):

        csv_file = options["csv_file"]

        created = 0
        updated = 0
        skipped = 0

        # Change to "latin-1" if your CSV requires it.
        with open(csv_file, "r", encoding="latin-1", newline="") as f:

            reader = csv.DictReader(f)

            for line_no, row in enumerate(reader, start=2):

                try:

                    article_date = datetime.strptime(
                        row["date"].strip(),
                        "%m/%d/%y",
                    ).date()

                    category = None

                    if row.get("category_id", "").strip():
                        try:
                            category = Category.objects.get(
                                pk=int(row["category_id"])
                            )
                        except Category.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Line {line_no}: Category {row['category_id']} not found."
                                )
                            )

                    drive_id = extract_drive_file_id(
                        row["drive_file_id"]
                    )

                    article, created_flag = Article.objects.update_or_create(
                        drive_file_id=drive_id,
                        defaults={
                            "title": row["title"].strip(),
                            "date": article_date,
                            "file_type": row["file_type"].strip().lower(),
                            "creator_name": row["creator_name"].strip(),
                            "category": category,
                        },
                    )

                    if created_flag:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    skipped += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"Line {line_no}: {e}"
                        )
                    )

        self.stdout.write("")
        self.stdout.write("=" * 40)
        self.stdout.write(self.style.SUCCESS(f"Created : {created}"))
        self.stdout.write(self.style.SUCCESS(f"Updated : {updated}"))
        self.stdout.write(self.style.WARNING(f"Skipped : {skipped}"))
        self.stdout.write("=" * 40)