# ============================================================================
# CONSTANTS - Material You Color System (Light Theme)
# ============================================================================

CLR_PRIMARY           = "#6366f1"
CLR_PRIMARY_CONTAINER = "#4f46e5"
CLR_PRIMARY_FIXED     = "#e0e7ff"
CLR_ON_PRIMARY        = "#ffffff"

CLR_SECONDARY           = "#ec4899"
CLR_SECONDARY_CONTAINER = "#fce7f3"
CLR_ON_SECONDARY        = "#ffffff"

CLR_TERTIARY           = "#f59e0b"
CLR_TERTIARY_CONTAINER = "#fef3c7"

CLR_SURFACE                  = "#fcfcfd"
CLR_SURFACE_CONTAINER        = "#f3f4f6"
CLR_SURFACE_CONTAINER_HIGH   = "#e5e7eb"
CLR_SURFACE_CONTAINER_HIGHEST= "#d1d5db"

CLR_ON_SURFACE         = "#0f172a"
CLR_ON_SURFACE_VARIANT = "#475569"

CLR_OUTLINE         = "#94a3b8"
CLR_OUTLINE_VARIANT = "#e2e8f0"

CLR_ERROR            = "#ef4444"
CLR_ERROR_CONTAINER  = "#fee2e2"
CLR_SUCCESS          = "#10b981"
CLR_WARNING          = "#f59e0b"

CLR_SIDEBAR        = "#f8fafc"
CLR_SIDEBAR_ACTIVE = "#6366f1"

PRIORITY_COLORS = {
    "High":   CLR_ERROR,
    "Medium": CLR_PRIMARY,
    "Low":    CLR_SECONDARY,
}

QUADRANT_COLORS = {
    "Q1: Do First":   CLR_ERROR,
    "Q2: Schedule":   CLR_SUCCESS,
    "Q3: Delegate":   CLR_WARNING,
    "Q4: Eliminate":  CLR_OUTLINE,
}

CATEGORY_COLORS = {
    "Work":     CLR_PRIMARY,
    "Personal": CLR_SUCCESS,
    "Health":   CLR_TERTIARY,
    "Study":    "#8b5cf6",
    "Social":   CLR_SECONDARY,
    "Other":    CLR_OUTLINE,
}

QUOTES = [
    "The secret of getting ahead is getting started. — Mark Twain",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Focus on being productive instead of busy. — Tim Ferriss",
    "Small steps every day lead to big results.",
    "Plan your work and work your plan.",
    "Done is better than perfect. — Sheryl Sandberg",
]

DEFAULT_CATEGORIES = [
    {"id": 1, "name": "Work",     "color": CLR_PRIMARY},
    {"id": 2, "name": "Personal", "color": CLR_SUCCESS},
    {"id": 3, "name": "Health",   "color": CLR_TERTIARY},
    {"id": 4, "name": "Study",    "color": "#8b5cf6"},
    {"id": 5, "name": "Social",   "color": CLR_SECONDARY},
]

NAV_ITEMS = [
    ("📊", "Dashboard", 0),
    ("📅", "Calendar",  1),
    ("✨", "Add Item",  2),
    ("📝", "Notes",     3),
    ("🏆", "Analytics", 4),
    ("🔄", "Habits",    5),
]

USERS_FILENAME    = "scheduler_users.txt"
DATA_FOLDER       = "scheduler_data"
SETTINGS_FILENAME = "scheduler_settings.json"
DATA_SCHEMA_VER   = 3