from .models import IndicatorSnapshot


def run_indicator_group(stdout, indicators):
    """
    indicators: dict of {key: callable}. Calls each function, stores the
    result via update_or_create, and reports success/failure per key so a
    single broken source doesn't stop the rest and doesn't fail silently.
    """
    for key, fn in indicators.items():
        try:
            value = fn()
        except Exception as exc:
            stdout.write(f"[{key}] FAILED: {exc}")
            continue

        IndicatorSnapshot.objects.update_or_create(
            key=key, defaults={"value": value}
        )
        stdout.write(f"[{key}] -> {value}")
