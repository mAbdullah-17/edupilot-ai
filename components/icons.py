
"""
Shared professional UI icons for EduPilot AI.

This version intentionally does NOT use inline <svg> elements.
It returns clean HTML text symbols instead, preventing Streamlit
from exposing "svg" text/markup in the rendered page.

Existing code can continue using:
    from components.icons import svg as _icon

and:
    _icon("person", 20, "#1B2A4A")
"""

# Professional, monochrome Unicode symbols.
# These are intentionally kept simple so they render reliably
# without requiring an external icon library or SVG support.

_ICONS = {
    # Navigation / general
    "home": "⌂",
    "search": "⌕",
    "menu": "≡",
    "close": "×",
    "chevron_right": "›",
    "chevron_left": "‹",
    "arrow_right": "→",
    "arrow_left": "←",
    "add": "+",
    "remove": "−",
    "refresh": "↻",
    "edit": "✎",
    "delete": "⌫",

    # Profile / people
    "person": "●",
    "people": "●",
    "account_circle": "●",

    # Education
    "school": "▤",
    "book": "▤",
    "menu_book": "▤",
    "education": "▤",
    "assignment": "☷",
    "description": "▤",
    "library": "▥",

    # Contact
    "phone": "☎",
    "email": "✉",
    "mail": "✉",
    "location": "⌖",
    "place": "⌖",
    "link": "↗",
    "language": "◎",
    "globe": "◎",

    # Work / career
    "work": "▣",
    "business": "▣",
    "career": "▣",
    "experience": "▣",
    "build": "⚒",
    "engineering": "⚒",
    "skills": "◇",

    # Opportunities
    "bookmark": "▮",
    "bookmark_border": "▯",
    "star": "★",
    "star_border": "☆",
    "trophy": "♜",
    "bolt": "ϟ",
    "target": "◎",
    "check": "✓",
    "check_circle": "●",

    # Dashboard / application
    "dashboard": "▦",
    "list": "☷",
    "list_alt": "☷",
    "calendar": "▦",
    "event": "▦",
    "notifications": "◇",
    "notification": "◇",
    "chat": "▱",
    "message": "▱",
    "download": "⇩",
    "upload": "⇧",

    # Security / settings
    "settings": "⚙",
    "lock": "▣",
    "unlock": "□",
    "security": "⬟",
    "shield": "⬟",
    "logout": "↪",
    "login": "↪",

    # UI / content
    "clipboard": "▣",
    "camera": "▣",
    "palette": "◈",
    "filter": "▽",
    "sort": "⇅",
    "info": "i",
    "help": "?",
    "warning": "!",
    "error": "!",
    "visibility": "◎",
    "visibility_off": "⊘",

    # AI / assistant
    "smart_toy": "◇",
    "psychology": "◇",
    "auto_awesome": "✦",
    "assistant": "◇",
    "ai": "◇",

    # Miscellaneous
    "folder": "▰",
    "folder_open": "▰",
    "more": "⋮",
    "more_vert": "⋮",
    "more_horiz": "…",
}


def svg(name: str, size: int = 20, color: str = "currentColor") -> str:
    """
    Return a professional non-SVG icon as an HTML span.

    The function is intentionally still named `svg` so existing
    EduPilot AI files do not need to be changed.

    Example:
        svg("person", 20, "#1B2A4A")
    """

    # Use bookmark as a safe fallback for unknown icon names.
    symbol = _ICONS.get(name, _ICONS["bookmark"])

    # Keep the visual appearance consistent with the existing UI.
    return (
        f'<span '
        f'style="'
        f'display:inline-flex;'
        f'align-items:center;'
        f'justify-content:center;'
        f'width:{size}px;'
        f'height:{size}px;'
        f'font-size:{max(size - 2, 12)}px;'
        f'line-height:1;'
        f'font-family:"Segoe UI Symbol","Segoe UI",sans-serif;'
        f'font-weight:600;'
        f'color:{color};'
        f'vertical-align:middle;'
        f'">'
        f'{symbol}'
        f'</span>'
    )

