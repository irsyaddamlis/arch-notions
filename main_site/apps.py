import os
import subprocess
import sys

from django.apps import AppConfig


class MainSiteConfig(AppConfig):
    name = 'main_site'

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Reflex admin panel (replaces flet_app/admin.py).
        # Dev mode: frontend (3550) and backend (8560) run as separate
        # processes. When you deploy, switch to `--env prod` with only
        # --backend-port set (prod serves both from one port in Reflex 0.9+).
        env = os.environ.copy()
        env["ARCH_ADMIN_TOKEN"] = env.get("ARCH_ADMIN_TOKEN", "684bc833a6abe07e59da2b04f5c829b026e595cb")
        env["DJANGO_URL"] = env.get("DJANGO_URL", "http://localhost:8000")

        subprocess.Popen(
            [sys.executable, "-m", "reflex", "run",
             "--backend-port", "8560", "--frontend-port", "3550"],
            cwd=os.path.join(base_dir, "reflex_admin"),
            env=env,
        )

        # Unchanged — still Flet, still port 8551.
        subprocess.Popen(
            [sys.executable, "flet_app/passreset.py"],
            cwd=base_dir,
        )