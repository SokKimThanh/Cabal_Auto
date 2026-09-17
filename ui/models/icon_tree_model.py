import os
import threading
import sqlite3
import time
from typing import Dict, List, Any, Callable, Tuple
from pathlib import Path

from database import MonsterDatabase
from lib.db.services.icon_service import IconService
from ui.helpers.icon_helper import get_icon_helper

class IconTreeModel:
    """
    Data model for the Icon Tree.
    Manages loading, caching, filtering, and usage dependency tracking
    without coupling to the UI.
    """
    def __init__(self):
        # Caches
        self.category_cache: Dict[int, Dict[str, Any]] = {}
        self.icon_cache: Dict[str, Dict[str, Any]] = {}
        self.usage_cache: Dict[str, List[Dict[str, Any]]] = {}  # key: icon_key, value: list of usage dicts
        self.status_cache: Dict[str, str] = {} # key: icon_key, value: GREEN/YELLOW/RED
        self.dependency_cache: Dict[str, int] = {} # key: icon_key, value: usage count

        # State tracking
        self.loaded = False
        self._load_lock = threading.Lock()

        # Filtering state
        self.current_filters = {
            "search": "",
            "category_id": None,
            "status": None
        }

    def _get_db_connection(self):
        """Creates a fresh, isolated database connection for the background thread."""
        return sqlite3.connect(str(MonsterDatabase.DB_PATH))

    def load_base_data_async(self, callback: Callable):
        """
        Loads categories and icons in a background thread.
        Does not load usages (lazy loaded).
        """
        def worker():
            with self._load_lock:
                conn = self._get_db_connection()
                icon_service = IconService(conn)
                icon_helper = get_icon_helper()

                try:
                    # 1. Load Categories
                    categories = icon_service.get_all_categories()
                    new_category_cache = {c['id']: c for c in categories}

                    # 2. Load Icons
                    # We fetch all without filters initially
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT i.*, c.name as category_name,
                               (SELECT COUNT(*) FROM icon_usages WHERE icon_key = i.icon_key) as usage_count
                        FROM icons i
                        LEFT JOIN icon_categories c ON i.category_id = c.id
                    ''')
                    rows = cursor.fetchall()

                    # Manual mapping since IconService might expect the cursor
                    icons = []
                    for r in rows:
                        d = dict(r)
                        self.dependency_cache[d['icon_key']] = d['usage_count']
                        icons.append(d)

                    new_icon_cache = {i['icon_key']: i for i in icons}

                    # 3. Calculate Statuses (O(1) with pre-scanned files)
                    existing_files = set()
                    if hasattr(icon_helper, 'icon_dirs'):
                        for d in icon_helper.icon_dirs:
                            if d.exists():
                                try:
                                    for f in d.iterdir():
                                        if f.is_file():
                                            existing_files.add(f.name)
                                except Exception:
                                    pass

                    new_status_cache = {}
                    for icon_key, icon_data in new_icon_cache.items():
                        new_status_cache[icon_key] = icon_helper.evaluate_icon_status(icon_data, existing_files_cache=existing_files)

                    # Update model state
                    self.category_cache = new_category_cache
                    self.icon_cache = new_icon_cache
                    self.status_cache = new_status_cache
                    self.loaded = True

                finally:
                    conn.close()

                # Notify UI
                if callback:
                    callback()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def load_usages_for_icon_async(self, icon_key: str, callback: Callable):
        """
        Lazy loads usages for a specific icon in the background.
        """
        def worker():
            with self._load_lock:
                if icon_key in self.usage_cache:
                    if callback:
                        callback(icon_key, self.usage_cache[icon_key])
                    return

                conn = self._get_db_connection()
                try:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM icon_usages WHERE icon_key = ?", (icon_key,))
                    rows = cursor.fetchall()
                    usages = [dict(r) for r in rows]

                    self.usage_cache[icon_key] = usages
                    self.dependency_cache[icon_key] = len(usages)
                finally:
                    conn.close()

                if callback:
                    callback(icon_key, usages)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def get_filtered_tree_data(self) -> Dict[int, List[Dict[str, Any]]]:
        """
        Returns purely in-memory filtered data, grouped by category_id.
        Returns: { category_id: [icon1, icon2, ...] }
        """
        search_term = self.current_filters["search"].lower()
        filter_cat_id = self.current_filters["category_id"]
        filter_status = self.current_filters["status"]

        grouped_data: Dict[int, List[Dict[str, Any]]] = {
            cat_id: [] for cat_id in self.category_cache.keys()
        }

        for icon_key, icon in self.icon_cache.items():
            cat_id = icon.get('category_id')

            # Apply Category Filter
            if filter_cat_id is not None and filter_cat_id != "" and str(cat_id) != str(filter_cat_id):
                continue

            # Apply Status Filter
            if filter_status:
                status = self.status_cache.get(icon_key, "⚪")
                if status != filter_status:
                    continue

            # Apply Search Filter
            if search_term:
                name = (icon.get('name') or '').lower()
                ik = (icon.get('icon_key') or '').lower()
                if search_term not in name and search_term not in ik:
                    continue

            if cat_id in grouped_data:
                grouped_data[cat_id].append(icon)
            else:
                # Fallback if category_id doesn't exist in cache (orphaned or default)
                if 1 not in grouped_data:
                    grouped_data[1] = []
                grouped_data[1].append(icon)

        # Clean up empty categories if filtering is active, unless it's the only one
        if search_term or filter_status or filter_cat_id:
             grouped_data = {k: v for k, v in grouped_data.items() if v}

        return grouped_data

    def set_filters(self, search: str = "", category_id: Any = None, status: str = None):
        """Updates internal filter state for the next render."""
        self.current_filters["search"] = search
        self.current_filters["category_id"] = category_id
        self.current_filters["status"] = status

    def get_icon(self, icon_key: str) -> Dict[str, Any]:
        return self.icon_cache.get(icon_key)

    def get_category(self, category_id: int) -> Dict[str, Any]:
        return self.category_cache.get(category_id)

    def invalidate_icon(self, icon_key: str):
        """Invalidate a specific icon and its dependencies."""
        if icon_key in self.icon_cache:
            del self.icon_cache[icon_key]
        if icon_key in self.status_cache:
            del self.status_cache[icon_key]
        if icon_key in self.usage_cache:
            del self.usage_cache[icon_key]
        if icon_key in self.dependency_cache:
            del self.dependency_cache[icon_key]

    def invalidate_category(self, category_id: int):
        """Invalidate category."""
        if category_id in self.category_cache:
            del self.category_cache[category_id]

    def update_icon_in_cache(self, icon_data: Dict[str, Any], status: str):
        """Update a specific icon in cache without full reload."""
        icon_key = icon_data.get('icon_key')
        if icon_key:
            self.icon_cache[icon_key] = icon_data
            self.status_cache[icon_key] = status

    def check_safe_delete(self, icon_key: str) -> Tuple[bool, List[Dict]]:
        """
        Check if an icon can be safely deleted.
        Returns (is_safe, list_of_usages).
        """
        usage_count = self.dependency_cache.get(icon_key, 0)
        usages = self.usage_cache.get(icon_key, [])
        # We might not have loaded usages yet, but we know the count. If count > 0, it's unsafe.
        # To show the warning, we mock usages list if it's empty to allow len(usages) check in UI
        if usage_count > 0 and not usages:
            usages = [{}] * usage_count
        return usage_count == 0, usages
