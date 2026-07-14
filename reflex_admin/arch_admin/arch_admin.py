"""Reflex admin app for Arch-notions. Ports admin.py (Flet) 1:1."""

import os
from dataclasses import dataclass

import reflex as rx
import requests

API_BASE = "http://127.0.0.1:8000/api"
# Prefer an env var over hardcoding the token in source.
ADMIN_TOKEN = os.environ.get("ARCH_ADMIN_TOKEN", "684bc833a6abe07e59da2b04f5c829b026e595cb")
AUTH_HEADERS = {"Authorization": f"Token {ADMIN_TOKEN}"}
DJANGO_URL = os.environ.get("DJANGO_URL", "http://localhost:8000")

NAV_ITEMS = [
    ("Manage Users", "/manage-users"),
    ("Upload Article", "/upload-article"),
    ("Manage Articles", "/manage-articles"),
]

# ── Theme tokens ──────────────────────────────────────────────────────────────
INK = "#0B1220"
PANEL = "#121B2B"
LINE = "#2C4257"
BRASS = "#C9A227"
PAPER = "#ECE8DD"
MUTED = "#7E8FA3"
GO = "#4F9D77"
STOP = "#C1666B"
FONT_DISPLAY = "'Space Grotesk', sans-serif"
FONT_MONO = "'IBM Plex Mono', monospace"


# ── State: Manage Users ──────────────────────────────────────────────────────

@dataclass
class UserRow:
    id: int
    username: str
    email: str
    is_approved: bool
    can_download_all: bool


class ManageUsersState(rx.State):
    users: list[UserRow] = []
    status: str = ""
    status_color: str = "white"
    loading: bool = False

    def load_users(self):
        self.loading = True
        self.status = "Refreshing..."
        self.status_color = MUTED
        yield
        try:
            r = requests.get(f"{API_BASE}/manage-users/", headers=AUTH_HEADERS, timeout=30)
            if r.status_code != 200:
                self.status = f"Failed: {r.status_code} {r.text}"
                self.status_color = STOP
                return
            data = r.json().get("results", [])
            self.users = [
                UserRow(
                    id=u.get("id"),
                    username=u.get("username", "-"),
                    email=u.get("email", "-"),
                    is_approved=bool(u.get("is_approved")),
                    can_download_all=bool(u.get("can_download_all")),
                )
                for u in data
            ]
            self.status = f"Loaded {len(self.users)} user(s)."
            self.status_color = GO
        except Exception as ex:
            self.status = f"Error: {ex}"
            self.status_color = STOP
        finally:
            self.loading = False

    def _do_action(self, uid: int, action_type: str):
        try:
            r = requests.post(
                f"{API_BASE}/manage-users/action/",
                json={"user_id": uid, "action": action_type},
                headers=AUTH_HEADERS,
                timeout=30,
            )
            self.status = "Action successful." if r.status_code == 200 else f"Failed: {r.status_code} {r.text}"
            self.status_color = GO if r.status_code == 200 else STOP
        except Exception as ex:
            self.status = f"Error: {ex}"
            self.status_color = STOP

    def toggle_approval(self, uid: int):
        self._do_action(uid, "toggle_approval")
        yield
        yield ManageUsersState.load_users

    def toggle_download(self, uid: int):
        self._do_action(uid, "toggle_download")
        yield
        yield ManageUsersState.load_users


# ── State: Upload Article ────────────────────────────────────────────────────

class UploadState(rx.State):
    title: str = ""
    date: str = ""
    file_type: str = "PDF"
    status: str = ""
    status_color: str = "white"
    uploaded_filename: str = ""

    def update_title(self, value: str):
        self.title = value

    def update_date(self, value: str):
        self.date = value

    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            self.status = "Please choose a file first."
            self.status_color = STOP
            return
        if not self.title or not self.date:
            self.status = "Title and date are required."
            self.status_color = STOP
            return

        file = files[0]
        data = await file.read()
        self.uploaded_filename = file.filename # type: ignore

        try:
            resp = requests.post(
                f"{API_BASE}/upload-article/",
                data={
                    "title": self.title,
                    "date": self.date,
                    "file_type": self.file_type,
                },
                files={"file": (file.filename, data)},
                headers=AUTH_HEADERS,
                timeout=60,
            )
            if resp.status_code in (200, 201):
                self.status = "✓ Upload successful."
                self.status_color = GO
            else:
                self.status = f"✗ Failed: {resp.status_code} {resp.text}"
                self.status_color = STOP
        except Exception as ex:
            self.status = f"✗ Error: {ex}"
            self.status_color = STOP


# ── State: Manage Articles ───────────────────────────────────────────────────

@dataclass
class ArticleRow:
    id: int
    title: str
    date: str
    file_type: str
    file_url: str


class ArticlesState(rx.State):
    articles: list[ArticleRow] = []
    status: str = ""
    status_color: str = "white"
    loading: bool = False
    confirming_id: int = 0

    def load_articles(self):
        self.loading = True
        self.status = "Refreshing..."
        self.status_color = MUTED
        yield
        try:
            r = requests.get(f"{API_BASE}/articles/", headers=AUTH_HEADERS, timeout=30)
            if r.status_code != 200:
                self.status = f"Failed: {r.status_code} {r.text}"
                self.status_color = STOP
                return
            data = r.json().get("results", [])
            self.articles = [
                ArticleRow(
                    id=a.get("id"),
                    title=a.get("title", "-"),
                    date=a.get("date", "-"),
                    file_type=a.get("file_type", "-"),
                    file_url=a.get("file_url", ""),
                )
                for a in data
            ]
            self.status = f"Loaded {len(self.articles)} article(s)."
            self.status_color = GO
        except Exception as ex:
            self.status = f"Error: {ex}"
            self.status_color = STOP
        finally:
            self.loading = False

    def ask_delete(self, aid: int):
        self.confirming_id = aid

    def cancel_delete(self):
        self.confirming_id = 0

    def confirm_delete(self, aid: int):
        try:
            r = requests.post(
                f"{API_BASE}/delete-article/",
                json={"article_id": aid},
                headers=AUTH_HEADERS,
                timeout=30,
            )
            self.status = "Deleted." if r.status_code == 200 else f"Failed: {r.status_code} {r.text}"
            self.status_color = GO if r.status_code == 200 else STOP
        except Exception as ex:
            self.status = f"Error: {ex}"
            self.status_color = STOP
        self.confirming_id = 0
        yield
        yield ArticlesState.load_articles




def _nav_link(label: str, route: str, current: str) -> rx.Component:
    active = route == current
    return rx.link(
        rx.hstack(
            rx.box(
                width="2px",
                height="16px",
                background=rx.cond(active, BRASS, "transparent"),
            ),
            rx.text(
                label,
                weight=rx.cond(active, "medium", "regular"),
                color=rx.cond(active, PAPER, MUTED),
                size="2",
                font_family=FONT_DISPLAY,
            ),
            spacing="3",
            align_items="center",
        ),
        href=route,
        padding="8px 4px",
        width="100%",
        _hover={"color": PAPER},
    )


def sidebar(current: str) -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text("ARCH-NOTIONS", size="4", weight="bold", color=PAPER, font_family=FONT_DISPLAY, letter_spacing="0.02em"),
            rx.text("Admin Console", size="1", color=MUTED, class_name="eyebrow"),
            spacing="1",
            align_items="start",
        ),
        rx.divider(border_color=LINE, margin_y="16px"),
        *[_nav_link(label, route, current) for label, route in NAV_ITEMS],
        rx.spacer(),
        rx.divider(border_color=LINE, margin_y="16px"),
        rx.link(
            rx.text("← Back to Home", color=MUTED, size="2"),
            href=DJANGO_URL,
            padding="8px 4px",
            _hover={"color": PAPER},
        ),
        width="220px",
        min_width="220px",
        max_width="220px",
        flex_shrink="0",
        flex_grow="0",
        min_height="100vh",
        height="100%",
        padding="24px 20px",
        background=PANEL,
        border_right=f"1px solid {LINE}",
        align_items="stretch",
        spacing="1",
    )


def page_shell(title: str, content: rx.Component, route: str) -> rx.Component:
    section = route.strip("/").replace("-", " ").upper() or "HOME"
    return rx.hstack(
        sidebar(route),
        rx.box(
            rx.vstack(
                rx.text(f"ADMIN / {section}", class_name="eyebrow", size="1", color=BRASS),
                rx.heading(title, color=PAPER, size="6", font_family=FONT_DISPLAY, weight="medium"),
                rx.divider(border_color=LINE, style={"borderStyle": "dashed"}),
                content,
                align_items="start",
                spacing="4",
                height="100%",
                width="100%",
            ),
            padding="32px 40px",
            width="100%",
            height="100%",
            overflow="hidden",
        ),
        spacing="0",
        background=INK,
        height="100vh",
        width="100%",
        align_items="start",
        overflow="hidden",
    )


# ── Pages ──────────────────────────────────────────────────────────────────

def _status_pill(text_content, is_positive) -> rx.Component:
    return rx.box(
        rx.text(text_content, size="1", class_name="eyebrow", color=rx.cond(is_positive, GO, STOP)),
        padding="4px 10px",
        border_radius="3px",
        border=rx.cond(is_positive, f"1px solid {GO}", f"1px solid {STOP}"),
        background=rx.cond(is_positive, "rgba(79,157,119,0.08)", "rgba(193,102,107,0.08)"),
        width="fit-content",
    )


def _user_row(u: UserRow) -> rx.Component:
    return rx.hstack(
        rx.text(u.username, width="200px", color=PAPER, weight="medium"),
        rx.text(u.email, width="240px", color=MUTED, class_name="data-mono", size="2"),
        rx.box(
            _status_pill(rx.cond(u.is_approved, "Approved", "Pending"), u.is_approved),
            width="130px",
        ),
        rx.button(
            "Toggle Approval",
            on_click=lambda: ManageUsersState.toggle_approval(u.id), # type: ignore
            variant="outline",
            color_scheme="gray",
            size="2",
        ),
        rx.box(
            _status_pill(rx.cond(u.can_download_all, "Can Download", "No Download"), u.can_download_all),
            width="150px",
        ),
        rx.button(
            "Toggle Download",
            on_click=lambda: ManageUsersState.toggle_download(u.id), # type: ignore
            variant="outline",
            color_scheme="gray",
            size="2",
        ),
        padding="14px",
        border=f"1px solid {LINE}",
        background=PANEL,
        width="100%",
        align_items="center",
    )


@rx.page(route="/manage-users", on_load=ManageUsersState.load_users) # type: ignore
def manage_users_page() -> rx.Component:
    content = rx.vstack(
        rx.button(
            "Refresh",
            on_click=ManageUsersState.load_users, # type: ignore
            loading=ManageUsersState.loading,
            style={"background": BRASS, "color": INK},
        ),
        rx.text(ManageUsersState.status, color=ManageUsersState.status_color, class_name="data-mono", size="2"),
        rx.box(
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(ManageUsersState.users, _user_row),
                    spacing="2",
                    width="100%",
                    min_width="900px",
                ),
                type="auto",
                scrollbars="both",
                style={"flex": "1", "minHeight": "0"},
                width="100%",
            ),
            class_name="blueprint-frame",
            padding="12px",
            width="100%",
            height="100%",
            flex="1",
            min_height="0",
        ),
        width="100%",
        max_width="900px",
        spacing="3",
        height="100%",
        flex="1",
        min_height="0",
    )
    return page_shell("Manage Users", content, "/manage-users")


def _article_row(a: ArticleRow) -> rx.Component:
    is_confirming = ArticlesState.confirming_id == a.id
    return rx.hstack(
        rx.text(a.title, width="260px", color=PAPER, weight="medium"),
        rx.text(a.date, width="120px", color=MUTED, class_name="data-mono", size="2"),
        rx.box(
            rx.text(a.file_type, size="1", class_name="eyebrow", color=BRASS),
            width="90px",
        ),
        rx.link(rx.text("View", size="2", color=BRASS), href=a.file_url, is_external=True, width="70px"),
        rx.spacer(),
        rx.cond(
            is_confirming,
            rx.hstack(
                rx.text("Delete permanently?", size="2", color=STOP),
                rx.button(
                    "Confirm",
                    on_click=lambda: ArticlesState.confirm_delete(a.id), # type: ignore
                    style={"background": STOP, "color": PAPER},
                    size="2",
                ),
                rx.button(
                    "Cancel",
                    on_click=ArticlesState.cancel_delete, # type: ignore
                    variant="outline",
                    color_scheme="gray",
                    size="2",
                ),
                spacing="2",
            ),
            rx.button(
                "Delete",
                on_click=lambda: ArticlesState.ask_delete(a.id), # type: ignore
                variant="outline",
                color_scheme="red",
                size="2",
            ),
        ),
        padding="14px",
        border=f"1px solid {LINE}",
        background=PANEL,
        width="100%",
        align_items="center",
    )


@rx.page(route="/manage-articles", on_load=ArticlesState.load_articles) # type: ignore
def manage_articles_page() -> rx.Component:
    content = rx.vstack(
        rx.button(
            "Refresh",
            on_click=ArticlesState.load_articles, # type: ignore
            loading=ArticlesState.loading,
            style={"background": BRASS, "color": INK},
        ),
        rx.text(ArticlesState.status, color=ArticlesState.status_color, class_name="data-mono", size="2"),
        rx.box(
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(ArticlesState.articles, _article_row),
                    spacing="2",
                    width="100%",
                    min_width="900px",
                ),
                type="auto",
                scrollbars="both",
                style={"flex": "1", "minHeight": "0"},
                width="100%",
            ),
            class_name="blueprint-frame",
            padding="12px",
            width="100%",
            height="100%",
            flex="1",
            min_height="0",
        ),
        width="100%",
        max_width="900px",
        spacing="3",
        height="100%",
        flex="1",
        min_height="0",
    )
    return page_shell("Manage Articles", content, "/manage-articles")



@rx.page(route="/upload-article")
def upload_article_page() -> rx.Component:
    input_style = {
        "background": PANEL,
        "borderColor": LINE,
        "color": PAPER,
    }
    content = rx.vstack(
        rx.input(placeholder="Title", on_change=UploadState.update_title, width="420px", style=input_style), # type: ignore
        rx.input(placeholder="Date", type="date", on_change=UploadState.update_date, width="420px", style=input_style), # type: ignore
        rx.hstack(
            rx.text("File type:", color=MUTED, size="2"),
            rx.text("PDF", color=BRASS, size="2", weight="medium", class_name="data-mono"),
            spacing="2",
            align_items="center",
        ),
        rx.box(
            rx.upload(
                rx.vstack(
                    rx.button(
                        "Choose File",
                        type="button",
                        style={"background": BRASS, "color": INK},
                    ),
                    rx.text("Drag/drop or click", size="1", color=MUTED, class_name="eyebrow"),
                ),
                id="article_upload",
                accept={
                    "application/pdf": [".pdf"],
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
                },
                max_files=1,
                border=f"1px dashed {LINE}",
                padding="24px",
                background=PANEL,
            ),
            class_name="blueprint-frame",
            padding="8px",
        ),
        rx.hstack(
            rx.foreach(rx.selected_files("article_upload"), lambda f: rx.text(f, color=PAPER, class_name="data-mono", size="2")),
        ),
        rx.hstack(
            rx.button(
                "Upload",
                on_click=UploadState.handle_upload(rx.upload_files(upload_id="article_upload")), # type: ignore
                style={"background": BRASS, "color": INK},
            ),
            rx.button(
                "Clear",
                on_click=rx.clear_selected_files("article_upload"),
                variant="outline",
                color_scheme="gray",
            ),
        ),
        rx.text(UploadState.uploaded_filename, color=MUTED, size="1", class_name="data-mono"),
        rx.text(UploadState.status, color=UploadState.status_color, class_name="data-mono", size="2"),
        width="600px",
        spacing="3",
    )
    return page_shell("Upload Article", content, "/upload-article")


@rx.page(route="/")
def index() -> rx.Component:
    return manage_users_page()


app = rx.App(stylesheets=["theme.css"])