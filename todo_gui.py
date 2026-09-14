
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import sqlite3
import hashlib
import hmac
import secrets
import os
import re
import csv
import json
import traceback
import shutil
from datetime import datetime


# ============================================================
# OPTIONAL LIBRARIES
# ============================================================

try:
    from PIL import Image, ImageTk, ImageEnhance
    PIL_AVAILABLE = True
except Exception:
    Image = None
    ImageTk = None
    ImageEnhance = None
    PIL_AVAILABLE = False


try:
    from plyer import notification
    PLYER_AVAILABLE = True
except Exception:
    notification = None
    PLYER_AVAILABLE = False


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "ToDO ✓"
APP_SUBTITLE = "can do"

# ------------------------------------------------------------
# Application directory
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ------------------------------------------------------------
# Windows user data directory
#
# The EXE itself can be installed anywhere.
# User data is stored separately in APPDATA.
# ------------------------------------------------------------

APP_DATA_DIR = os.path.join(
    os.environ.get(
        "APPDATA",
        os.path.expanduser("~")
    ),
    "ToDO"
)

os.makedirs(
    APP_DATA_DIR,
    exist_ok=True
)

# ------------------------------------------------------------
# Current application data files
# ------------------------------------------------------------

DB_FILE = os.path.join(
    APP_DATA_DIR,
    "tasks.db"
)

THEME_FILE = os.path.join(
    APP_DATA_DIR,
    "theme.json"
)

# ------------------------------------------------------------
# Legacy files
#
# These are the files used by the old development version.
# We migrate them automatically on first startup.
# ------------------------------------------------------------

LEGACY_DB_FILE = os.path.join(
    BASE_DIR,
    "tasks.db"
)

LEGACY_THEME_FILE = os.path.join(
    BASE_DIR,
    "theme.json"
)

CURRENT_DB_VERSION = 5

REMINDER_CHECK_MS = 10000

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 580

MIN_WIDTH = 820
MIN_HEIGHT = 520


# ============================================================
# DATA MIGRATION
# ============================================================

def migrate_legacy_data():

    """
    Move/copy old project data into the Windows user-data
    directory.

    Old version:
        Project folder/tasks.db
        Project folder/theme.json

    New version:
        %APPDATA%/ToDO/tasks.db
        %APPDATA%/ToDO/theme.json

    Existing new files are never overwritten.
    """

    # --------------------------------------------------------
    # Database migration
    # --------------------------------------------------------

    try:

        if (
            os.path.exists(LEGACY_DB_FILE)
            and not os.path.exists(DB_FILE)
        ):

            shutil.copy2(
                LEGACY_DB_FILE,
                DB_FILE
            )

            print(
                "Migrated old database to:",
                DB_FILE
            )

    except Exception as error:

        print(
            "Database migration error:",
            error
        )

    # --------------------------------------------------------
    # Theme migration
    # --------------------------------------------------------

    try:

        if (
            os.path.exists(LEGACY_THEME_FILE)
            and not os.path.exists(THEME_FILE)
        ):

            shutil.copy2(
                LEGACY_THEME_FILE,
                THEME_FILE
            )

            print(
                "Migrated old theme file to:",
                THEME_FILE
            )

    except Exception as error:

        print(
            "Theme migration error:",
            error
        )


# ============================================================
# FONTS
# ============================================================

FONT_XS = ("Segoe UI", 9)
FONT_SMALL = ("Segoe UI", 10)
FONT_NORMAL = ("Segoe UI", 11)
FONT_MEDIUM = ("Segoe UI Semibold", 11)
FONT_BUTTON = ("Segoe UI Semibold", 10)
FONT_TITLE = ("Segoe UI Semibold", 18)
FONT_SECTION = ("Segoe UI Semibold", 12)
FONT_TASK_TITLE = ("Segoe UI Semibold", 11)
FONT_TASK_DESC = ("Segoe UI", 10)
FONT_BIG_NUMBER = ("Segoe UI Semibold", 16)


# ============================================================
# READY-MADE THEMES
# ============================================================

THEMES = {

    "Midnight": {
        "APP_BG": "#080C12",
        "SIDEBAR_BG": "#0C1420",
        "PANEL_BG": "#121C29",
        "CARD_BG": "#17263A",
        "CARD_HOVER": "#213B59",
        "INPUT_BG": "#15283E",
        "TEXT": "#F8FBFF",
        "MUTED": "#9CB0C8",
        "BORDER": "#2A4664",
        "ACCENT": "#4D7CFF",
        "ACCENT_HOVER": "#6B94FF",
        "SUCCESS": "#27D69A",
        "WARNING": "#FFB83D",
        "DANGER": "#FF596B",
        "PURPLE": "#A66CFF",
        "BACKGROUND_IMAGE": ""
    },

    "Ocean": {
        "APP_BG": "#061218",
        "SIDEBAR_BG": "#081A22",
        "PANEL_BG": "#0D252F",
        "CARD_BG": "#12333F",
        "CARD_HOVER": "#194653",
        "INPUT_BG": "#102C37",
        "TEXT": "#F2FCFF",
        "MUTED": "#8EB8C4",
        "BORDER": "#24515F",
        "ACCENT": "#18B8D8",
        "ACCENT_HOVER": "#39CDE6",
        "SUCCESS": "#29D6A0",
        "WARNING": "#FFC857",
        "DANGER": "#FF6174",
        "PURPLE": "#A978FF",
        "BACKGROUND_IMAGE": ""
    },

    "Emerald": {
        "APP_BG": "#07110D",
        "SIDEBAR_BG": "#0A1812",
        "PANEL_BG": "#10231A",
        "CARD_BG": "#153225",
        "CARD_HOVER": "#1D4834",
        "INPUT_BG": "#132B20",
        "TEXT": "#F3FFF8",
        "MUTED": "#99B8A7",
        "BORDER": "#28523D",
        "ACCENT": "#23C982",
        "ACCENT_HOVER": "#45DEA0",
        "SUCCESS": "#39E59C",
        "WARNING": "#FFC857",
        "DANGER": "#FF6578",
        "PURPLE": "#B07AFF",
        "BACKGROUND_IMAGE": ""
    },

    "Purple": {
        "APP_BG": "#0D0914",
        "SIDEBAR_BG": "#150D20",
        "PANEL_BG": "#21142E",
        "CARD_BG": "#2B1B3B",
        "CARD_HOVER": "#3D2852",
        "INPUT_BG": "#271836",
        "TEXT": "#FCF8FF",
        "MUTED": "#B8A8C7",
        "BORDER": "#51396A",
        "ACCENT": "#A66CFF",
        "ACCENT_HOVER": "#BB8AFF",
        "SUCCESS": "#36DDA0",
        "WARNING": "#FFC857",
        "DANGER": "#FF6376",
        "PURPLE": "#C084FF",
        "BACKGROUND_IMAGE": ""
    },

    "Rose": {
        "APP_BG": "#140A0F",
        "SIDEBAR_BG": "#1D0D15",
        "PANEL_BG": "#2A141F",
        "CARD_BG": "#361A28",
        "CARD_HOVER": "#4A2537",
        "INPUT_BG": "#301723",
        "TEXT": "#FFF8FB",
        "MUTED": "#C7A9B5",
        "BORDER": "#603447",
        "ACCENT": "#FF5F8F",
        "ACCENT_HOVER": "#FF7EA5",
        "SUCCESS": "#38D99D",
        "WARNING": "#FFC857",
        "DANGER": "#FF596B",
        "PURPLE": "#B77AFF",
        "BACKGROUND_IMAGE": ""
    },

    "Light": {
        "APP_BG": "#EEF2F7",
        "SIDEBAR_BG": "#FFFFFF",
        "PANEL_BG": "#FFFFFF",
        "CARD_BG": "#F7F9FC",
        "CARD_HOVER": "#E8EEF8",
        "INPUT_BG": "#F1F4F8",
        "TEXT": "#172033",
        "MUTED": "#69778C",
        "BORDER": "#D5DDE8",
        "ACCENT": "#3867E8",
        "ACCENT_HOVER": "#557FEF",
        "SUCCESS": "#159A70",
        "WARNING": "#D58B00",
        "DANGER": "#D83C50",
        "PURPLE": "#8054D6",
        "BACKGROUND_IMAGE": ""
    }
}


DEFAULT_THEME = THEMES["Midnight"].copy()


# ============================================================
# GLOBAL VARIABLES
# ============================================================

current_user_id = None
current_username = ""

active_filter = "all"
selected_task_id = None

search_var = None

main_container = None
sidebar = None
content_area = None

task_list_frame = None
details_frame = None
stats_frame = None

total_label = None
completed_label = None
pending_label = None
progress_bar = None
progress_text = None

background_label = None
background_image = None

theme = DEFAULT_THEME.copy()
current_theme_name = "Midnight"


# ============================================================
# ROOT
# ============================================================

main_window = tk.Tk()

main_window.title(APP_NAME)
main_window.geometry(
    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
)
main_window.minsize(
    MIN_WIDTH,
    MIN_HEIGHT
)
main_window.configure(
    bg=theme["APP_BG"]
)


# ============================================================
# ERROR HANDLER
# ============================================================

def report_callback_exception(
    exc,
    val,
    tb
):

    error = "".join(
        traceback.format_exception(
            exc,
            val,
            tb
        )
    )

    print(
        "\n========== TODO ERROR =========="
    )

    print(error)

    print(
        "================================\n"
    )

    try:

        messagebox.showerror(
            "ToDO Error",
            f"An unexpected error occurred:\n\n{val}"
        )

    except Exception:

        pass


main_window.report_callback_exception = (
    report_callback_exception
)


# ============================================================
# THEME STORAGE
# ============================================================

def load_theme():

    global theme
    global current_theme_name

    theme = DEFAULT_THEME.copy()

    current_theme_name = "Midnight"

    if not os.path.exists(THEME_FILE):

        return

    try:

        with open(
            THEME_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            saved_data = json.load(file)

        if not isinstance(
            saved_data,
            dict
        ):

            return

        saved_theme_name = saved_data.get(
            "theme_name",
            "Midnight"
        )

        if saved_theme_name in THEMES:

            current_theme_name = (
                saved_theme_name
            )

            theme = THEMES[
                saved_theme_name
            ].copy()

        saved_colors = saved_data.get(
            "colors",
            {}
        )

        if isinstance(
            saved_colors,
            dict
        ):

            for key in theme:

                if key in saved_colors:

                    theme[key] = (
                        saved_colors[key]
                    )

        background = saved_data.get(
            "background",
            theme.get(
                "BACKGROUND_IMAGE",
                ""
            )
        )

        theme["BACKGROUND_IMAGE"] = (
            background or ""
        )

    except Exception:

        theme = DEFAULT_THEME.copy()

        current_theme_name = "Midnight"


def save_theme():

    try:

        data = {
            "theme_name": current_theme_name,
            "colors": theme.copy(),
            "background": theme.get(
                "BACKGROUND_IMAGE",
                ""
            )
        }

        with open(
            THEME_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    except Exception as error:

        print(
            "Theme save error:",
            error
        )


# ------------------------------------------------------------
# IMPORTANT:
# Migrate old files BEFORE loading theme/database.
# ------------------------------------------------------------

migrate_legacy_data()

load_theme()


# ============================================================
# DATABASE
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DB_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


def migrate_database():

    connection = get_connection()

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # USERS
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE COLLATE NOCASE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # ----------------------------------------------------
        # TASKS
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT 'General',
                priority TEXT DEFAULT 'Medium',
                due_date TEXT DEFAULT '',
                completed INTEGER DEFAULT 0,
                important INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                user_id INTEGER DEFAULT NULL,
                reminder_enabled INTEGER DEFAULT 0,
                reminder_at TEXT DEFAULT '',
                reminder_sent INTEGER DEFAULT 0
            )
        """)

        # ----------------------------------------------------
        # MIGRATION
        # ----------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(tasks)"
        )

        existing_columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        required_columns = {

            "description":
                "TEXT DEFAULT ''",

            "category":
                "TEXT DEFAULT 'General'",

            "priority":
                "TEXT DEFAULT 'Medium'",

            "due_date":
                "TEXT DEFAULT ''",

            "completed":
                "INTEGER DEFAULT 0",

            "important":
                "INTEGER DEFAULT 0",

            "created_at":
                "TEXT DEFAULT ''",

            "user_id":
                "INTEGER DEFAULT NULL",

            "reminder_enabled":
                "INTEGER DEFAULT 0",

            "reminder_at":
                "TEXT DEFAULT ''",

            "reminder_sent":
                "INTEGER DEFAULT 0"
        }

        for column_name, definition in (
            required_columns.items()
        ):

            if column_name not in existing_columns:

                try:

                    cursor.execute(
                        f"""
                        ALTER TABLE tasks
                        ADD COLUMN {column_name} {definition}
                        """
                    )

                except Exception as error:

                    print(
                        f"Could not add {column_name}:",
                        error
                    )

        # ----------------------------------------------------
        # CLEAN DATA
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE tasks
            SET title = 'Untitled Task'
            WHERE title IS NULL
            OR TRIM(title) = ''
        """)

        cursor.execute("""
            UPDATE tasks
            SET description = ''
            WHERE description IS NULL
        """)

        cursor.execute("""
            UPDATE tasks
            SET category = 'General'
            WHERE category IS NULL
            OR TRIM(category) = ''
        """)

        cursor.execute("""
            UPDATE tasks
            SET priority = 'Medium'
            WHERE priority IS NULL
            OR TRIM(priority) = ''
        """)

        cursor.execute("""
            UPDATE tasks
            SET due_date = ''
            WHERE due_date IS NULL
        """)

        cursor.execute("""
            UPDATE tasks
            SET reminder_at = ''
            WHERE reminder_at IS NULL
        """)

        cursor.execute("""
            UPDATE tasks
            SET reminder_enabled = 0
            WHERE reminder_enabled IS NULL
        """)

        cursor.execute("""
            UPDATE tasks
            SET reminder_sent = 0
            WHERE reminder_sent IS NULL
        """)

        cursor.execute("""
            UPDATE tasks
            SET completed = 0
            WHERE completed IS NULL
        """)

        cursor.execute("""
            UPDATE tasks
            SET important = 0
            WHERE important IS NULL
        """)

        # ----------------------------------------------------
        # INDEXES
        # ----------------------------------------------------

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_user_id
            ON tasks(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_completed
            ON tasks(completed)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_reminder
            ON tasks(reminder_enabled, reminder_sent)
        """)

        cursor.execute(
            f"PRAGMA user_version = {CURRENT_DB_VERSION}"
        )

        connection.commit()

    finally:

        connection.close()


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(
    password,
    salt=None
):

    if salt is None:

        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        180000
    ).hex()

    return password_hash, salt


def verify_password(
    password,
    stored_hash,
    stored_salt
):

    password_hash, _ = hash_password(
        password,
        stored_salt
    )

    return hmac.compare_digest(
        password_hash,
        stored_hash
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_username(username):

    if not 3 <= len(username) <= 20:

        return False

    return re.fullmatch(
        r"[A-Za-z0-9_]+",
        username
    ) is not None


def validate_date(date_text):

    if not date_text.strip():

        return True

    try:

        datetime.strptime(
            date_text.strip(),
            "%Y-%m-%d"
        )

        return True

    except ValueError:

        return False


def validate_time(time_text):

    if not time_text.strip():

        return True

    try:

        datetime.strptime(
            time_text.strip(),
            "%H:%M"
        )

        return True

    except ValueError:

        return False


# ============================================================
# UI HELPERS
# ============================================================

def clear_root():

    global selected_task_id
    global background_label
    global background_image

    selected_task_id = None

    background_label = None
    background_image = None

    for widget in main_window.winfo_children():

        widget.destroy()


def create_button(
    parent,
    text,
    command,
    bg=None,
    fg=None,
    width=None
):

    if bg is None:

        bg = theme["ACCENT"]

    if fg is None:

        fg = theme["TEXT"]

    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=theme["ACCENT_HOVER"],
        activeforeground=theme["TEXT"],
        relief="flat",
        bd=0,
        cursor="hand2",
        font=FONT_BUTTON,
        padx=10,
        pady=7
    )

    if width:

        button.configure(
            width=width
        )

    return button


def create_entry(
    parent,
    textvariable=None
):

    return tk.Entry(
        parent,
        textvariable=textvariable,
        bg=theme["INPUT_BG"],
        fg=theme["TEXT"],
        insertbackground=theme["TEXT"],
        selectbackground=theme["ACCENT"],
        selectforeground=theme["TEXT"],
        relief="flat",
        bd=0,
        font=FONT_NORMAL
    )


# ============================================================
# BRAND LOGO
# ============================================================

def create_logo(
    parent,
    compact=False,
    centered=False
):

    if compact:

        logo_frame = tk.Frame(
            parent,
            bg=theme["SIDEBAR_BG"]
        )

        if centered:

            logo_frame.pack(
                pady=(20, 8)
            )

        else:

            logo_frame.pack(
                anchor="w",
                padx=18,
                pady=(18, 8)
            )

        logo_top = tk.Frame(
            logo_frame,
            bg=theme["SIDEBAR_BG"]
        )

        logo_top.pack()

        tk.Label(
            logo_top,
            text="To",
            bg=theme["SIDEBAR_BG"],
            fg=theme["TEXT"],
            font=("Segoe UI Semibold", 20)
        ).pack(
            side="left"
        )

        tk.Label(
            logo_top,
            text="DO",
            bg=theme["SIDEBAR_BG"],
            fg=theme["ACCENT"],
            font=("Segoe UI Semibold", 20)
        ).pack(
            side="left"
        )

        tk.Label(
            logo_top,
            text=" ✓",
            bg=theme["SIDEBAR_BG"],
            fg=theme["SUCCESS"],
            font=("Segoe UI Semibold", 18)
        ).pack(
            side="left"
        )

        tk.Label(
            logo_frame,
            text=APP_SUBTITLE,
            bg=theme["SIDEBAR_BG"],
            fg=theme["MUTED"],
            font=("Segoe UI", 9)
        ).pack(
            anchor="e",
            padx=(0, 3)
        )

        return logo_frame

    logo_frame = tk.Frame(
        parent,
        bg=theme["APP_BG"]
    )

    logo_frame.pack(
        pady=(15, 5)
    )

    logo_top = tk.Frame(
        logo_frame,
        bg=theme["APP_BG"]
    )

    logo_top.pack()

    tk.Label(
        logo_top,
        text="To",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=("Segoe UI Semibold", 28)
    ).pack(
        side="left"
    )

    tk.Label(
        logo_top,
        text="DO",
        bg=theme["APP_BG"],
        fg=theme["ACCENT"],
        font=("Segoe UI Semibold", 28)
    ).pack(
        side="left"
    )

    tk.Label(
        logo_top,
        text=" ✓",
        bg=theme["APP_BG"],
        fg=theme["SUCCESS"],
        font=("Segoe UI Semibold", 25)
    ).pack(
        side="left"
    )

    tk.Label(
        logo_frame,
        text=APP_SUBTITLE,
        bg=theme["APP_BG"],
        fg=theme["MUTED"],
        font=("Segoe UI", 10)
    ).pack(
        anchor="e",
        padx=(0, 5)
    )

    return logo_frame


# ============================================================
# LOGIN
# ============================================================

def show_login_screen():

    global current_user_id
    global current_username

    current_user_id = None
    current_username = ""

    clear_root()

    main_window.title(
        f"{APP_NAME} - Login"
    )

    main_window.geometry(
        "450x470"
    )

    main_window.minsize(
        400,
        420
    )

    main_window.configure(
        bg=theme["APP_BG"]
    )

    container = tk.Frame(
        main_window,
        bg=theme["APP_BG"]
    )

    container.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=25
    )

    create_logo(
        container,
        compact=False
    )

    tk.Label(
        container,
        text="Organize your day. Stay productive.",
        bg=theme["APP_BG"],
        fg=theme["MUTED"],
        font=FONT_SMALL
    ).pack(
        pady=(0, 18)
    )

    card = tk.Frame(
        container,
        bg=theme["PANEL_BG"],
        highlightbackground=theme["BORDER"],
        highlightthickness=1
    )

    card.pack(
        fill="x",
        padx=8
    )

    tk.Label(
        card,
        text="Username",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=25,
        pady=(20, 6)
    )

    username_entry = create_entry(card)

    username_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )

    tk.Label(
        card,
        text="Password",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=25,
        pady=(14, 6)
    )

    password_entry = create_entry(card)

    password_entry.configure(
        show="●"
    )

    password_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )

    def login():

        username = username_entry.get().strip()

        password = password_entry.get()

        if not username or not password:

            messagebox.showwarning(
                "Login",
                "Please enter username and password."
            )

            return

        connection = get_connection()

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT *
                FROM users
                WHERE username = ?
                COLLATE NOCASE
            """, (
                username,
            ))

            user = cursor.fetchone()

        finally:

            connection.close()

        if user is None:

            messagebox.showerror(
                "Login Failed",
                "Username or password is incorrect."
            )

            return

        if not verify_password(
            password,
            user["password_hash"],
            user["password_salt"]
        ):

            messagebox.showerror(
                "Login Failed",
                "Username or password is incorrect."
            )

            return

        global current_user_id
        global current_username

        current_user_id = user["id"]

        current_username = user["username"]

        start_main_application()

    create_button(
        card,
        "Login",
        login
    ).pack(
        fill="x",
        padx=25,
        pady=(20, 8)
    )

    create_button(
        card,
        "Create Account",
        show_register_screen,
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=25,
        pady=(0, 20)
    )

    password_entry.bind(
        "<Return>",
        lambda event: login()
    )

    username_entry.focus_set()


# ============================================================
# REGISTER
# ============================================================

def show_register_screen():

    clear_root()

    main_window.title(
        f"{APP_NAME} - Create Account"
    )

    main_window.geometry(
        "450x540"
    )

    main_window.minsize(
        400,
        500
    )

    container = tk.Frame(
        main_window,
        bg=theme["APP_BG"]
    )

    container.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=20
    )

    create_logo(
        container,
        compact=False
    )

    tk.Label(
        container,
        text="Create your personal ToDO account",
        bg=theme["APP_BG"],
        fg=theme["MUTED"],
        font=FONT_SMALL
    ).pack(
        pady=(0, 15)
    )

    card = tk.Frame(
        container,
        bg=theme["PANEL_BG"],
        highlightbackground=theme["BORDER"],
        highlightthickness=1
    )

    card.pack(
        fill="x",
        padx=8
    )

    tk.Label(
        card,
        text="Username",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )

    username_entry = create_entry(card)

    username_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )

    tk.Label(
        card,
        text="Password",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=25,
        pady=(12, 5)
    )

    password_entry = create_entry(card)

    password_entry.configure(
        show="●"
    )

    password_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )

    tk.Label(
        card,
        text="Confirm Password",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=25,
        pady=(12, 5)
    )

    confirm_entry = create_entry(card)

    confirm_entry.configure(
        show="●"
    )

    confirm_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )

    def register():

        username = username_entry.get().strip()

        password = password_entry.get()

        confirm = confirm_entry.get()

        if not validate_username(username):

            messagebox.showwarning(
                "Invalid Username",
                "Username must be 3-20 characters.\n"
                "Only letters, numbers and underscore are allowed."
            )

            return

        if len(password) < 6:

            messagebox.showwarning(
                "Invalid Password",
                "Password must contain at least 6 characters."
            )

            return

        if password != confirm:

            messagebox.showwarning(
                "Password",
                "Passwords do not match."
            )

            return

        password_hash, salt = hash_password(
            password
        )

        connection = get_connection()

        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO users
                (
                    username,
                    password_hash,
                    password_salt,
                    created_at
                )
                VALUES (?, ?, ?, ?)
            """, (
                username,
                password_hash,
                salt,
                datetime.now().isoformat(
                    timespec="seconds"
                )
            ))

            new_user_id = cursor.lastrowid

            cursor.execute("""
                SELECT COUNT(*)
                FROM users
            """)

            user_count = cursor.fetchone()[0]

            if user_count == 1:

                cursor.execute("""
                    UPDATE tasks
                    SET user_id = ?
                    WHERE user_id IS NULL
                """, (
                    new_user_id,
                ))

            connection.commit()

        except sqlite3.IntegrityError:

            connection.rollback()

            connection.close()

            messagebox.showerror(
                "Create Account",
                "This username already exists."
            )

            return

        except Exception as error:

            connection.rollback()

            connection.close()

            messagebox.showerror(
                "Create Account",
                str(error)
            )

            return

        connection.close()

        messagebox.showinfo(
            "Account Created",
            "Your account has been created successfully."
        )

        show_login_screen()

    create_button(
        card,
        "Create Account",
        register
    ).pack(
        fill="x",
        padx=25,
        pady=(18, 8)
    )

    create_button(
        card,
        "Back to Login",
        show_login_screen,
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=25,
        pady=(0, 18)
    )

    confirm_entry.bind(
        "<Return>",
        lambda event: register()
    )

    username_entry.focus_set()


# ============================================================
# MAIN APPLICATION
# ============================================================

def start_main_application():

    clear_root()

    main_window.title(
        f"{APP_NAME} - {current_username}"
    )

    main_window.geometry(
        f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
    )

    main_window.minsize(
        MIN_WIDTH,
        MIN_HEIGHT
    )

    main_window.configure(
        bg=theme["APP_BG"]
    )

    build_main_ui()

    refresh_tasks()

    main_window.after(
        100,
        apply_background_image
    )

    main_window.after(
        1000,
        check_reminders
    )


# ============================================================
# LOGOUT
# ============================================================

def logout():

    global current_user_id
    global current_username

    answer = messagebox.askyesno(
        "Logout",
        "Are you sure you want to logout?"
    )

    if not answer:

        return

    current_user_id = None

    current_username = ""

    show_login_screen()


# ============================================================
# MAIN UI
# ============================================================

def build_main_ui():

    global main_container
    global sidebar
    global content_area
    global task_list_frame
    global details_frame
    global stats_frame

    global total_label
    global completed_label
    global pending_label
    global progress_bar
    global progress_text

    global search_var

    main_container = tk.Frame(
        main_window,
        bg=theme["APP_BG"]
    )

    main_container.pack(
        fill="both",
        expand=True
    )

    sidebar = tk.Frame(
        main_container,
        bg=theme["SIDEBAR_BG"],
        width=215
    )

    sidebar.pack(
        side="left",
        fill="y"
    )

    sidebar.pack_propagate(False)

    create_logo(
        sidebar,
        compact=True
    )

    tk.Label(
        sidebar,
        text=f"👤  {current_username}",
        bg=theme["SIDEBAR_BG"],
        fg=theme["MUTED"],
        font=FONT_SMALL
    ).pack(
        anchor="w",
        padx=18,
        pady=(0, 15)
    )

    create_sidebar_button(
        "📋  All Tasks",
        "all"
    ).pack(
        fill="x",
        padx=10,
        pady=2
    )

    create_sidebar_button(
        "⏳  Pending",
        "pending"
    ).pack(
        fill="x",
        padx=10,
        pady=2
    )

    create_sidebar_button(
        "✓  Completed",
        "completed"
    ).pack(
        fill="x",
        padx=10,
        pady=2
    )

    create_sidebar_button(
        "⭐  Important",
        "important"
    ).pack(
        fill="x",
        padx=10,
        pady=2
    )

    create_sidebar_button(
        "🔔  Reminders",
        "reminders"
    ).pack(
        fill="x",
        padx=10,
        pady=2
    )

    tk.Frame(
        sidebar,
        bg=theme["BORDER"],
        height=1
    ).pack(
        fill="x",
        padx=15,
        pady=16
    )

    create_button(
        sidebar,
        "＋  Add Task",
        open_add_task_dialog
    ).pack(
        fill="x",
        padx=15,
        pady=4
    )

    create_button(
        sidebar,
        "🎨  Appearance",
        open_appearance,
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=15,
        pady=4
    )

    create_button(
        sidebar,
        "⇩  Import CSV",
        import_csv,
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=15,
        pady=4
    )

    create_button(
        sidebar,
        "⇧  Export CSV",
        export_csv,
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=15,
        pady=4
    )

    create_button(
        sidebar,
        "🗑  Clear All",
        clear_all_tasks,
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=15,
        pady=4
    )

    create_button(
        sidebar,
        "↪  Logout",
        logout,
        bg=theme["DANGER"]
    ).pack(
        side="bottom",
        fill="x",
        padx=15,
        pady=15
    )

    content_area = tk.Frame(
        main_container,
        bg=theme["APP_BG"]
    )

    content_area.pack(
        side="left",
        fill="both",
        expand=True
    )

    top_bar = tk.Frame(
        content_area,
        bg=theme["APP_BG"]
    )

    top_bar.pack(
        fill="x",
        padx=18,
        pady=(15, 7)
    )

    title_section = tk.Frame(
        top_bar,
        bg=theme["APP_BG"]
    )

    title_section.pack(
        side="left"
    )

    tk.Label(
        title_section,
        text="My Tasks",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_TITLE
    ).pack(
        anchor="w"
    )

    tk.Label(
        title_section,
        text="Stay organized. Get things done.",
        bg=theme["APP_BG"],
        fg=theme["MUTED"],
        font=FONT_XS
    ).pack(
        anchor="w"
    )

    search_var = tk.StringVar()

    search_container = tk.Frame(
        top_bar,
        bg=theme["INPUT_BG"],
        highlightbackground=theme["BORDER"],
        highlightthickness=1
    )

    search_container.pack(
        side="right",
        padx=(10, 0)
    )

    tk.Label(
        search_container,
        text="🔎",
        bg=theme["INPUT_BG"],
        fg=theme["MUTED"],
        font=FONT_NORMAL
    ).pack(
        side="left",
        padx=(10, 3)
    )

    search_entry = create_entry(
        search_container,
        search_var
    )

    search_entry.configure(
        width=25
    )

    search_entry.pack(
        side="left",
        ipadx=5,
        ipady=6,
        padx=(0, 8)
    )

    search_var.trace_add(
        "write",
        lambda *args: refresh_tasks()
    )

    stats_frame = tk.Frame(
        content_area,
        bg=theme["APP_BG"]
    )

    stats_frame.pack(
        fill="x",
        padx=18,
        pady=5
    )

    total_label = create_stat_card(
        stats_frame,
        "Total",
        theme["ACCENT"]
    )

    total_label.master.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(0, 5)
    )

    completed_label = create_stat_card(
        stats_frame,
        "Completed",
        theme["SUCCESS"]
    )

    completed_label.master.pack(
        side="left",
        fill="x",
        expand=True,
        padx=5
    )

    pending_label = create_stat_card(
        stats_frame,
        "Pending",
        theme["WARNING"]
    )

    pending_label.master.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(5, 0)
    )

    progress_container = tk.Frame(
        content_area,
        bg=theme["APP_BG"]
    )

    progress_container.pack(
        fill="x",
        padx=18,
        pady=(7, 8)
    )

    progress_text = tk.Label(
        progress_container,
        text="0% completed",
        bg=theme["APP_BG"],
        fg=theme["MUTED"],
        font=FONT_XS
    )

    progress_text.pack(
        side="left"
    )

    style = ttk.Style()

    try:

        style.theme_use("clam")

    except Exception:

        pass

    style.configure(
        "Task.Horizontal.TProgressbar",
        troughcolor=theme["PANEL_BG"],
        background=theme["SUCCESS"],
        bordercolor=theme["PANEL_BG"],
        lightcolor=theme["SUCCESS"],
        darkcolor=theme["SUCCESS"]
    )

    progress_bar = ttk.Progressbar(
        progress_container,
        style="Task.Horizontal.TProgressbar",
        maximum=100,
        value=0
    )

    progress_bar.pack(
        side="right",
        fill="x",
        expand=True,
        padx=(12, 0)
    )

    body = tk.Frame(
        content_area,
        bg=theme["APP_BG"]
    )

    body.pack(
        fill="both",
        expand=True,
        padx=18,
        pady=(0, 15)
    )

    list_container = tk.Frame(
        body,
        bg=theme["PANEL_BG"],
        highlightbackground=theme["BORDER"],
        highlightthickness=1
    )

    list_container.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )

    list_header = tk.Frame(
        list_container,
        bg=theme["PANEL_BG"]
    )

    list_header.pack(
        fill="x",
        padx=12,
        pady=10
    )

    tk.Label(
        list_header,
        text="Tasks",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_SECTION
    ).pack(
        side="left"
    )

    create_button(
        list_header,
        "Edit",
        edit_selected_task,
        bg=theme["CARD_BG"]
    ).pack(
        side="right",
        padx=2
    )

    create_button(
        list_header,
        "Delete",
        delete_selected_task,
        bg=theme["DANGER"]
    ).pack(
        side="right",
        padx=2
    )

    create_button(
        list_header,
        "Complete",
        complete_selected_task,
        bg=theme["SUCCESS"],
        fg="#07120E"
    ).pack(
        side="right",
        padx=2
    )

    canvas = tk.Canvas(
        list_container,
        bg=theme["PANEL_BG"],
        highlightthickness=0
    )

    scrollbar = tk.Scrollbar(
        list_container,
        orient="vertical",
        command=canvas.yview
    )

    task_list_frame = tk.Frame(
        canvas,
        bg=theme["PANEL_BG"]
    )

    task_list_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=task_list_frame,
        anchor="nw"
    )

    def resize_task_frame(event):

        canvas.itemconfig(
            canvas_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_task_frame
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    canvas.bind_all(
        "<MouseWheel>",
        lambda event: canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )
    )

    details_frame = tk.Frame(
        body,
        bg=theme["PANEL_BG"],
        width=245,
        highlightbackground=theme["BORDER"],
        highlightthickness=1
    )

    details_frame.pack(
        side="right",
        fill="y"
    )

    details_frame.pack_propagate(False)

    show_empty_details()

    main_window.bind(
        "<Control-n>",
        lambda event: open_add_task_dialog()
    )

    main_window.bind(
        "<Control-f>",
        lambda event: focus_search()
    )

    main_window.bind(
        "<Delete>",
        lambda event: delete_selected_task()
    )

    main_window.bind(
        "<Control-e>",
        lambda event: edit_selected_task()
    )

    main_window.bind(
        "<Control-q>",
        lambda event: logout()
    )


# ============================================================
# SIDEBAR BUTTON
# ============================================================

def create_sidebar_button(
    text,
    filter_name
):

    def command():

        global active_filter

        active_filter = filter_name

        refresh_tasks()

    return tk.Button(
        sidebar,
        text=text,
        command=command,
        bg=theme["SIDEBAR_BG"],
        fg=theme["TEXT"],
        activebackground=theme["CARD_HOVER"],
        activeforeground=theme["TEXT"],
        relief="flat",
        bd=0,
        anchor="w",
        padx=14,
        pady=9,
        font=FONT_SMALL,
        cursor="hand2"
    )


# ============================================================
# STAT CARD
# ============================================================

def create_stat_card(
    parent,
    title,
    color
):

    card = tk.Frame(
        parent,
        bg=theme["CARD_BG"],
        height=55,
        highlightbackground=theme["BORDER"],
        highlightthickness=1
    )

    card.pack_propagate(False)

    value_label = tk.Label(
        card,
        text="0",
        bg=theme["CARD_BG"],
        fg=color,
        font=FONT_BIG_NUMBER
    )

    value_label.pack(
        side="left",
        padx=(12, 7)
    )

    tk.Label(
        card,
        text=title,
        bg=theme["CARD_BG"],
        fg=theme["MUTED"],
        font=FONT_SMALL
    ).pack(
        side="left"
    )

    return value_label


# ============================================================
# SEARCH
# ============================================================

def focus_search():

    try:

        entry = find_entry(
            main_window
        )

        if entry:

            entry.focus_set()

    except Exception:

        pass


def find_entry(widget):

    if isinstance(
        widget,
        tk.Entry
    ):

        return widget

    for child in widget.winfo_children():

        result = find_entry(child)

        if result:

            return result

    return None


# ============================================================
# FILTER
# ============================================================

def get_filtered_tasks():

    connection = get_connection()

    cursor = connection.cursor()

    sql = """
        SELECT *
        FROM tasks
        WHERE user_id = ?
    """

    params = [
        current_user_id
    ]

    if active_filter == "pending":

        sql += """
            AND completed = 0
        """

    elif active_filter == "completed":

        sql += """
            AND completed = 1
        """

    elif active_filter == "important":

        sql += """
            AND important = 1
        """

    elif active_filter == "reminders":

        sql += """
            AND reminder_enabled = 1
            AND completed = 0
        """

    if search_var:

        search_text = (
            search_var.get().strip()
        )

        if search_text:

            sql += """
                AND (
                    title LIKE ?
                    OR description LIKE ?
                    OR category LIKE ?
                    OR priority LIKE ?
                )
            """

            pattern = (
                f"%{search_text}%"
            )

            params.extend([
                pattern,
                pattern,
                pattern,
                pattern
            ])

    sql += """
        ORDER BY
            completed ASC,
            important DESC,
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                ELSE 4
            END,
            id DESC
    """

    cursor.execute(
        sql,
        params
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# REFRESH
# ============================================================

def refresh_tasks():

    if task_list_frame is None:

        return

    for widget in (
        task_list_frame.winfo_children()
    ):

        widget.destroy()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(completed), 0) AS completed
        FROM tasks
        WHERE user_id = ?
    """, (
        current_user_id,
    ))

    stats = cursor.fetchone()

    connection.close()

    total = stats["total"]

    completed = stats["completed"]

    pending = total - completed

    if total_label:

        total_label.config(
            text=str(total)
        )

    if completed_label:

        completed_label.config(
            text=str(completed)
        )

    if pending_label:

        pending_label.config(
            text=str(pending)
        )

    percentage = 0

    if total > 0:

        percentage = int(
            completed / total * 100
        )

    if progress_bar:

        progress_bar["value"] = percentage

    if progress_text:

        progress_text.config(
            text=f"{percentage}% completed"
        )

    tasks = get_filtered_tasks()

    if not tasks:

        tk.Label(
            task_list_frame,
            text="No tasks found",
            bg=theme["PANEL_BG"],
            fg=theme["MUTED"],
            font=FONT_NORMAL
        ).pack(
            pady=50
        )

        show_empty_details()

        return

    for task in tasks:

        create_task_card(
            task_list_frame,
            task
        )


# ============================================================
# TASK CARD
# ============================================================

def create_task_card(
    parent,
    task
):

    card = tk.Frame(
        parent,
        bg=theme["CARD_BG"],
        highlightbackground=theme["BORDER"],
        highlightthickness=1,
        cursor="hand2"
    )

    card.pack(
        fill="x",
        padx=10,
        pady=5
    )

    priority_colors = {
        "High": theme["DANGER"],
        "Medium": theme["WARNING"],
        "Low": theme["SUCCESS"]
    }

    priority_color = priority_colors.get(
        task["priority"],
        theme["ACCENT"]
    )

    tk.Frame(
        card,
        bg=priority_color,
        width=4
    ).pack(
        side="left",
        fill="y"
    )

    info = tk.Frame(
        card,
        bg=theme["CARD_BG"]
    )

    info.pack(
        side="left",
        fill="both",
        expand=True,
        padx=10,
        pady=8
    )

    title_text = task["title"]

    if task["completed"]:

        title_text = (
            "✓ " + title_text
        )

    if task["important"]:

        title_text = (
            "⭐ " + title_text
        )

    title_label = tk.Label(
        info,
        text=title_text,
        bg=theme["CARD_BG"],
        fg=(
            theme["MUTED"]
            if task["completed"]
            else theme["TEXT"]
        ),
        font=FONT_TASK_TITLE,
        anchor="w"
    )

    title_label.pack(
        fill="x"
    )

    if task["description"]:

        description = task["description"]

        if len(description) > 100:

            description = (
                description[:100]
                + "..."
            )

        tk.Label(
            info,
            text=description,
            bg=theme["CARD_BG"],
            fg=theme["MUTED"],
            font=FONT_TASK_DESC,
            anchor="w",
            justify="left"
        ).pack(
            fill="x",
            pady=(3, 0)
        )

    meta = []

    if task["category"]:

        meta.append(
            f"📁 {task['category']}"
        )

    if task["priority"]:

        meta.append(
            f"⚡ {task['priority']}"
        )

    if task["due_date"]:

        meta.append(
            f"📅 {task['due_date']}"
        )

    if (
        task["reminder_enabled"]
        and task["reminder_at"]
    ):

        meta.append(
            "🔔 "
            + format_reminder(
                task["reminder_at"]
            )
        )

    if meta:

        tk.Label(
            info,
            text="   ".join(meta),
            bg=theme["CARD_BG"],
            fg=theme["MUTED"],
            font=FONT_XS,
            anchor="w"
        ).pack(
            fill="x",
            pady=(5, 0)
        )

    def select(event=None):

        global selected_task_id

        selected_task_id = task["id"]

        show_task_details(task)

    card.bind(
        "<Button-1>",
        select
    )

    for widget in card.winfo_children():

        widget.bind(
            "<Button-1>",
            select
        )

        if isinstance(
            widget,
            tk.Frame
        ):

            for subwidget in (
                widget.winfo_children()
            ):

                subwidget.bind(
                    "<Button-1>",
                    select
                )

    return card


# ============================================================
# REMINDER FORMAT
# ============================================================

def format_reminder(value):

    try:

        dt = datetime.strptime(
            value,
            "%Y-%m-%d %H:%M"
        )

        return dt.strftime(
            "%Y-%m-%d %H:%M"
        )

    except Exception:

        return value


# ============================================================
# DETAILS
# ============================================================

def clear_details():

    if details_frame is None:

        return

    for widget in (
        details_frame.winfo_children()
    ):

        widget.destroy()


def show_empty_details():

    if details_frame is None:

        return

    clear_details()

    tk.Label(
        details_frame,
        text="Task Details",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_SECTION
    ).pack(
        anchor="w",
        padx=15,
        pady=(15, 10)
    )

    tk.Label(
        details_frame,
        text="Select a task to view\nits details.",
        bg=theme["PANEL_BG"],
        fg=theme["MUTED"],
        font=FONT_SMALL,
        justify="left"
    ).pack(
        anchor="w",
        padx=15
    )


def show_task_details(task):

    if details_frame is None:

        return

    clear_details()

    tk.Label(
        details_frame,
        text="Task Details",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_SECTION
    ).pack(
        anchor="w",
        padx=15,
        pady=(15, 12)
    )

    title = task["title"]

    if task["important"]:

        title = (
            "⭐ " + title
        )

    tk.Label(
        details_frame,
        text=title,
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=("Segoe UI Semibold", 14),
        wraplength=210,
        justify="left"
    ).pack(
        anchor="w",
        padx=15
    )

    if task["description"]:

        tk.Label(
            details_frame,
            text=task["description"],
            bg=theme["PANEL_BG"],
            fg=theme["MUTED"],
            font=FONT_SMALL,
            wraplength=210,
            justify="left"
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 12)
        )

    details = [

        (
            "Category",
            task["category"]
        ),

        (
            "Priority",
            task["priority"]
        ),

        (
            "Due Date",
            task["due_date"] or "None"
        ),

        (
            "Status",
            "Completed"
            if task["completed"]
            else "Pending"
        ),

        (
            "Reminder",
            format_reminder(
                task["reminder_at"]
            )
            if (
                task["reminder_enabled"]
                and task["reminder_at"]
            )
            else "Off"
        )
    ]

    for label, value in details:

        row = tk.Frame(
            details_frame,
            bg=theme["PANEL_BG"]
        )

        row.pack(
            fill="x",
            padx=15,
            pady=4
        )

        tk.Label(
            row,
            text=label,
            bg=theme["PANEL_BG"],
            fg=theme["MUTED"],
            font=FONT_XS
        ).pack(
            side="left"
        )

        tk.Label(
            row,
            text=str(value),
            bg=theme["PANEL_BG"],
            fg=theme["TEXT"],
            font=FONT_XS,
            wraplength=120
        ).pack(
            side="right"
        )

    create_button(
        details_frame,
        "Edit Task",
        edit_selected_task
    ).pack(
        fill="x",
        padx=15,
        pady=(18, 5)
    )

    create_button(
        details_frame,
        "Delete Task",
        delete_selected_task,
        bg=theme["DANGER"]
    ).pack(
        fill="x",
        padx=15,
        pady=5
    )


# ============================================================
# ADD TASK
# ============================================================

def open_add_task_dialog():

    open_task_dialog()


# ============================================================
# EDIT TASK
# ============================================================

def edit_selected_task():

    if selected_task_id is None:

        messagebox.showinfo(
            "Edit Task",
            "Please select a task first."
        )

        return

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tasks
        WHERE id = ?
        AND user_id = ?
    """, (
        selected_task_id,
        current_user_id
    ))

    task = cursor.fetchone()

    connection.close()

    if task is None:

        messagebox.showerror(
            "Edit Task",
            "Task not found."
        )

        return

    open_task_dialog(task)


# ============================================================
# TASK DIALOG
# ============================================================

def open_task_dialog(
    task=None
):

    global selected_task_id

    is_editing = task is not None

    dialog = tk.Toplevel(
        main_window
    )

    dialog.title(
        "Edit Task"
        if is_editing
        else "Add Task"
    )

    dialog.geometry(
        "520x650"
    )

    dialog.minsize(
        480,
        600
    )

    dialog.configure(
        bg=theme["APP_BG"]
    )

    dialog.transient(
        main_window
    )

    dialog.grab_set()

    title_var = tk.StringVar(
        value=(
            task["title"]
            if task
            else ""
        )
    )

    category_var = tk.StringVar(
        value=(
            task["category"]
            if task
            else "General"
        )
    )

    priority_var = tk.StringVar(
        value=(
            task["priority"]
            if task
            else "Medium"
        )
    )

    due_var = tk.StringVar(
        value=(
            task["due_date"]
            if task
            else ""
        )
    )

    important_var = tk.BooleanVar(
        value=(
            bool(
                task["important"]
            )
            if task
            else False
        )
    )

    reminder_enabled_var = tk.BooleanVar(
        value=(
            bool(
                task["reminder_enabled"]
            )
            if task
            else False
        )
    )

    reminder_date_var = tk.StringVar()

    reminder_time_var = tk.StringVar()

    if task and task["reminder_at"]:

        try:

            reminder_datetime = datetime.strptime(
                task["reminder_at"],
                "%Y-%m-%d %H:%M"
            )

            reminder_date_var.set(
                reminder_datetime.strftime(
                    "%Y-%m-%d"
                )
            )

            reminder_time_var.set(
                reminder_datetime.strftime(
                    "%H:%M"
                )
            )

        except Exception:

            pass

    canvas = tk.Canvas(
        dialog,
        bg=theme["APP_BG"],
        highlightthickness=0
    )

    scrollbar = tk.Scrollbar(
        dialog,
        orient="vertical",
        command=canvas.yview
    )

    form = tk.Frame(
        canvas,
        bg=theme["APP_BG"]
    )

    form.bind(
        "<Configure>",
        lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    window_id = canvas.create_window(
        (0, 0),
        window=form,
        anchor="nw"
    )

    def resize_form(event):

        canvas.itemconfig(
            window_id,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_form
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    tk.Label(
        form,
        text="Task Title",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=20,
        pady=(18, 5)
    )

    title_entry = create_entry(
        form,
        title_var
    )

    title_entry.pack(
        fill="x",
        padx=20,
        ipady=8
    )

    tk.Label(
        form,
        text="Description",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 5)
    )

    description_text = tk.Text(
        form,
        height=5,
        bg=theme["INPUT_BG"],
        fg=theme["TEXT"],
        insertbackground=theme["TEXT"],
        selectbackground=theme["ACCENT"],
        relief="flat",
        bd=0,
        font=FONT_NORMAL,
        wrap="word"
    )

    description_text.pack(
        fill="x",
        padx=20
    )

    if task:

        description_text.insert(
            "1.0",
            task["description"] or ""
        )

    tk.Label(
        form,
        text="Category",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 5)
    )

    category_combo = ttk.Combobox(
        form,
        textvariable=category_var,
        values=[
            "General",
            "Work",
            "Study",
            "Personal",
            "Shopping",
            "Health",
            "Finance",
            "Programming",
            "Other"
        ],
        state="normal",
        font=FONT_NORMAL
    )

    category_combo.pack(
        fill="x",
        padx=20,
        ipady=4
    )

    tk.Label(
        form,
        text="Priority",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 5)
    )

    priority_combo = ttk.Combobox(
        form,
        textvariable=priority_var,
        values=[
            "Low",
            "Medium",
            "High"
        ],
        state="readonly",
        font=FONT_NORMAL
    )

    priority_combo.pack(
        fill="x",
        padx=20,
        ipady=4
    )

    tk.Label(
        form,
        text="Due Date (YYYY-MM-DD)",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 5)
    )

    due_entry = create_entry(
        form,
        due_var
    )

    due_entry.pack(
        fill="x",
        padx=20,
        ipady=8
    )

    tk.Checkbutton(
        form,
        text="⭐ Mark as Important",
        variable=important_var,
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        activebackground=theme["APP_BG"],
        activeforeground=theme["TEXT"],
        selectcolor=theme["INPUT_BG"],
        font=FONT_NORMAL
    ).pack(
        anchor="w",
        padx=20,
        pady=(12, 5)
    )

    reminder_card = tk.Frame(
        form,
        bg=theme["PANEL_BG"],
        highlightbackground=theme["BORDER"],
        highlightthickness=1
    )

    reminder_card.pack(
        fill="x",
        padx=20,
        pady=(15, 5)
    )

    tk.Checkbutton(
        reminder_card,
        text="🔔 Enable Reminder",
        variable=reminder_enabled_var,
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        activebackground=theme["PANEL_BG"],
        activeforeground=theme["TEXT"],
        selectcolor=theme["INPUT_BG"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=12,
        pady=(12, 8)
    )

    tk.Label(
        reminder_card,
        text="Reminder Date (YYYY-MM-DD)",
        bg=theme["PANEL_BG"],
        fg=theme["MUTED"],
        font=FONT_XS
    ).pack(
        anchor="w",
        padx=12,
        pady=(4, 3)
    )

    reminder_date_entry = create_entry(
        reminder_card,
        reminder_date_var
    )

    reminder_date_entry.pack(
        fill="x",
        padx=12,
        ipady=7
    )

    tk.Label(
        reminder_card,
        text="Reminder Time (HH:MM)",
        bg=theme["PANEL_BG"],
        fg=theme["MUTED"],
        font=FONT_XS
    ).pack(
        anchor="w",
        padx=12,
        pady=(9, 3)
    )

    reminder_time_entry = create_entry(
        reminder_card,
        reminder_time_var
    )

    reminder_time_entry.pack(
        fill="x",
        padx=12,
        ipady=7
    )

    def save_task():

        title = title_var.get().strip()

        description = description_text.get(
            "1.0",
            "end"
        ).strip()

        category = category_var.get().strip()

        priority = priority_var.get().strip()

        due_date = due_var.get().strip()

        important = (
            1
            if important_var.get()
            else 0
        )

        reminder_enabled = (
            1
            if reminder_enabled_var.get()
            else 0
        )

        reminder_date = (
            reminder_date_var.get().strip()
        )

        reminder_time = (
            reminder_time_var.get().strip()
        )

        if not title:

            messagebox.showwarning(
                "Task",
                "Please enter a task title.",
                parent=dialog
            )

            title_entry.focus_set()

            return

        if not validate_date(
            due_date
        ):

            messagebox.showwarning(
                "Due Date",
                "Invalid date.\nUse YYYY-MM-DD.",
                parent=dialog
            )

            return

        reminder_at = ""

        if reminder_enabled:

            if not reminder_date:

                messagebox.showwarning(
                    "Reminder",
                    "Please enter reminder date.",
                    parent=dialog
                )

                return

            if not reminder_time:

                messagebox.showwarning(
                    "Reminder",
                    "Please enter reminder time.",
                    parent=dialog
                )

                return

            if not validate_date(
                reminder_date
            ):

                messagebox.showwarning(
                    "Reminder",
                    "Invalid reminder date.\n"
                    "Use YYYY-MM-DD.",
                    parent=dialog
                )

                return

            if not validate_time(
                reminder_time
            ):

                messagebox.showwarning(
                    "Reminder",
                    "Invalid reminder time.\n"
                    "Use HH:MM.",
                    parent=dialog
                )

                return

            reminder_at = (
                f"{reminder_date} "
                f"{reminder_time}"
            )

            try:

                reminder_datetime = datetime.strptime(
                    reminder_at,
                    "%Y-%m-%d %H:%M"
                )

                if (
                    reminder_datetime
                    <= datetime.now()
                ):

                    messagebox.showwarning(
                        "Reminder",
                        "Reminder must be in the future.",
                        parent=dialog
                    )

                    return

            except Exception:

                messagebox.showwarning(
                    "Reminder",
                    "Invalid reminder date/time.",
                    parent=dialog
                )

                return

        connection = get_connection()

        cursor = connection.cursor()

        try:

            if is_editing:

                cursor.execute("""
                    UPDATE tasks
                    SET
                        title = ?,
                        description = ?,
                        category = ?,
                        priority = ?,
                        due_date = ?,
                        important = ?,
                        reminder_enabled = ?,
                        reminder_at = ?,
                        reminder_sent = 0
                    WHERE id = ?
                    AND user_id = ?
                """, (
                    title,
                    description,
                    category or "General",
                    priority or "Medium",
                    due_date,
                    important,
                    reminder_enabled,
                    reminder_at,
                    task["id"],
                    current_user_id
                ))

                selected_task_id = task["id"]

            else:

                cursor.execute("""
                    INSERT INTO tasks
                    (
                        title,
                        description,
                        category,
                        priority,
                        due_date,
                        completed,
                        important,
                        created_at,
                        user_id,
                        reminder_enabled,
                        reminder_at,
                        reminder_sent
                    )
                    VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, 0)
                """, (
                    title,
                    description,
                    category or "General",
                    priority or "Medium",
                    due_date,
                    important,
                    datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    current_user_id,
                    reminder_enabled,
                    reminder_at
                ))

                selected_task_id = (
                    cursor.lastrowid
                )

            connection.commit()

        except Exception as error:

            connection.rollback()

            messagebox.showerror(
                "Save Task",
                str(error),
                parent=dialog
            )

            connection.close()

            return

        connection.close()

        dialog.destroy()

        refresh_tasks()

    create_button(
        form,
        "Save Task",
        save_task
    ).pack(
        fill="x",
        padx=20,
        pady=(18, 25)
    )

    title_entry.focus_set()

    dialog.bind(
        "<Control-Return>",
        lambda event: save_task()
    )


# ============================================================
# COMPLETE TASK
# ============================================================

def complete_selected_task():

    global selected_task_id

    if selected_task_id is None:

        messagebox.showinfo(
            "Complete Task",
            "Please select a task first."
        )

        return

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT completed
        FROM tasks
        WHERE id = ?
        AND user_id = ?
    """, (
        selected_task_id,
        current_user_id
    ))

    task = cursor.fetchone()

    if task is None:

        connection.close()

        selected_task_id = None

        refresh_tasks()

        return

    new_status = (
        0
        if task["completed"]
        else 1
    )

    cursor.execute("""
        UPDATE tasks
        SET completed = ?
        WHERE id = ?
        AND user_id = ?
    """, (
        new_status,
        selected_task_id,
        current_user_id
    ))

    connection.commit()

    connection.close()

    refresh_tasks()


# ============================================================
# DELETE TASK
# ============================================================

def delete_selected_task():

    global selected_task_id

    if selected_task_id is None:

        messagebox.showinfo(
            "Delete Task",
            "Please select a task first."
        )

        return

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT title
        FROM tasks
        WHERE id = ?
        AND user_id = ?
    """, (
        selected_task_id,
        current_user_id
    ))

    task = cursor.fetchone()

    connection.close()

    if task is None:

        selected_task_id = None

        refresh_tasks()

        return

    answer = messagebox.askyesno(
        "Delete Task",
        f"Delete '{task['title']}'?"
    )

    if not answer:

        return

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM tasks
            WHERE id = ?
            AND user_id = ?
        """, (
            selected_task_id,
            current_user_id
        ))

        connection.commit()

        selected_task_id = None

    except Exception as error:

        connection.rollback()

        messagebox.showerror(
            "Delete Error",
            f"Could not delete the task.\n\n{error}"
        )

    finally:

        connection.close()

    refresh_tasks()


# ============================================================
# CLEAR ALL
# ============================================================

def clear_all_tasks():

    global selected_task_id

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE user_id = ?
    """, (
        current_user_id,
    ))

    count = cursor.fetchone()[0]

    connection.close()

    if count == 0:

        messagebox.showinfo(
            "Clear All",
            "There are no tasks."
        )

        return

    answer = messagebox.askyesno(
        "Clear All",
        f"Delete all {count} tasks?"
    )

    if not answer:

        return

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE user_id = ?
    """, (
        current_user_id,
    ))

    connection.commit()

    connection.close()

    selected_task_id = None

    refresh_tasks()


# ============================================================
# REMINDERS
# ============================================================

def check_reminders():

    if not main_window.winfo_exists():

        return

    if current_user_id is None:

        main_window.after(
            REMINDER_CHECK_MS,
            check_reminders
        )

        return

    now_text = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT *
            FROM tasks
            WHERE user_id = ?
            AND reminder_enabled = 1
            AND reminder_sent = 0
            AND completed = 0
            AND reminder_at != ''
            AND reminder_at <= ?
            ORDER BY reminder_at ASC
        """, (
            current_user_id,
            now_text
        ))

        reminders = cursor.fetchall()

        for task in reminders:

            send_notification(
                task["title"],
                task["description"]
                or "You have a task reminder."
            )

            cursor.execute("""
                UPDATE tasks
                SET reminder_sent = 1
                WHERE id = ?
                AND user_id = ?
            """, (
                task["id"],
                current_user_id
            ))

        connection.commit()

    except Exception as error:

        connection.rollback()

        print(
            "Reminder error:",
            error
        )

        reminders = []

    finally:

        connection.close()

    if reminders:

        refresh_tasks()

    try:

        main_window.after(
            REMINDER_CHECK_MS,
            check_reminders
        )

    except tk.TclError:

        pass


def send_notification(
    title,
    message
):

    if PLYER_AVAILABLE:

        try:

            notification.notify(
                title=f"{APP_NAME} 🔔",
                message=message,
                app_name=APP_NAME,
                timeout=10
            )

            return

        except Exception as error:

            print(
                "Plyer notification error:",
                error
            )

    try:

        popup = tk.Toplevel(
            main_window
        )

        popup.title(
            "Reminder"
        )

        popup.geometry(
            "350x170"
        )

        popup.configure(
            bg=theme["PANEL_BG"]
        )

        popup.transient(
            main_window
        )

        tk.Label(
            popup,
            text="🔔 Reminder",
            bg=theme["PANEL_BG"],
            fg=theme["ACCENT"],
            font=FONT_SECTION
        ).pack(
            pady=(20, 8)
        )

        tk.Label(
            popup,
            text=title,
            bg=theme["PANEL_BG"],
            fg=theme["TEXT"],
            font=FONT_MEDIUM,
            wraplength=300
        ).pack(
            padx=20
        )

        tk.Label(
            popup,
            text=message,
            bg=theme["PANEL_BG"],
            fg=theme["MUTED"],
            font=FONT_SMALL,
            wraplength=300
        ).pack(
            padx=20,
            pady=5
        )

        create_button(
            popup,
            "OK",
            popup.destroy
        ).pack(
            pady=8
        )

        popup.after(
            15000,
            lambda: (
                popup.destroy()
                if popup.winfo_exists()
                else None
            )
        )

    except Exception:

        pass


# ============================================================
# CSV EXPORT
# ============================================================

def export_csv():

    filename = filedialog.asksaveasfilename(
        title="Export Tasks",
        defaultextension=".csv",
        filetypes=[
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        ]
    )

    if not filename:

        return

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            title,
            description,
            category,
            priority,
            due_date,
            completed,
            important,
            created_at,
            reminder_enabled,
            reminder_at,
            reminder_sent
        FROM tasks
        WHERE user_id = ?
        ORDER BY id ASC
    """, (
        current_user_id,
    ))

    rows = cursor.fetchall()

    connection.close()

    fields = [
        "title",
        "description",
        "category",
        "priority",
        "due_date",
        "completed",
        "important",
        "created_at",
        "reminder_enabled",
        "reminder_at",
        "reminder_sent"
    ]

    try:

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )

            writer.writeheader()

            for row in rows:

                writer.writerow({
                    field: row[field]
                    for field in fields
                })

        messagebox.showinfo(
            "Export",
            "Tasks exported successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Export Error",
            str(error)
        )


# ============================================================
# CSV IMPORT
# ============================================================

def import_csv():

    filename = filedialog.askopenfilename(
        title="Import Tasks",
        filetypes=[
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        ]
    )

    if not filename:

        return

    try:

        with open(
            filename,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            rows = list(reader)

    except Exception as error:

        messagebox.showerror(
            "Import Error",
            str(error)
        )

        return

    if not rows:

        messagebox.showinfo(
            "Import",
            "The CSV file is empty."
        )

        return

    connection = get_connection()

    cursor = connection.cursor()

    imported = 0

    try:

        for row in rows:

            title = (
                row.get("title")
                or row.get("Title")
                or ""
            ).strip()

            if not title:

                continue

            description = (
                row.get("description")
                or ""
            )

            category = (
                row.get("category")
                or "General"
            )

            priority = (
                row.get("priority")
                or "Medium"
            )

            due_date = (
                row.get("due_date")
                or ""
            )

            try:

                completed = int(
                    str(
                        row.get(
                            "completed",
                            0
                        )
                    ).strip() or 0
                )

            except ValueError:

                completed = 0

            try:

                important = int(
                    str(
                        row.get(
                            "important",
                            0
                        )
                    ).strip() or 0
                )

            except ValueError:

                important = 0

            try:

                reminder_enabled = int(
                    str(
                        row.get(
                            "reminder_enabled",
                            0
                        )
                    ).strip() or 0
                )

            except ValueError:

                reminder_enabled = 0

            reminder_at = (
                row.get("reminder_at")
                or ""
            )

            try:

                reminder_sent = int(
                    str(
                        row.get(
                            "reminder_sent",
                            0
                        )
                    ).strip() or 0
                )

            except ValueError:

                reminder_sent = 0

            created_at = (
                row.get("created_at")
                or datetime.now().isoformat(
                    timespec="seconds"
                )
            )

            cursor.execute("""
                INSERT INTO tasks
                (
                    title,
                    description,
                    category,
                    priority,
                    due_date,
                    completed,
                    important,
                    created_at,
                    user_id,
                    reminder_enabled,
                    reminder_at,
                    reminder_sent
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                description,
                category,
                priority,
                due_date,
                completed,
                important,
                created_at,
                current_user_id,
                reminder_enabled,
                reminder_at,
                reminder_sent
            ))

            imported += 1

        connection.commit()

    except Exception as error:

        connection.rollback()

        connection.close()

        messagebox.showerror(
            "Import Error",
            str(error)
        )

        return

    connection.close()

    refresh_tasks()

    messagebox.showinfo(
        "Import",
        f"{imported} tasks imported successfully."
    )


# ============================================================
# APPEARANCE
# ============================================================

def open_appearance():

    dialog = tk.Toplevel(
        main_window
    )

    dialog.title(
        "Appearance"
    )

    dialog.geometry(
        "500x650"
    )

    dialog.minsize(
        460,
        600
    )

    dialog.configure(
        bg=theme["APP_BG"]
    )

    dialog.transient(
        main_window
    )

    dialog.grab_set()

    header = tk.Frame(
        dialog,
        bg=theme["APP_BG"]
    )

    header.pack(
        fill="x",
        padx=25,
        pady=(20, 5)
    )

    tk.Label(
        header,
        text="Appearance",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_TITLE
    ).pack(
        anchor="w"
    )

    tk.Label(
        header,
        text="Customize the look and feel of ToDO",
        bg=theme["APP_BG"],
        fg=theme["MUTED"],
        font=FONT_SMALL
    ).pack(
        anchor="w",
        pady=(2, 0)
    )

    tk.Label(
        dialog,
        text="Ready-made Themes",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_SECTION
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 8)
    )

    themes_frame = tk.Frame(
        dialog,
        bg=theme["APP_BG"]
    )

    themes_frame.pack(
        fill="x",
        padx=25
    )

    theme_names = list(
        THEMES.keys()
    )

    for index, theme_name in enumerate(
        theme_names
    ):

        row = index // 3

        column = index % 3

        preset = THEMES[
            theme_name
        ]

        button = tk.Button(
            themes_frame,
            text=theme_name,
            command=lambda name=theme_name:
                apply_preset_theme(
                    name,
                    dialog
                ),
            bg=preset["CARD_BG"],
            fg=preset["TEXT"],
            activebackground=preset["CARD_HOVER"],
            activeforeground=preset["TEXT"],
            relief="flat",
            bd=0,
            font=FONT_BUTTON,
            cursor="hand2",
            pady=8
        )

        button.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=4,
            pady=4
        )

    for column in range(3):

        themes_frame.grid_columnconfigure(
            column,
            weight=1
        )

    current_frame = tk.Frame(
        dialog,
        bg=theme["PANEL_BG"],
        highlightbackground=theme["BORDER"],
        highlightthickness=1
    )

    current_frame.pack(
        fill="x",
        padx=25,
        pady=15
    )

    tk.Label(
        current_frame,
        text=f"Current theme: {current_theme_name}",
        bg=theme["PANEL_BG"],
        fg=theme["TEXT"],
        font=FONT_MEDIUM
    ).pack(
        anchor="w",
        padx=15,
        pady=(12, 3)
    )

    tk.Label(
        current_frame,
        text="You can also customize the accent color.",
        bg=theme["PANEL_BG"],
        fg=theme["MUTED"],
        font=FONT_XS
    ).pack(
        anchor="w",
        padx=15,
        pady=(0, 10)
    )

    create_button(
        current_frame,
        "🎨  Choose Accent Color",
        lambda: choose_accent_color(dialog),
        bg=theme["ACCENT"]
    ).pack(
        fill="x",
        padx=15,
        pady=(0, 12)
    )

    tk.Label(
        dialog,
        text="Background",
        bg=theme["APP_BG"],
        fg=theme["TEXT"],
        font=FONT_SECTION
    ).pack(
        anchor="w",
        padx=25,
        pady=(2, 8)
    )

    background_status = (
        "Custom background selected"
        if theme.get(
            "BACKGROUND_IMAGE"
        )
        else
        "No custom background"
    )

    tk.Label(
        dialog,
        text=background_status,
        bg=theme["APP_BG"],
        fg=theme["MUTED"],
        font=FONT_XS
    ).pack(
        anchor="w",
        padx=25,
        pady=(0, 5)
    )

    create_button(
        dialog,
        "🖼  Choose Background Image",
        lambda: choose_background_image(dialog),
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=25,
        pady=4
    )

    create_button(
        dialog,
        "✕  Remove Background Image",
        lambda: remove_background_image(dialog),
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=25,
        pady=4
    )

    create_button(
        dialog,
        "↺  Reset Appearance",
        lambda: reset_theme(dialog),
        bg=theme["DANGER"]
    ).pack(
        fill="x",
        padx=25,
        pady=(15, 4)
    )

    create_button(
        dialog,
        "Close",
        dialog.destroy,
        bg=theme["CARD_BG"]
    ).pack(
        fill="x",
        padx=25,
        pady=4
    )


# ============================================================
# APPLY PRESET
# ============================================================

def apply_preset_theme(
    theme_name,
    dialog=None
):

    global theme
    global current_theme_name

    if theme_name not in THEMES:

        return

    old_background = theme.get(
        "BACKGROUND_IMAGE",
        ""
    )

    theme = THEMES[
        theme_name
    ].copy()

    theme["BACKGROUND_IMAGE"] = (
        old_background
    )

    current_theme_name = theme_name

    save_theme()

    if dialog is not None:

        try:

            dialog.destroy()

        except Exception:

            pass

    start_main_application()


# ============================================================
# ACCENT COLOR
# ============================================================

def choose_accent_color(
    dialog=None
):

    result = colorchooser.askcolor(
        color=theme["ACCENT"],
        title="Choose Accent Color"
    )

    if not result or not result[1]:

        return

    theme["ACCENT"] = result[1]

    theme["ACCENT_HOVER"] = (
        lighten_color(
            result[1],
            1.18
        )
    )

    save_theme()

    if dialog is not None:

        try:

            dialog.destroy()

        except Exception:

            pass

    start_main_application()


def lighten_color(
    hex_color,
    factor=1.15
):

    try:

        hex_color = (
            hex_color.lstrip("#")
        )

        if len(hex_color) != 6:

            return "#FFFFFF"

        r = int(
            hex_color[0:2],
            16
        )

        g = int(
            hex_color[2:4],
            16
        )

        b = int(
            hex_color[4:6],
            16
        )

        r = min(
            255,
            int(r * factor)
        )

        g = min(
            255,
            int(g * factor)
        )

        b = min(
            255,
            int(b * factor)
        )

        return (
            f"#{r:02X}{g:02X}{b:02X}"
        )

    except Exception:

        return "#FFFFFF"


# ============================================================
# RESET THEME
# ============================================================

def reset_theme(
    dialog=None
):

    global theme
    global current_theme_name

    answer = messagebox.askyesno(
        "Reset Appearance",
        "Reset all appearance settings?"
    )

    if not answer:

        return

    theme = DEFAULT_THEME.copy()

    current_theme_name = "Midnight"

    save_theme()

    if dialog is not None:

        try:

            dialog.destroy()

        except Exception:

            pass

    start_main_application()


# ============================================================
# BACKGROUND IMAGE
# ============================================================

def choose_background_image(
    dialog=None
):

    if not PIL_AVAILABLE:

        messagebox.showwarning(
            "Pillow Required",
            "Install Pillow first:\n\n"
            "pip install pillow"
        )

        return

    filename = filedialog.askopenfilename(
        title="Choose Background Image",
        filetypes=[
            (
                "Images",
                "*.png *.jpg *.jpeg *.webp *.bmp"
            ),
            (
                "All Files",
                "*.*"
            )
        ]
    )

    if not filename:

        return

    theme["BACKGROUND_IMAGE"] = filename

    save_theme()

    if dialog is not None:

        try:

            dialog.destroy()

        except Exception:

            pass

    start_main_application()


def remove_background_image(
    dialog=None
):

    theme["BACKGROUND_IMAGE"] = ""

    save_theme()

    if dialog is not None:

        try:

            dialog.destroy()

        except Exception:

            pass

    start_main_application()


def apply_background_image():

    global background_label
    global background_image

    if not theme.get(
        "BACKGROUND_IMAGE"
    ):

        return

    if not PIL_AVAILABLE:

        return

    filename = theme[
        "BACKGROUND_IMAGE"
    ]

    if not os.path.exists(filename):

        theme[
            "BACKGROUND_IMAGE"
        ] = ""

        save_theme()

        return

    try:

        image = Image.open(
            filename
        )

        width = max(
            main_window.winfo_width(),
            WINDOW_WIDTH
        )

        height = max(
            main_window.winfo_height(),
            WINDOW_HEIGHT
        )

        image = image.copy()

        image_ratio = (
            image.width / image.height
        )

        window_ratio = (
            width / height
        )

        if image_ratio > window_ratio:

            new_height = height

            new_width = int(
                height * image_ratio
            )

        else:

            new_width = width

            new_height = int(
                width / image_ratio
            )

        image = image.resize(
            (
                new_width,
                new_height
            ),
            Image.Resampling.LANCZOS
        )

        left = max(
            0,
            (new_width - width) // 2
        )

        top = max(
            0,
            (new_height - height) // 2
        )

        image = image.crop(
            (
                left,
                top,
                left + width,
                top + height
            )
        )

        if ImageEnhance is not None:

            try:

                image = ImageEnhance.Brightness(
                    image
                ).enhance(
                    0.55
                )

            except Exception:

                pass

        background_image = (
            ImageTk.PhotoImage(
                image
            )
        )

        background_label = tk.Label(
            main_window,
            image=background_image,
            bg=theme["APP_BG"],
            bd=0
        )

        background_label.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )

        background_label.lower()

        if main_container is not None:

            main_container.lift()

    except Exception as error:

        print(
            "Background image error:",
            error
        )


# ============================================================
# APPLICATION CLOSE
# ============================================================

def close_application():

    answer = messagebox.askyesno(
        "Exit",
        "Are you sure you want to exit?"
    )

    if answer:

        main_window.destroy()


main_window.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# STARTUP - DATABASE
# ============================================================

try:

    migrate_database()

except Exception as error:

    print(
        "Database startup error:"
    )

    print(
        traceback.format_exc()
    )

    messagebox.showerror(
        "ToDO",
        "Could not initialize the database.\n\n"
        f"{error}"
    )

    main_window.destroy()

    raise SystemExit


# ============================================================
# START APPLICATION
# ============================================================

show_login_screen()

main_window.mainloop()

