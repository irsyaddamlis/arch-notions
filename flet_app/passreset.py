"""Standalone Flet app for password reset requests."""

from __future__ import annotations

import os
import threading
import time

import flet as ft
import requests

API_BASE = "http://127.0.0.1:8000/api"
DJANGO_URL = "http://localhost:8000"


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#050510"
    page.title = "Arch-notions — Password Reset"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ── Logo with pulse animation ─────────────────────────────────────────────

    logo = ft.Image(
        src="Logo_Sticker.png",
        fit=ft.BoxFit.CONTAIN,
        width=240,
        height=120,
        opacity=0.0,
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
    )

    def pulse_animation():
        time.sleep(0.8)
        while True:
            try:
                logo.opacity = 1.0
                logo.update()
                time.sleep(1.5)
                logo.opacity = 0.35
                logo.update()
                time.sleep(1.5)
            except Exception:
                # Catch errors if the page closes while the thread runs
                break

    # ── Controls ──────────────────────────────────────────────────────────────

    email_input = ft.TextField(
        label="EMAIL ADDRESS",
        width=320,
        border_color="#00f2ff",
        focused_border_color="#ff00ff",
        keyboard_type=ft.KeyboardType.EMAIL,
        text_style=ft.TextStyle(color="#ffffff"),
        label_style=ft.TextStyle(color="#00f2ff", size=11),
    )

    status_text = ft.Text(
        value="",
        size=13,
        color="#00f2ff",
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
        width=320,
    )

    submit_btn = ft.FilledButton(
        content=ft.Text("SEND RESET LINK"),  # Wrap the string in ft.Text
        style=ft.ButtonStyle(
            bgcolor="#00f2ff",
            color="#000000",
            shape=ft.RoundedRectangleBorder(radius=6),
        ),
        width=320,
    )

    refresh_btn = ft.IconButton(
        icon=ft.Icons.REFRESH,
        icon_color="#00f2ff",
        tooltip="Clear",
    )

    # ── Handlers ──────────────────────────────────────────────────────────────

    def on_submit(e):
        email = email_input.value.strip()
        if not email:
            email_input.error_text = "EMAIL REQUIRED"
            status_text.value = ""
            status_text.color = "#ff4444"
            page.update()
            return

        email_input.error_text = None
        status_text.value = "Sending..."
        status_text.color = "#00f2ff"
        submit_btn.disabled = True
        page.update()

        try:
            r = requests.post(
                f"{API_BASE}/password-reset-request/",
                json={"email": email},
                timeout=15,
            )
            if r.status_code == 200:
                status_text.value = "✓  Reset link sent — check your inbox."
                status_text.color = "#00ff88"
            else:
                status_text.value = f"✗  Server error ({r.status_code}). Try again."
                status_text.color = "#ff4444"
        except requests.exceptions.ConnectionError:
            status_text.value = "✗  Cannot reach server. Is Django running?"
            status_text.color = "#ff4444"
        except Exception as ex:
            status_text.value = f"✗  {ex}"
            status_text.color = "#ff4444"

        submit_btn.disabled = False
        page.update()

    def on_refresh(e):
        email_input.value = ""
        email_input.error_text = None
        status_text.value = ""
        submit_btn.disabled = False
        page.update()

    submit_btn.on_click = on_submit
    refresh_btn.on_click = on_refresh

    # ── Layout ────────────────────────────────────────────────────────────────

    card = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Text(
                    "PASSWORD RESET",
                    size=22,
                    weight=ft.FontWeight.W_900,
                    color="#ffffff",
                    style=ft.TextStyle(letter_spacing=4),
                ),
                ft.Text(
                    "Enter your email to receive a reset link.",
                    size=11,
                    color="#888899",
                    style=ft.TextStyle(letter_spacing=1.5),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=16, color="#1a1a2e"),
                email_input,
                submit_btn,
                status_text,
                ft.Row([refresh_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=8, color="#1a1a2e"),
                ft.Markdown(
                    f"[← Back to site]({DJANGO_URL})",
                    auto_follow_links=True,
                    auto_follow_links_target=ft.UrlTarget.SELF,
                    md_style_sheet=ft.MarkdownStyleSheet(
                        a_text_style=ft.TextStyle(color="#888899", size=11),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            tight=True,
        ),
        padding=40,
        bgcolor="#0d1117",
        border_radius=16,
        border=ft.Border(
            top=ft.BorderSide(1, "#1e2a3a"),
            bottom=ft.BorderSide(1, "#1e2a3a"),
            left=ft.BorderSide(1, "#1e2a3a"),
            right=ft.BorderSide(1, "#1e2a3a"),
        ),
        shadow=ft.BoxShadow(blur_radius=32, color="#00f2ff22"),
        width=420,
    )

    page.add(ft.Row([card], alignment=ft.MainAxisAlignment.CENTER))
    threading.Thread(target=pulse_animation, daemon=True).start()


# ── Initialization (Moved outside main) ───────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("FLET_PORT", "8551"))
    os.environ["FLET_DISPLAY_URL_PREFIX"] = ""  # prevents auto-opening browser
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    # Note: Using modern `ft.app` instead of legacy `ft.run`
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)