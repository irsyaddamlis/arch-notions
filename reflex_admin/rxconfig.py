import reflex as rx

# Mirrors your old Flet setup (8550/8551) but for Reflex, which needs two
# processes: a backend (state/websocket, like Flet's app process) and a
# frontend (compiled Next.js static build served in dev by a Node server).
#
# In production these get reverse-proxied under Django's public port so the
# end user only ever sees ONE url/port — same pattern as your Flet setup.

config = rx.Config(
    app_name="arch_admin",
    backend_port=8560,
    frontend_port=3550,
    plugins=[rx.plugins.RadixThemesPlugin()],
    # api_url is what the compiled frontend JS uses to reach the backend
    # websocket. In dev this is the raw backend port. In production, point
    # this at the public path Nginx proxies to the backend (see nginx.conf.example).
    api_url="http://localhost:8560",
    cors_allowed_origins=[
        "http://localhost:8000",   # Django
        "http://localhost:3550",   # Reflex frontend dev server
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3550",
    ],
)