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
DJANGO_ARTICLE = f"{DJANGO_URL.rstrip('/')}/articles/"

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
    confirming_uid: int = 0

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

    def delete_user(self, uid: int):
        self._do_action(uid, "delete_user")
        yield
        yield ManageUsersState.load_users

    def ask_delete_user(self, uid: int):
        self.confirming_uid = uid

    def cancel_delete_user(self):
        self.confirming_uid = 0

    def confirm_delete_user(self, uid: int):
        self._do_action(uid, "delete_user")
        self.confirming_uid = 0
        yield
        yield ManageUsersState.load_users

    def toggle_download(self, uid: int):
        self._do_action(uid, "toggle_download")
        yield
        yield ManageUsersState.load_users


# ── State: Upload Article ────────────────────────────────────────────────────

import re

_DRIVE_ID_PATTERNS = [
    r"/file/d/([a-zA-Z0-9_-]{10,})",   # .../file/d/<ID>/view
    r"[?&]id=([a-zA-Z0-9_-]{10,})",    # .../uc?id=<ID> or open?id=<ID>
]


def extract_drive_file_id(raw: str) -> str:
    """Accepts a full Google Drive share link or a bare file id and
    returns just the file id. Returns '' if nothing could be parsed."""
    raw = raw.strip()
    if not raw:
        return ""
    for pattern in _DRIVE_ID_PATTERNS:
        m = re.search(pattern, raw)
        if m:
            return m.group(1)
    # No URL pattern matched — assume they pasted the bare ID already.
    if re.fullmatch(r"[a-zA-Z0-9_-]{10,}", raw):
        return raw
    return ""


class UploadState(rx.State):
    date: str = ""
    file_type: str = "PDF"
    title: str = ""
    category: str = "whitepaper"
    creator_name: str = ""
    drive_link: str = ""
    status: str = ""
    status_color: str = "white"
    parsed_drive_id: str = ""

    def update_title(self, value: str):
        self.title = value

    def update_date(self, value: str):
        self.date = value

    def update_category(self, label: str):
        # rx.select surfaces the human label; store the underlying value key.
        self.category = _CATEGORY_LABEL_TO_VALUE.get(label, self.category)


    def update_creator_name(self, value: str):
        self.creator_name = value

    def update_drive_link(self, value: str):
        self.drive_link = value
        self.parsed_drive_id = extract_drive_file_id(value)

    def handle_submit(self):
        if not self.title or not self.date:
            self.status = "Title and date are required."
            self.status_color = STOP
            return
        drive_id = extract_drive_file_id(self.drive_link)
        if not drive_id:
            self.status = "Couldn't parse a Google Drive file ID from that link."
            self.status_color = STOP
            return

        try:
            resp = requests.post(
                f"{API_BASE}/upload-article/",
                data={
                    "date": self.date,
                    "title": self.title,
                    "category": self.category,
                    "file_type": self.file_type,
                    "creator_name": self.creator_name,
                    "drive_file_id": drive_id,
                },
                headers=AUTH_HEADERS,
                timeout=30,
            )
            if resp.status_code in (200, 201):
                self.status = "✓ Article linked successfully."
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
    date: str
    file_type: str
    title: str
    category: str
    category_display: str
    creator_name: str

CATEGORY_OPTIONS = [
    ("financial_analytic", "Financial Analytic"),
    ("project_management", "Project Management"),
    ("business_development", "Business Development"),
    ("market_analysis", "Market Analysis"),
    ("intelligence", "Business Analyst & Intelligence"),
    ("industry_report", "Industry Report"),
    ("science", "Data Science"),
    ("statistic", "Statistic"),
    ("script", "Code Script"),
    ("whitepaper", "Whitepaper")
]
_CATEGORY_LABEL_TO_VALUE = {label: value for value, label in CATEGORY_OPTIONS}

class ArticlesState(rx.State):
    articles: list[ArticleRow] = []
    status: str = ""
    status_color: str = "white"
    loading: bool = False
    confirming_id: int = 0

    # Edit form state
    editing_id: int = 0
    edit_date: str = ""
    edit_title: str = ""
    edit_category: str = "whitepaper"
    edit_creator_name: str = ""
    edit_status: str = ""
    edit_status_color: str = "white"

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
                    id=a.get("id"), # type: ignore
                    date=a.get("date", "-"),
                    title=a.get("title", "-"),
                    file_type=a.get("file_type", "-"),
                    category=a.get("category", "whitepaper"),
                    category_display=a.get("category_display", "-"),
                    creator_name=a.get("creator_name", ""),                )
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


    # ── Edit ──────────────────────────────────────────────────────────────
 
    def start_edit(self, a: ArticleRow):
        self.editing_id = a.id
        self.edit_date = a.date
        self.edit_title = a.title
        self.edit_category = a.category
        self.edit_creator_name = a.creator_name
        self.edit_status = ""
 
    def cancel_edit(self):
        self.editing_id = 0
        self.edit_status = ""
 
    def update_edit_title(self, value: str):
        self.edit_title = value
 
    def update_edit_date(self, value: str):
        self.edit_date = value
 
    def update_edit_category(self, label: str):
        self.edit_category = _CATEGORY_LABEL_TO_VALUE.get(label, self.edit_category)
 
    def update_edit_creator_name(self, value: str):
        self.edit_creator_name = value
 
    def submit_edit(self):
        if not self.edit_title or not self.edit_date:
            self.edit_status = "Title and date are required."
            self.edit_status_color = STOP
            return
        try:
            r = requests.post(
                f"{API_BASE}/edit-article/",
                json={
                    "article_id": self.editing_id,
                    "date": self.edit_date,
                    "title": self.edit_title,
                    "creator_name": self.edit_creator_name,
                    "category": self.edit_category,
                },
                headers=AUTH_HEADERS,
                timeout=30,
            )
            if r.status_code == 200:
                self.editing_id = 0
                self.status = "Article updated."
                self.status_color = GO
            else:
                self.edit_status = f"Failed: {r.status_code} {r.text}"
                self.edit_status_color = STOP
                return
        except Exception as ex:
            self.edit_status = f"Error: {ex}"
            self.edit_status_color = STOP
            return
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
        rx.link(
            rx.text("← Back to Article", color=MUTED, size="2"),
            href=DJANGO_ARTICLE,
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
    is_confirming = ManageUsersState.confirming_uid == u.id
    return rx.hstack(
        rx.text(u.username, width="200px", color=PAPER, weight="medium"),
        rx.text(u.email, width="240px", color=MUTED, class_name="data-mono", size="2"),
        rx.box(
            _status_pill(rx.cond(u.is_approved, "Approved", "Pending"), u.is_approved),
            width="130px",
        ),
        rx.box(
            _status_pill(rx.cond(u.can_download_all, "Can Download", "No Download"), u.can_download_all),
            width="150px",
        ),
        rx.button(
            "Can Download",
            on_click=lambda: ManageUsersState.toggle_download(u.id), # type: ignore
            variant="outline",
            color_scheme="gray",
            size="2",
        ),
        rx.cond(
            is_confirming,
            rx.hstack(
                rx.text("Delete?", size="2", color=STOP),
                rx.button(
                    "Confirm",
                    on_click=lambda: ManageUsersState.confirm_delete_user(u.id), # type: ignore
                    style={"background": STOP, "color": PAPER},
                    size="2",
                ),
                rx.button(
                    "Cancel",
                    on_click=ManageUsersState.cancel_delete_user, # type: ignore
                    variant="outline",
                    color_scheme="gray",
                    size="2",
                ),
                spacing="2",
            ),
            rx.button(
                "Delete User",
                on_click=lambda: ManageUsersState.ask_delete_user(u.id), # type: ignore
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
    is_editing = ArticlesState.editing_id == a.id

    display_row = rx.hstack(
        rx.vstack(
            rx.text(a.title, color=PAPER, weight="medium"),
            rx.hstack(
                rx.text(a.category_display, size="1", class_name="eyebrow", color=BRASS),
                rx.cond(
                    a.creator_name != "",
                    rx.text(f"By {a.creator_name}", size="1", color=MUTED),
                ),
                spacing="3",
            ),
            spacing="1",
            align_items="start",
            width="260px",
        ),
        rx.text(a.date, width="110px", color=MUTED, class_name="data-mono", size="2"),
        rx.box(
            rx.text(a.file_type, size="1", class_name="eyebrow", color=BRASS),
            width="70px",
        ),
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
            rx.hstack(
                rx.button(
                    "Edit",
                    on_click=lambda: ArticlesState.start_edit(a), # type: ignore
                    variant="outline",
                    color_scheme="gray",
                    size="2",
                ),
                rx.button(
                    "Delete",
                    on_click=lambda: ArticlesState.ask_delete(a.id), # type: ignore
                    variant="outline",
                    color_scheme="red",
                    size="2",
                ),
                spacing="2",
            ),
        ),
        padding="14px",
        border=f"1px solid {LINE}",
        background=PANEL,
        width="100%",
        align_items="center",
    )
 
    edit_form = rx.vstack(
        rx.hstack(
            rx.input(
                value=ArticlesState.edit_title,
                placeholder="Title",
                on_change=ArticlesState.update_edit_title, # type: ignore
                width="260px",
                style={"borderColor": LINE, "color": PAPER, "background": INK},
            ),
            rx.input(
                value=ArticlesState.edit_date,
                type="date",
                on_change=ArticlesState.update_edit_date, # type: ignore
                width="160px",
                style={"borderColor": LINE, "color": PAPER, "background": INK},
            ),
            rx.select(
                [label for _, label in CATEGORY_OPTIONS],
                placeholder=a.category_display,
                on_change=ArticlesState.update_edit_category, # type: ignore
                width="200px",
            ),
            spacing="3",
        ),
        rx.hstack(
            rx.input(
                value=ArticlesState.edit_creator_name,
                placeholder="Creator / Author",
                on_change=ArticlesState.update_edit_creator_name, # type: ignore
                width="260px",
                style={"borderColor": LINE, "color": PAPER, "background": INK},
            ),
            spacing="4",
            align_items="center",
        ),
        rx.hstack(
            rx.button(
                "Save",
                on_click=ArticlesState.submit_edit, # type: ignore
                style={"background": BRASS, "color": INK},
                size="2",
            ),
            rx.button(
                "Cancel",
                on_click=ArticlesState.cancel_edit, # type: ignore
                variant="outline",
                color_scheme="gray",
                size="2",
            ),
            rx.text(ArticlesState.edit_status, color=ArticlesState.edit_status_color, size="2", class_name="data-mono"),
            spacing="3",
            align_items="center",
        ),
        padding="14px",
        border=f"1px solid {BRASS}",
        background=PANEL,
        width="100%",
        spacing="3",
    )
 
    return rx.cond(is_editing, edit_form, display_row)


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
        rx.hstack(
            rx.vstack(
                rx.text("Category", size="1", color=MUTED, class_name="eyebrow"),
                rx.select(
                    [label for _, label in CATEGORY_OPTIONS],
                    placeholder="Whitepaper",
                    on_change=UploadState.update_category, # type: ignore
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            rx.vstack(
                rx.text("Creator / Author", size="1", color=MUTED, class_name="eyebrow"),
                rx.input(
                    placeholder="e.g. Irsyad Damlis",
                    on_change=UploadState.update_creator_name, # type: ignore
                    width="100%",
                    style=input_style,
                ),
                spacing="1",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.input(
                    placeholder="Paste Google Drive share link (or file ID)",
                    on_change=UploadState.update_drive_link, # type: ignore
                    width="100%",
                    style=input_style,
                ),
                rx.text(
                    rx.cond(
                        UploadState.parsed_drive_id != "",
                        f"Parsed file ID: {UploadState.parsed_drive_id}",
                        "Paste a Drive share link — the file must be viewable by your service account.",
                    ),
                    size="1",
                    color=rx.cond(UploadState.parsed_drive_id != "", GO, MUTED),
                    class_name="data-mono",
                ),
                spacing="2",
                width="100%",
            ),
            class_name="blueprint-frame",
            padding="16px",
            width="100%",
        ),
        rx.hstack(
            rx.button(
                "Link Article",
                on_click=UploadState.handle_submit, # type: ignore
                style={"background": BRASS, "color": INK},
            ),
        ),
        rx.text(UploadState.status, color=UploadState.status_color, class_name="data-mono", size="2"),
        width="600px",
        spacing="3",
    )
    return page_shell("Upload Article", content, "/upload-article")


@rx.page(route="/")
def index() -> rx.Component:
    return manage_users_page()


app = rx.App(stylesheets=["theme.css"])