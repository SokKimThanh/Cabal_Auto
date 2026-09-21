from ui.views.skill_config_view import SkillConfigView
from lib.features.hunt.window_selection_service import WindowSelectionService
from ui.controllers.app_lifecycle_controller import AppLifecycleController
from lib.ui_style_v2 import UIStyleV2 as UI  # Global UI style constants
from ui.controllers.hotkey_controller import HotkeyController




from lib.features.hunt.hunt_config import (
    ConfigManager,
    load_config,
    load_hunt_config,
    save_config,
    save_hunt_config,
        )
from ui.helpers.translation_binder import TranslationBinder
from lib.i18n import t as i18n_t
from lib.i18n import set_default_lang as i18n_set_lang
from lib.i18n import GLOBAL_NS as I18N_GLOBAL
from lib.features.hunt.config_validator import get_valid_hunt_area
from lib.system.task_scheduler import TaskScheduler
from lib.events.event_bus import EventBus, IconUpdatedEvent, HuntStatusUpdatedEvent, HuntStateChangedEvent, TargetHpUpdatedEvent, TargetStatusUpdatedEvent, TargetInfoUpdatedEvent, ClearTargetUIEvent, SkillStatsUpdatedEvent, LanguageChangedEvent, GlobalApplyEvent, StartStopHuntEvent, TranslationDataUpdatedEvent
import tkinter as tk
import sys
from lib.ui.dialog_service import DialogService
from pathlib import Path

# Add parent directory to path for lib imports


try:
    import pyautogui  # type: ignore
except ImportError:
    pyautogui = None  # type: ignore

try:
    from PIL import Image, ImageDraw, ImageTk  # type: ignore
except ImportError:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    ImageDraw = None  # type: ignore

# Imported for its side effect: self-registers GLOBAL_TRANSLATIONS into the i18n registry.

# Logger for debugging
import logging
from lib.logging_config import setup_logging

# Initialize logging system (size-based rotation: 5MB per file, keep 3 backups)
setup_logging(rotation_type='size')

logger = logging.getLogger(__name__)

# Import icon button component
try:
    from ui.components import create_icon_button as _create_icon_btn_component

    _HAS_ICON_COMPONENT = True
except ImportError:
    _HAS_ICON_COMPONENT = False

    from lib.ui.helpers.fallback_components import _create_icon_btn_component

    print("Warning: Icon button component not available, using fallback")


# =====================================================================
# Single Instance Lock (Prevent multiple app instances)

# =====================================================================




class App:


    def _t(self, key: str, **kwargs) -> str:
        kwargs.pop("ns", None)

        # Extract supported i18n_t args
        t_kwargs = {}
        if "lang" in kwargs:
            t_kwargs["lang"] = kwargs.pop("lang")
        if "default" in kwargs:
            t_kwargs["default"] = kwargs.pop("default")

        translated = i18n_t(key, ns=I18N_GLOBAL, **t_kwargs)

        # Apply formatting if there are extra kwargs left
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except Exception:
                pass

        return translated

    def bind_text(self, widget, key: str, **kwargs):
        """Binds a widget to a translation key and sets its initial text."""
        initial_text = self._t(key, **kwargs)
        if isinstance(widget, tk.Variable):
            widget.set(initial_text)
            self.translation_binder.bind_var(widget, key, **kwargs)
        else:
            try:
                if hasattr(widget, 'set_text'):
                    widget.set_text(initial_text)
                else:
                    widget.config(text=initial_text)
            except Exception:
                pass
            self.translation_binder.bind(widget, key, **kwargs)
        return widget

    def __init__(self, root, di_container=None):
        self.root = root
        self.has_unsaved_changes = False
        self._btn_scan_ref = None
        self._action_locked = False
        self.monster_selected_index = None
        self.translation_binder = TranslationBinder()

        try:
            self._create_services(di_container)
            self._create_controllers(di_container)
            self._initialize_application_state()
            self._build_ui()
            self._register_events()
        except Exception as e:
            print(f"[App.__init__] Error in early init: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _create_services(self, di_container):
        if di_container:
            self.monster_library_service = getattr(di_container, "monster_library_service", None)
            self.skill_service = getattr(di_container, "skill_service", None)
            self.db_skill_service = getattr(di_container, "db_skill_service", None)
            self.db_skill_type_service = getattr(di_container, "db_skill_type_service", None)
            self.db_class_service = getattr(di_container, "db_class_service", None)
            self.db_scan_service = getattr(di_container, "db_scan_service", None)
            self.skill_caster_service = getattr(di_container, "skill_caster_service", None)

        # Initialize IconSyncManager so it binds to EventBus and responds to IconManagerSyncEvent
        try:
            from lib.db.services.icon_sync_manager import IconSyncManager
            from lib.db.services.icon_service import IconService
            from database import get_db

            db = get_db()
            icon_service = IconService(db.conn)
            self.icon_sync_manager = IconSyncManager(icon_service)
            self.icon_sync_manager.sync_registry_to_db(db.conn)
        except Exception as e:
            print(f"Error initializing IconSyncManager: {e}")

        self.pil_available = (
            Image is not None and ImageTk is not None and ImageDraw is not None
        )

    def _create_controllers(self, di_container):
        if di_container:
            self.overlay_controller = getattr(di_container, "overlay_controller", None)
            self.scan_controller = getattr(di_container, "scan_controller", None)
            self.hunt_runner = getattr(di_container, "hunt_runner", None)
            self.hunt_orchestrator = getattr(di_container, "hunt_orchestrator", None)
        else:
            self.hunt_runner = None
            self.hunt_orchestrator = None
            self.scan_controller = None

        self.task_scheduler = TaskScheduler(self)

        from ui.controllers.app_state_controller import AppStateController
        self.state_controller = AppStateController(self.root)

        # Load config and language early for hotkey controller
        self.cfg = load_config()
        self.state_controller.hunt_cfg = load_hunt_config()

        self.hotkey_controller = HotkeyController(self, self.state_controller.hunt_cfg)

        from ui.controllers.app_window_controller import AppWindowController
        from ui.controllers.window_tracker_controller import WindowTrackerController
        self.window_controller = AppWindowController(self)
        self.window_tracker_controller = WindowTrackerController(self)

        self.overlay_ctrl = None
        self.hunt_controller = None

        from lib.ui.controllers.monster_rotation_controller import MonsterRotationController
        if hasattr(self, 'di_container') and self.di_container and hasattr(self.di_container, "monster_rotation_controller") and self.di_container.monster_rotation_controller:
            self.monster_rotation_controller = self.di_container.monster_rotation_controller
        else:
            self.monster_rotation_controller = MonsterRotationController(self.state_controller)

        from lib.ui.controllers.menu_vision_controller import MenuVisionController
        self.menu_vision_controller = MenuVisionController(app=self, window_controller=self.window_controller)

        self.skill_config_view = SkillConfigView(self.state_controller)

    def _initialize_application_state(self):
        self._is_destroyed = False
        DialogService.set_default_parent(self.root)
        self._last_height_under_900 = False

        from lib.db.services.translation_service import TranslationService
        from lib.db.services.translation_sync_manager import TranslationSyncManager

        db_record_count = TranslationService().get_total_count()
        if db_record_count == 0:
            TranslationSyncManager.seed_initial_data()

        import lib.i18n
        lib.i18n.load_from_db()

        self.lang = str(self.cfg.get("ui", {}).get("language", "vi"))
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass

        try:
            from ui.helpers.icon_helper import get_icon_helper
            from ui.icon_library import register_icons

            self.icon_helper = get_icon_helper()
            register_icons(self.icon_helper)
        except Exception:
            self.icon_helper = None

        self.root.config_mgr = ConfigManager(self.cfg, self.state_controller.hunt_cfg)

        self.state_controller._collect_skill_slots_func = getattr(self.skill_config_view, '_collect_skill_slots', None)
        self.state_controller.ui_widgets['unsaved_indicator_func'] = getattr(self, '_update_unsaved_indicator', None)

        self._detected_snapshot_items = []
        self._last_snapshot = None
        self.state_controller.hunt_selected = {}

        if hasattr(self, "monster_library_service") and self.monster_library_service:
            self.monsters = self.monster_library_service.load_monsters()
        else:
            self.monsters = []

        if hasattr(self, "skill_service") and self.skill_service:
            self.monsters = self.skill_service._normalize_library_items(self.monsters)

        self.monster_selected_name = self.monsters[0].get("name", "Unknown") if self.monsters else None

        self.state_controller.monster_rotation = []
        if hasattr(self, 'monster_rotation_controller') and self.monster_rotation_controller:
            self.monster_rotation_controller.load_monster_rotation_list()

        skills = self.skill_service.get_all_skills() if hasattr(self, "skill_service") and self.skill_service else []
        self.skill_selected_name = skills[0].get("name", "Unknown") if skills else None
        self.skill_slot_saved_names = [
            slot.get("name", "")
            for slot in self.skill_panel_controller.get_combo_sequence()
            if isinstance(slot, dict) and slot.get("name")
        ]
        self.monster_template_working = []
        self.monster_template_selected_index = None
        self.state_controller.ui_widgets['monster_template_listbox'] = None
        self.state_controller.monster_template_region_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }
        self.state_controller.ui_widgets['monster_template_preview_label'] = None
        self.state_controller.ui_widgets['monster_template_preview_image'] = None
        self._monster_template_path_trace = None
        self._thumbnail_cache = {}
        self.state_controller.monster_bounds_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }

        safe_area = get_valid_hunt_area(self.state_controller.hunt_cfg)
        self.state_controller.hunt_cfg["hunt_area"] = safe_area
        self.state_controller.current_window_bounds = safe_area.get("window_bounds")
        WindowSelectionService.update_bounds(self.state_controller.hunt_cfg, self.state_controller.current_window_bounds)

        if pyautogui is not None:
            pyautogui.FAILSAFE = bool(self.cfg.get("safety", {}).get("failsafe", True))

        self.state_controller.win_items = []
        self.win_items_map = {}

    def _register_events(self):
        self._register_bus_events()
        self._register_ui_events()
        self._register_lifecycle_events()

    def _register_bus_events(self):
        EventBus.bind(IconUpdatedEvent, self.on_icon_updated)
        EventBus.bind(HuntStatusUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self.state_controller.set_ui_var('hunt_status', e.status)))
        EventBus.bind(HuntStateChangedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self._on_orchestrator_state_change(e.state)))
        EventBus.bind(TargetHpUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self.tab_hunt.update_hp_display(e.hp_percent) if hasattr(self, 'tab_hunt') and hasattr(self.tab_hunt, 'update_hp_display') else None))
        EventBus.bind(TargetStatusUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self.tab_hunt.update_status(e.status) if hasattr(self, 'tab_hunt') and hasattr(self.tab_hunt, 'update_status') else None))
        EventBus.bind(TargetInfoUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self.state_controller.set_ui_var('hunt_target_info', e.info)))
        EventBus.bind(ClearTargetUIEvent, lambda e: self.task_scheduler.schedule_task(None, 0, self.clear_target_ui))
        EventBus.bind(SkillStatsUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: getattr(self, 'update_skill_stats_display', lambda _: None)(e.stats)))
        EventBus.bind(LanguageChangedEvent, self.on_language_change)
        EventBus.bind(TranslationDataUpdatedEvent, self.on_translation_updated)

        from lib.ui.controllers.global_config_controller import GlobalConfigController
        self.global_config_controller = GlobalConfigController(self.state_controller, self.hotkey_controller, self._t, app_instance=self)
        EventBus.bind(GlobalApplyEvent, lambda e: self.global_config_controller.apply_all_configs())

        self.monster_rotation_controller.bind_events()
        EventBus.bind(StartStopHuntEvent, lambda e: self.hunt_controller.on_start_stop_clicked())

    def _register_ui_events(self):
        self.root.bind("<Control-b>", lambda e: self.navigation.navigate_to("build_manager"))
        self.root.bind("<Control-m>", lambda e: self.navigation.navigate_to("monster_manager"))
        self.root.bind("<Control-k>", lambda e: self.navigation.navigate_to("skill_manager"))
        self.root.bind("<Control-l>", lambda e: self.navigation.navigate_to("language_manager"))
        self.root.bind("<Alt-Key-1>", lambda e: self.navigation.navigate_to("hunt"))
        self.root.bind("<Alt-Key-2>", lambda e: self.navigation.navigate_to("setup"))
        self.root.bind("<Configure>", self._on_window_configure)

    def _register_lifecycle_events(self):
        from ui.theme.ttk_theme import configure_ttk_styles
        configure_ttk_styles(self.root)
        self.hotkey_controller.register_all()
        self.lifecycle_controller = AppLifecycleController(self)
        self.lifecycle_controller.start_lifecycle()
        if hasattr(self, 'di_container') and self.di_container:
            self.monster_library_service = getattr(self.di_container, "monster_library_service", None)
            self.skill_service = getattr(self.di_container, "skill_service", None)
            self.db_skill_service = getattr(self.di_container, "db_skill_service", None)
            self.db_skill_type_service = getattr(self.di_container, "db_skill_type_service", None)
            self.db_class_service = getattr(self.di_container, "db_class_service", None)
            self.db_scan_service = getattr(self.di_container, "db_scan_service", None)
            self.overlay_controller = getattr(self.di_container, "overlay_controller", None)
            self.skill_caster_service = getattr(self.di_container, "skill_caster_service", None)
            self.scan_controller = getattr(self.di_container, "scan_controller", None)

        self.has_unsaved_changes = False
        self._btn_scan_ref = None
        self._action_locked = False

        self.monster_selected_index = None
        self.translation_binder = TranslationBinder()

        try:
            self._is_destroyed = False
            DialogService.set_default_parent(self.root)
            self._last_height_under_900 = False

            # Initialize State Controller early
            from ui.controllers.app_state_controller import AppStateController
            self.state_controller = AppStateController(self.root)

            # Startup Protection: Ensure translations exist in DB before loading UI
            from lib.db.services.translation_service import TranslationService
            from lib.db.services.translation_sync_manager import TranslationSyncManager

            db_record_count = TranslationService().get_total_count()
            if db_record_count == 0:
                TranslationSyncManager.seed_initial_data()

            # Load from DB to memory
            import lib.i18n
            lib.i18n.load_from_db()

            # Load config and language
            self.cfg = load_config()
            self.state_controller.hunt_cfg = load_hunt_config()
            self.lang = str(self.cfg.get("ui", {}).get("language", "vi"))
            try:
                i18n_set_lang(self.lang)
            except Exception:
                pass
            try:
                i18n_set_lang(self.lang)
            except Exception:
                pass

            self.hotkey_controller = HotkeyController(self, self.state_controller.hunt_cfg)
            # Centralized icon helper
            try:
                from ui.helpers.icon_helper import get_icon_helper
                from ui.icon_library import register_icons

                self.icon_helper = get_icon_helper()
                register_icons(self.icon_helper)
            except Exception:
                self.icon_helper = None

            EventBus.bind(IconUpdatedEvent, self.on_icon_updated)

            # Create config manager for wizard
            self.root.config_mgr = ConfigManager(self.cfg, self.state_controller.hunt_cfg)

            from ui.components.app_shell import AppShell
            self.shell = AppShell(root=self.root, app=self)
            self.shell.build()
        except Exception as e:
            print(f"[App.__init__] Error in early init: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Initialize ScanController




        # State Bookkeeping Extracted
        from ui.controllers.app_window_controller import AppWindowController
        from ui.controllers.window_tracker_controller import WindowTrackerController



        self.skill_config_view = SkillConfigView(self.state_controller)
        self.state_controller._collect_skill_slots_func = getattr(self.skill_config_view, '_collect_skill_slots', None)
        self.state_controller.ui_widgets['unsaved_indicator_func'] = getattr(self, '_update_unsaved_indicator', None)
        self.window_controller = AppWindowController(self)
        self.window_tracker_controller = WindowTrackerController(self)
        self.overlay_ctrl = None
        self.hunt_controller = None
        self._detected_snapshot_items = []
        self._last_snapshot = None
        self.task_scheduler = TaskScheduler(self)

        # --- Event Bus Bindings ---
        EventBus.bind(HuntStatusUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self.state_controller.set_ui_var('hunt_status', e.status)))
        EventBus.bind(HuntStateChangedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self._on_orchestrator_state_change(e.state)))
        EventBus.bind(TargetHpUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self.tab_hunt.update_hp_display(e.hp_percent) if hasattr(self, 'tab_hunt') and hasattr(self.tab_hunt, 'update_hp_display') else None))
        EventBus.bind(TargetStatusUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self.tab_hunt.update_status(e.status) if hasattr(self, 'tab_hunt') and hasattr(self.tab_hunt, 'update_status') else None))
        EventBus.bind(TargetInfoUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: self.state_controller.set_ui_var('hunt_target_info', e.info)))
        EventBus.bind(ClearTargetUIEvent, lambda e: self.task_scheduler.schedule_task(None, 0, self.clear_target_ui))
        EventBus.bind(SkillStatsUpdatedEvent, lambda e: self.task_scheduler.schedule_task(None, 0, lambda: getattr(self, 'update_skill_stats_display', lambda _: None)(e.stats)))
        EventBus.bind(LanguageChangedEvent, self.on_language_change)
        EventBus.bind(TranslationDataUpdatedEvent, self.on_translation_updated)

        from lib.ui.controllers.global_config_controller import GlobalConfigController
        self.global_config_controller = GlobalConfigController(self.state_controller, self.hotkey_controller, self._t, app_instance=self)
        EventBus.bind(GlobalApplyEvent, lambda e: self.global_config_controller.apply_all_configs())

        from lib.ui.controllers.monster_rotation_controller import MonsterRotationController
        if hasattr(self, 'di_container') and self.di_container and hasattr(self.di_container, "monster_rotation_controller") and self.di_container.monster_rotation_controller:
            self.monster_rotation_controller = self.di_container.monster_rotation_controller
        else:
            self.monster_rotation_controller = MonsterRotationController(self.state_controller)
        self.monster_rotation_controller.bind_events()
        EventBus.bind(StartStopHuntEvent, lambda e: self.hunt_controller.on_start_stop_clicked())

        # Instantiate the MenuVisionController to handle vision menu events
        from lib.ui.controllers.menu_vision_controller import MenuVisionController
        self.menu_vision_controller = MenuVisionController(app=self, window_controller=self.window_controller)

        self.state_controller.hunt_selected = {}

        # Check PIL availability (for image preview features)
        self.pil_available = (
            Image is not None and ImageTk is not None and ImageDraw is not None
        )

        if hasattr(self, "monster_library_service") and self.monster_library_service:
            self.monsters = self.monster_library_service.load_monsters()
        else:
            self.monsters = []

        if hasattr(self, "skill_service") and self.skill_service:
            self.monsters = self.skill_service._normalize_library_items(self.monsters)

        self.monster_selected_name = self.monsters[0].get("name", "Unknown") if self.monsters else None

        # Phase 3: Multi-Monster Support
        self.state_controller.monster_rotation = []
        if hasattr(self, 'monster_rotation_controller') and self.monster_rotation_controller:
            self.monster_rotation_controller.load_monster_rotation_list()

        skills = self.skill_service.get_all_skills() if hasattr(self, "skill_service") and self.skill_service else []
        self.skill_selected_name = skills[0].get("name", "Unknown") if skills else None
        self.skill_slot_saved_names = [
            slot.get("name", "")
            for slot in self.skill_panel_controller.get_combo_sequence()
            if isinstance(slot, dict) and slot.get("name")
        ]
        self.monster_template_working = []
        self.monster_template_selected_index = None
        self.state_controller.ui_widgets['monster_template_listbox'] = None
        self.state_controller.monster_template_region_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }
        self.state_controller.ui_widgets['monster_template_preview_label'] = None
        self.state_controller.ui_widgets['monster_template_preview_image'] = None
        self._monster_template_path_trace = None
        self._thumbnail_cache = {}  # path -> PhotoImage cache
        self.state_controller.monster_bounds_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }

        # Configuration is already migrated during load_hunt_config

        safe_area = get_valid_hunt_area(self.state_controller.hunt_cfg)
        self.state_controller.hunt_cfg["hunt_area"] = safe_area
        self.state_controller.current_window_bounds = safe_area.get("window_bounds")
        WindowSelectionService.update_bounds(self.state_controller.hunt_cfg, self.state_controller.current_window_bounds)

        if pyautogui is not None:
            pyautogui.FAILSAFE = bool(self.cfg.get("safety", {}).get("failsafe", True))

        # Initialize window selection state
        self.state_controller.win_items = []
        self.win_items_map = {}

        self._build_ui()
        self.hunt_runner = self.di_container.hunt_runner if hasattr(self, 'di_container') and self.di_container else None

        self.hunt_orchestrator = self.di_container.hunt_orchestrator if hasattr(self, 'di_container') and self.di_container else None

        # Keyboard shortcuts (Window-focused only)
        self.root.bind("<Control-b>", lambda e: self.navigation.navigate_to("build_manager"))
        self.root.bind("<Control-m>", lambda e: self.navigation.navigate_to("monster_manager"))
        self.root.bind("<Control-k>", lambda e: self.navigation.navigate_to("skill_manager"))
        self.root.bind("<Control-l>", lambda e: self.navigation.navigate_to("language_manager"))

        self.root.bind("<Alt-Key-1>", lambda e: self.navigation.navigate_to("hunt"))  # Alt+1: Hunt tab
        self.root.bind(
            "<Alt-Key-2>", lambda e: self.navigation.navigate_to("setup")
        )  # Alt+2: Setup tab

        # Responsive layout bindings
        self.root.bind("<Configure>", self._on_window_configure)

        from ui.theme.ttk_theme import configure_ttk_styles

        configure_ttk_styles(self.root)

        self.hotkey_controller.register_all()
        self.lifecycle_controller = AppLifecycleController(self)
        self.lifecycle_controller.start_lifecycle()

        # Register for skill key updates

    # -----------------


    def _build_ui(self):
        self._build_shell_layout()
        self._build_main_menu()
        self._build_navigation_and_views()
        self._build_action_bar()
        self._build_status_bar()

    def _build_shell_layout(self):
        from ui.components.app_shell import AppShell
        self.shell = AppShell(root=self.root, app=self)
        self.shell.build()

        self.main_shell = self.shell.main_shell
        self.shell_zone_a = self.shell.shell_zone_a
        self.action_bar_visible = True
        self.shell_zone_b = self.shell.shell_zone_b
        self.shell_zone_c1 = self.shell.shell_zone_c1
        self.status_bar_frame = self.shell.status_bar_frame

    def _build_main_menu(self):
        try:
            from lib.ui.components.main_menu_bar import MainMenuBar
            self.main_menu = MainMenuBar(
                parent=self.root,
                app=self,
                state_controller=self.state_controller,
                hotkey_controller=self.hotkey_controller,
                window_controller=self.window_controller,
                overlay_controller=self.overlay_controller
            )
            try:
                self.root.config(menu=self.main_menu)
            except Exception:
                pass
        except Exception as e:
            print(f"[Menu] Error creating menubar: {e}")

    def _build_navigation_and_views(self):
        from ui.controllers.navigation_controller import NavigationController
        self.navigation = NavigationController(self.shell_zone_b, on_view_changed=self._update_sidebar_state)
        self.navigation.register_views(self)

        self.logs_text_widget = (
            self.navigation.views.get("logs").text_widget
            if "logs" in self.navigation.views and hasattr(self.navigation.views["logs"], "text_widget")
            else None
        )

        self.tab_hunt = (
            self.navigation.views["hunt"].hunt_tab
            if "hunt" in getattr(self.navigation, "views", {}) and hasattr(self.navigation.views["hunt"], "hunt_tab")
            else None
        )
        self.tab_setup = (
            self.navigation.views["setup"].setup_tab
            if "setup" in getattr(self.navigation, "views", {}) and hasattr(self.navigation.views["setup"], "setup_tab")
            else None
        )
        self.tab_stats = (
            self.navigation.views["stats"].stats_tab
            if "stats" in getattr(self.navigation, "views", {}) and hasattr(self.navigation.views["stats"], "stats_tab")
            else None
        )
        self.tab_help = (
            self.navigation.views["help"].help_tab
            if "help" in getattr(self.navigation, "views", {}) and hasattr(self.navigation.views["help"], "help_tab")
            else None
        )
        self.notebook = None

        from ui.components.sidebar_component import SidebarComponent
        self.sidebar = SidebarComponent(
            parent=self.shell_zone_c1.get_content_frame(),
            app=self,
            on_navigate_callback=self.navigation.navigate_to
        )
        self.sidebar.pack(fill="both", expand=True)
        self.navigation.navigate_to("hunt")

    def _build_action_bar(self):
        from ui.components.action_bar_view import ActionBarView
        self.action_bar = ActionBarView(self.shell_zone_a, state_controller=self.state_controller, window_controller=self.window_controller, scan_controller=self.scan_controller)
        self.action_bar.pack(fill="x", expand=False)

        self.btn_manual_scan = self.action_bar.btn_manual_scan
        self.compact_window_selector = self.action_bar.compact_window_selector
        self.screen_state_panel = self.action_bar.screen_state_panel
        self.global_apply_btn = self.action_bar.global_apply_btn
        self.start_stop_btn = self.action_bar.start_stop_btn
        self.window_status_lbl = self.action_bar.window_status_lbl
        self.lang_cmb = self.action_bar.lang_cmb
        
        self.has_unsaved_changes = False
        self._update_unsaved_indicator()

    def _build_status_bar(self):
        from ui.components.status_bar_view import StatusBarView
        self.status_bar = StatusBarView(self.status_bar_frame, state_controller=self.state_controller)
        self.status_bar.pack(fill="both", expand=True)
        self._db_status_bar = self.status_bar.db_status_label
    def _on_window_configure(self, event):
        pass

    def _check_initial_logs_state(self):
        """Check window height and auto-collapse logs if needed (UX4B.1)."""
        self.root.update_idletasks()
        current_height = self.root.winfo_height()
        if current_height < 900:
            self._last_height_under_900 = True
            if getattr(self, "logs_expanded", False):
                self._toggle_bottom_logs()
        else:
            self._last_height_under_900 = False

    def _toggle_action_bar(self, force_state=None):
        """Toggles the visibility of the top action bar."""
        if not hasattr(self, 'action_bar_visible'):
            self.action_bar_visible = True

        if force_state is not None:
            self.action_bar_visible = force_state
        else:
            self.action_bar_visible = not self.action_bar_visible

        if self.action_bar_visible:
            self.shell_zone_a.grid()
        else:
            self.shell_zone_a.grid_remove()

    def _update_sidebar_state(self, view_key: str):
        # Update sidebar selected state
        if hasattr(self, "sidebar"):
            self.sidebar.set_active_tab(view_key)

    # Click Tab removed

    # Hunt Tab (Refactored - Sprint 18 Phase 4 Task #2 + UX Enhancement)


    def _set_db_status(self, msg: str, ok: bool = True):
        """Called by AppLifecycleController to display DB health status."""
        if self.state_controller.get_ui_var('hunt_status') is not None:
            self.task_scheduler.schedule_task(None, 0, lambda: self.state_controller.set_ui_var('hunt_status', msg))

    def _update_scan_status_text(self, text):
        if self.state_controller.get_ui_var('hunt_status') is not None:
            self.task_scheduler.schedule_task(None, 0, lambda: self.state_controller.set_ui_var('hunt_status', text))

    def _update_scan_status_icon(self, icon_name):
        if hasattr(self, "btn_manual_scan") and self.btn_manual_scan:
            try:
                from ui.helpers.icon_helper import get_icon_helper

                helper = get_icon_helper()
                img = helper.get_icon(icon_name, fallback="🔍", size=22)

                def update():
                    if isinstance(img, str):
                        self.btn_manual_scan.config(text=img, image="")
                    else:
                        self.btn_manual_scan.config(image=img, text="")
                        self._btn_scan_ref = (
                            img  # Store a single reference to avoid memory leak
                        )

                self.task_scheduler.schedule_task(None, 0, update)
            except Exception as e:
                print(f"[UI] Error updating scan status icon: {e}")

    def _show_scan_results(self, results):
        if hasattr(self, "screen_state_panel"):
            # Fetch state from ScreenStateAnalyzer
            from lib.features.setup.screen_state_analyzer import ScreenStateAnalyzer

            analyzer = ScreenStateAnalyzer()
            # For a manual scan triggered via UI, we typically use the selected window hwnd
            hwnd = None
            if hasattr(self, "app_window_controller"):
                hwnd = self.app_window_controller.get_current_hwnd()
            if not hwnd:
                hwnd = 0  # Default fallback

            # Analyze screen state
            state = analyzer.scan_screen_state(hwnd)

            # Optionally update state with scanner results if needed
            if "class" in results and results["class"] != "Unknown":
                state["character_class"] = results["class"]

                scanned_class_name = results["class"]
                scanned_class_id = None

                from lib.db.services.class_service import ClassService
                try:
                    classes = ClassService().get_all_classes()
                    for c in classes:
                        if scanned_class_name.lower() in c.get("name", "Unknown").lower() or c.get("name", "Unknown").lower() in scanned_class_name.lower():
                            scanned_class_id = c["id"]
                            break
                except Exception:
                    pass

                if scanned_class_id is not None:
                    current_class_id = getattr(self.state_controller.root, "_current_class_id", 1)
                    if scanned_class_id != current_class_id:
                        msg = self._t("msg_class_scan_mismatch") if hasattr(self, "_t") else "Scanned class differs from selected class. Update?"
                        if DialogService.ask_yes_no("Warning", msg, parent=self):
                            if hasattr(self.state_controller, "set_current_class"):
                                self.skill_panel.controller.preset_controller.set_current_class(scanned_class_id)

            self.screen_state_panel.update_from_scan(state)

            if "thumbnail" in results:
                self.screen_state_panel.update_thumbnail(results["thumbnail"])



    def on_language_change(self, _evt=None):
        # Save selection based on hwnd to prevent loss on language change
        saved_hwnd = None
        if self.state_controller.hunt_selected and isinstance(
            self.state_controller.hunt_selected, dict
        ):
            saved_hwnd = self.state_controller.hunt_selected.get("hwnd")

        self.lang = self.state_controller.get_ui_var('lang')
        self.cfg.setdefault("ui", {})
        self.cfg["ui"]["language"] = self.lang
        save_config(self.cfg)
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass

        # Trigger live update of all bound UI text tokens
        if hasattr(self, "translation_binder"):
            self.translation_binder.refresh_all(self._t)

        self.shell.update_title()
        self.refresh_translations()

        # Re-apply window selection robustly by hwnd
        if saved_hwnd and hasattr(self, "compact_window_selector"):
            # Refresh windows and set search text to the saved window title
            if isinstance(self.state_controller.hunt_selected, dict):
                saved_title = self.state_controller.hunt_selected.get("title", "")
                self.compact_window_selector.set_search_text(saved_title)

    def on_icon_updated(self, event: IconUpdatedEvent):
        if self.icon_helper is None:
            return

        # We need to query icon_usages from IconService
        from lib.db.services.icon_service import IconService
        from database import get_db
        db = get_db()
        icon_service = IconService(db.conn)

        usages = icon_service.get_usages(event.icon_key)

        # Get new image
        icon_data = icon_service.get_icon_by_key(event.icon_key)
        if not icon_data:
            return

        fallback = icon_data.get("fallback_emoji", "")
        # 1. Reload the in-memory map from JSON so new paths are recognized
        if hasattr(self.icon_helper, "reload_icon_map"):
            self.icon_helper.reload_icon_map()

        # 1.1 Reload tooltip keys from database
        all_tooltips = icon_service.get_all_tooltip_keys()
        self.icon_helper.update_tooltip_keys(all_tooltips)

        # 1.2 Force refresh all global tooltips via TranslationBinder
        if hasattr(self, 'translation_binder') and hasattr(self.translation_binder, 'refresh_all_tooltips'):
            self.translation_binder.refresh_all_tooltips()

        # 2. Clear cache for this icon key so Tkinter PhotoImages are regenerated
        if hasattr(self.icon_helper, "clear_cache"):
            self.icon_helper.clear_cache(event.icon_key)
        elif hasattr(self.icon_helper, "_cache"):
            keys_to_remove = [k for k in self.icon_helper._cache.keys() if k.startswith(f"{event.icon_key}_")]
            for k in keys_to_remove:
                del self.icon_helper._cache[k]

        # 3. Handle specific consumers from icon_usages
        requires_sidebar_refresh = False

        for usage in usages:
            component_type = usage.get("ui_component_type")
            if component_type == "sidebar_button":
                requires_sidebar_refresh = True

        # Trigger natural refresh mechanisms for components that need it
        if requires_sidebar_refresh and hasattr(self, "sidebar") and hasattr(self, "navigation"):
            # Update all icons in the sidebar
            if hasattr(self.sidebar, "update_sidebar_icons"):
                self.sidebar.update_sidebar_icons()

            # Simply re-setting the active tab forces the Sidebar to naturally redraw
            # all its icons utilizing the freshly reloaded icon_helper cache
            current_view = getattr(self.navigation, "current_view_key", None)
            if current_view:
                self.sidebar.set_active_tab(current_view)

    def on_translation_updated(self, event=None):
        """Handle TranslationDataUpdatedEvent from EventBus to refresh UI."""
        # Load from DB to update in-memory dicts
        import lib.i18n
        lib.i18n.load_from_db()
        # Trigger TranslationBinder refresh on main thread
        if hasattr(self, "translation_binder"):
            self.root.after(0, lambda: self.translation_binder.refresh_all(self._t))

    def refresh_translations(self):
        # Dynamically update text on widgets without rebuilding
        # _create_icon_btn_component returns a wrapper with set_text/set_tooltip if it's our custom component
        # But if it returns standard button, we config directly.

        if hasattr(self, "translation_binder"):
            self.translation_binder.refresh_all(self._t)

        if hasattr(self, 'hunt_controller') and self.hunt_controller:
            self.hunt_controller.refresh_start_stop_visual()
        self._update_unsaved_indicator()

        if hasattr(self, "window_status_lbl"):
            self.window_status_lbl.config(text=self._t("window_status_label"))

        # Note: Refresh button is now part of CompactWindowSelector, no separate update needed

        # Update bounds readiness label explicitly via state controller
        if hasattr(self, "state_controller") and hasattr(
            self.state_controller, "_update_window_bounds_display"
        ):
            self.window_controller.update_window_bounds_display()

        # Optionally update tabs here, though the prompt primarily requests
        # Zone A widgets to change immediately without losing state.
        # Now handled by views instead of notebook
        if hasattr(self, "update_shell_translations"):
            self.update_shell_translations()

    def update_shell_translations(self):
        """Update i18n text for shell elements like sidebar."""
        if hasattr(self, "sidebar"):
            self.sidebar.update_translations()


    def _switch_to_tab(self, tab_index: int):
        """Switch to specified tab via keyboard shortcut."""
        try:
            tab_map = {0: "hunt", 1: "setup", 2: "stats", 3: "help"}
            if tab_index in tab_map and hasattr(self, "navigation") and self.navigation:
                self.navigation.navigate_to(tab_map[tab_index])
                # Update status with shortcut indicator
                tab_names = ["Hunt", "Setup", "Stats", "Help"]
                if 0 <= tab_index < len(tab_names):
                    tab_name = tab_names[tab_index]
                    shortcut = f"Alt+{tab_index + 1}"
                    if self.state_controller.get_ui_var('hunt_status') is not None:
                        self.state_controller.set_ui_var('hunt_status', f"{shortcut}: Switched to {tab_name} tab")
        except Exception as e:
            print(f"Tab switch error: {e}")

    def _update_hotkeys_state(self):
        """Update hotkey state.
        Called when Global hotkeys are re-registered.
        """
        if hasattr(self.state_controller, "hunt_cfg"):
            self.hotkey_controller.register_all()

    # --- Helpers to attempt closing other windows while respecting unsaved changes ---


        is_running = self.state_controller.is_bot_running()
        if is_running:
            text = self._t("stop_hunt")
            tooltip = self._t("stop_hunt") + "\n(Ctrl+F6)"
            bg_color = UI.DANGER
        else:
            text = self._t("start_hunt")
            tooltip = self._t("start_hunt") + "\n(Ctrl+F5)"
            bg_color = UI.ACCENT_GREEN

        if hasattr(self.start_stop_btn, "set_text"):
            self.start_stop_btn.set_text(text)
            self.start_stop_btn.set_tooltip(tooltip)
            # Custom component coloring would rely on button_type typically,
            # but we can fallback to config if needed. We assume custom wrapper might support bg configure.
            try:
                self.start_stop_btn.config(bg=bg_color)
            except Exception:
                pass
        else:
            self.start_stop_btn.config(text=text, bg=bg_color)



        self._action_locked = True

        # Debounce: Disable button while state transition resolves
        if hasattr(self.start_stop_btn, "configure"):
            self.start_stop_btn.configure(state="disabled")
        elif hasattr(self.start_stop_btn, "config"):
            self.start_stop_btn.config(state="disabled")



        self.task_scheduler.schedule_task("reenable_start_stop_btn", 500, self.hunt_controller.reenable_start_stop_btn if hasattr(self, 'hunt_controller') else None, recurring=False)



    def _on_orchestrator_state_change(self, state: str):
        if state == "running":
            self.state_controller.set_ui_var('is_hunting', True)
            if self.state_controller.get_ui_var('hunt_status') is not None:
                self.state_controller.set_ui_var('hunt_status', self._t("hunt_running"))
            if hasattr(self, "tab_hunt") and hasattr(
                self.tab_hunt, "update_hunt_status_color"
            ):
                self.tab_hunt.update_hunt_status_color("running")
        elif state in ["idle", "error", "stopped"]:
            self.state_controller.set_ui_var('is_hunting', False)
            if state == "idle" and self.state_controller.get_ui_var('hunt_status') is not None:
                self.state_controller.set_ui_var('hunt_status',
                    self._t("hunt_idle") if hasattr(self, "_t") else "Idle"
                )
            if hasattr(self, "tab_hunt") and hasattr(
                self.tab_hunt, "update_hunt_status_color"
            ):
                self.tab_hunt.update_hunt_status_color(state)

        if hasattr(self.state_controller, "_emit_event"):
            self.state_controller._emit_event("on_bot_state_changed", state)

        if hasattr(self, 'hunt_controller') and self.hunt_controller:
            self.hunt_controller.refresh_start_stop_visual()


    # -----------------
    # Close
    # -----------------

    def _on_rotation_mode_changed(self, event=None):
        """Handle rotation mode change."""
        display_mode = self.state_controller.get_ui_var('rotation_mode')
        if hasattr(self, "rotation_mode_map"):
            mode = self.rotation_mode_map.get(display_mode, display_mode)
        else:
            mode = display_mode

        if mode not in {"sequence", "priority"}:
            mode = "sequence"

        self.state_controller.hunt_cfg["rotation_mode"] = mode
        self.monster_rotation_controller.refresh_list()
        self.state_controller.set_ui_var('hunt_status', f"Rotation mode: {mode}")






        title = self._t("hunt_monsters")

        # Reset listbox background to default
        if "monster_rotation_listbox" in self.state_controller.ui_widgets and self.state_controller.ui_widgets["monster_rotation_listbox"]:
            self.state_controller.ui_widgets['monster_rotation_listbox'].config(bg="white")

        if hasattr(self, 'tab_hunt') and hasattr(self.tab_hunt, 'monster_frame') and self.tab_hunt.monster_frame:
            self.tab_hunt.monster_frame.config(text=title)



        if not self.state_controller.monster_rotation:
            self.state_controller.set_ui_var('monster_status', self._t("monster_none_selected"))
            return

        mode = self.state_controller.hunt_cfg.get("rotation_mode", "sequence")

        if mode == "sequence":
            self.state_controller.set_ui_var('monster_status', f"Sequence: {len(self.state_controller.monster_rotation)} monsters")
        else:
            sorted_monsters = sorted(
                self.state_controller.monster_rotation, key=lambda m: m.get("priority", 1)
            )
            current = sorted_monsters[0]
            self.state_controller.set_ui_var('monster_status', f"Priority: {current['name']} (P{current.get('priority', 1)}) | {len(self.state_controller.monster_rotation)} total")











    # -----------------
    # Skill library helpers
    # -----------------
    def _update_rotation_mode_description(self):
        """Update rotation mode description."""
        if not hasattr(self, "rotation_desc_var"):
            return

        mode = self.state_controller.get_ui_var('rotation_mode')
        if mode == "sequence":
            self.state_controller.set_ui_var('rotation_desc', "Hunt monsters in order, cycle through list")
        elif mode == "priority":
            self.state_controller.set_ui_var('rotation_desc', "Always hunt highest priority (lowest number)")

    def _reload_setup_advanced_settings(self):
        """Reload Advanced Settings values in Setup tab after timing changes."""
        # Update variables with new values from hunt_cfg
        if self.state_controller.get_ui_var('setup_search_interval') is not None:
            self.state_controller.set_ui_var('setup_search_interval', f"{self.state_controller.hunt_cfg.get('search_interval', 0.25):.2f}")
        if self.state_controller.get_ui_var('setup_attack_interval') is not None:
            self.state_controller.set_ui_var('setup_attack_interval', f"{self.state_controller.hunt_cfg.get('attack_interval', 0.15):.2f}")
        if self.state_controller.get_ui_var('setup_lost_timeout') is not None:
            self.state_controller.set_ui_var('setup_lost_timeout', f"{self.state_controller.hunt_cfg.get('lost_timeout_sec', 0.5):.2f}")
        if self.state_controller.get_ui_var('setup_attack_duration') is not None:
            self.state_controller.set_ui_var('setup_attack_duration', f"{self.state_controller.hunt_cfg.get('attack_min_duration_sec', 5.0):.2f}")

    def _populate_hunt_ui_from_config(self):
        """Populate Hunt tab UI elements from hunt_config.json data."""
        # 1. Window selection
        window_title = self.state_controller.hunt_cfg.get("window_title", "").strip()
        window_pid = self.state_controller.hunt_cfg.get("window_pid")
        window_hwnd = self.state_controller.hunt_cfg.get("window_hwnd")

        if window_title:
            # If we have PID/HWND, create hunt_selected object
            if window_pid and window_hwnd:
                self.state_controller.hunt_selected = {
                    "title": window_title,
                    "pid": window_pid,
                    "hwnd": window_hwnd,
                    "proc": None,  # Process name not saved in config
                }

                # Populate compact selector with saved window
                if hasattr(self, "compact_window_selector"):
                    self.compact_window_selector.set_search_text(window_title)
                    self.state_controller.win_items = [self.state_controller.hunt_selected]

        # 2. Monster template (if exists)
        monster_name = self.state_controller.hunt_cfg.get("monster_selected_name", "").strip()
        _template_path = self.state_controller.hunt_cfg.get("template_path", "").strip()

        if monster_name:
            # Update monster name display (assuming you have a monster_name variable)
            # This will be shown in UI when monster selection is implemented
            pass

        # 3. Skill slots
        skill_slots = self.skill_panel_controller.get_combo_sequence()
        if skill_slots:
            # Update skill UI (assuming skill slot UI variables exist)
            # This will populate skill comboboxes when skill UI is ready
            pass

        # 4. Update any other UI elements that depend on config
        # (Add more as needed based on your UI structure)
        pass

    def _mark_unsaved(self):
        self.has_unsaved_changes = True
        self._update_unsaved_indicator()

    def _update_unsaved_indicator(self):
        """Update unsaved changes indicator UI."""
        if not hasattr(self, "global_apply_btn"):
            return

        if self.has_unsaved_changes:
            # Enable button, show prominent color and text
            self.global_apply_btn.config(
                text=f"💾 {self._t('apply_all_settings_unsaved')}",
                bg=UI.ACCENT_AMBER,
                activebackground="#d97706",
                state="normal"
            )
        else:
            # Disable button, show green color and "no changes" text
            self.global_apply_btn.config(
                text=f"✓ {self._t('apply_all_settings_saved')}",
                bg=UI.ACCENT_GREEN,
                activebackground=UI.ACCENT_GREEN_BG,
                state="disabled"
            )

    def clear_target_ui(self, delay_ms=0):
        if hasattr(self, "tab_hunt") and hasattr(self.tab_hunt, "clear_target_card"):
            self.tab_hunt.clear_target_card(delay_ms)
        if self.state_controller.get_ui_var('hunt_target_info') is not None:
            self.state_controller.set_ui_var('hunt_target_info', self._t("target_card.target_none"))
        if "monster_rotation_listbox" in self.state_controller.ui_widgets and self.state_controller.ui_widgets["monster_rotation_listbox"]:
            try:
                self.state_controller.ui_widgets['monster_rotation_listbox'].selection_clear(0, tk.END)
            except Exception as e:

                logging.debug(f"Failed to clear monster rotation listbox: {e}")

    # ==========================================
    # Lifecycle & Cleanup
    # ==========================================

    def on_close(self):
        self._shutdown_runtime()

    def _shutdown_runtime(self):
        self.lifecycle_controller.on_close()

    def destroy(self):
        self._cleanup_resources()

    def _cleanup_resources(self):
        self._is_destroyed = True
        self.lifecycle_controller.cleanup_before_destroy()
        if hasattr(self, "monster_rotation_controller"):
            self.monster_rotation_controller.unbind_events()
        if hasattr(self, "task_scheduler"):
            self.task_scheduler.cancel_all()
        self.root.destroy()
    def _create_icon_button(
        self,
        parent,
        icon_emoji,
        command,
        style="compact",
        bg_color=None,
        hover_color=None,
        **kwargs,
    ):
        """Create a standardized icon button following UIStyleV2 guidelines.

        **DEPRECATED**: This method now uses the new icon_button component internally.
        For new code, prefer using `from ui.components import create_icon_button` directly.

        Args:
            parent: Parent widget
            icon_emoji: Emoji text for button (e.g., '➕', '↑', '↓') - used as fallback
            command: Button command callback
            style: Size style - 'compact', 'small', 'medium', or 'large'
            bg_color: Background color (uses BTN_ACCENT_BG if not specified)
            hover_color: Hover color (uses BTN_ACCENT_HOVER if not specified)
            **kwargs: Additional button configuration options

        Returns:
            tk.Button: Configured button widget
        """
        # If component available, use it for better icon quality
        if _HAS_ICON_COMPONENT and _create_icon_btn_component is not None:
            # Map emoji to icon names
            emoji_to_icon = {
                "➕": "add",
                "🗑️": "delete",
                "💾": "save",
                "✖": "cancel",
                "🔄": "refresh",
                "↑": "up",
                "↓": "down",
                "📁": "folder",
                "⚙️": "settings",
                "🔍": "search",
            }

            # Map bg_color to button_type
            button_type_map = {
                UI.ACCENT_GREEN: "green_light",
                UI.DANGER: "red",
                UI.ACCENT_BLUE: "blue",
                UI.BG_ELEVATED: "refresh",
            }

            icon_name = emoji_to_icon.get(icon_emoji, "add")
            button_type = button_type_map.get(
                bg_color or UI.ACCENT_GREEN, "green_light"
            )

            # Map style to variant
            variant_map = {
                "compact": "compact",
                "small": "small",
                "medium": "medium",
                "large": "large",
            }
            variant = variant_map.get(style, "compact")

            return _create_icon_btn_component(
                parent=parent,
                icon_name=icon_name,
                icon_fallback=icon_emoji,
                command=command,
                button_type=button_type,
                variant=variant,
                icon_size=16,
                **kwargs,
            )

        # Fallback to old emoji-only method if component not available
        style_configs = {
            "compact": {
                "width": 0,
                "height": 0,
                "padx": UI.SPACE_XS,
                "pady": UI.SPACE_XS,
            },
            "small": {
                "width": 3,
                "height": 1,
                "padx": UI.SPACE_SM,
                "pady": UI.SPACE_SM,
            },
            "medium": {
                "width": 3,
                "height": 1,
                "padx": UI.SPACE_MD,
                "pady": UI.SPACE_MD,
            },
            "large": {
                "width": 4,
                "height": 1,
                "padx": UI.SPACE_LG,
                "pady": UI.SPACE_LG,
            },
        }

        config = style_configs.get(style, style_configs["compact"])

        if bg_color is None:
            bg_color = UI.ACCENT_GREEN
        if hover_color is None:
            hover_color = UI.ACCENT_GREEN_BG

        color_map = {
            UI.ACCENT_GREEN: UI.BG_BASE,
            UI.ACCENT_BLUE: UI.BG_BASE,
            UI.BG_ELEVATED: UI.TEXT_MUTED,
            UI.DANGER: UI.BG_BASE,
        }
        fg_color = color_map.get(bg_color, UI.BG_BASE)

        button_config = {
            "text": icon_emoji,
            "command": command,
            "font": UI.FONT_BUTTON,
            "bg": bg_color,
            "fg": fg_color,
            "activebackground": hover_color,
            "activeforeground": fg_color,
            "relief": "flat",
            "cursor": "hand2",
            **config,
            **kwargs,
        }

        return tk.Button(parent, **button_config)


def main():
    from lib.features.setup.config_migration_service import ConfigMigrationService
    from lib.system.instance_lock import SingleInstanceLock

    instance_lock = SingleInstanceLock("CabalAutoHunt_v1")
    if not instance_lock.acquire():
        root = tk.Tk()
        root.withdraw()
        DialogService.show_error(
            "Application Already Running",
            "Another instance is already running!",
            parent=root,
        )
        root.destroy()
        return

    try:
        from lib.core.app_container import AppContainer
        from lib.features.monsters.monster_library_service import MonsterLibraryService
        from lib.features.skills.skill_runtime_service import SkillRuntimeService
        from lib.db.services.skill_service import SkillService as DbSkillService
        from lib.db.services.class_service import ClassService as DbClassService
        from lib.db.services.scan_service import ScanService
        from lib.features.skills.skill_caster_service import SkillCasterService
        from ui.controllers.overlay_controller import OverlayController as AppOverlayController
        from lib.features.hunt.scan_controller import ScanController
        from lib.vision.vision_engine import get_vision_engine
        from ui.icon_library import Icons
        from lib.features.hunt.hunt_runner import HuntRunner
        from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
        from lib.features.hunt.target_locator import TargetLocatorService
        from lib.ui.controllers.hunt_controller import HuntController
        from lib.ui.controllers.monster_rotation_controller import MonsterRotationController

        root = tk.Tk()
        container = AppContainer()

        container.monster_library_service = MonsterLibraryService()
        container.skill_service = SkillRuntimeService()
        from lib.db.services.skill_type_service import SkillTypeService
        container.db_skill_service = DbSkillService()
        container.db_skill_type_service = SkillTypeService()
        container.db_class_service = DbClassService()
        container.db_scan_service = ScanService()
        container.skill_caster_service = SkillCasterService()

        app = App(root=root, di_container=container)
        ConfigMigrationService.migrate_legacy_attack_keys(app.state_controller, getattr(container, 'skill_service', None), app._t)

        container.overlay_controller = AppOverlayController(app)
        app.overlay_controller = container.overlay_controller

        container.scan_controller = ScanController(
            vision_engine_getter=lambda: getattr(app, "_vision_engine", None) or get_vision_engine(),
            set_status_text=app._update_scan_status_text,
            set_status_icon=app._update_scan_status_icon,
            show_results=app._show_scan_results,
            icons=Icons,
        )
        app.scan_controller = container.scan_controller

        container.hunt_runner = HuntRunner(
            hunt_cfg=app.state_controller.hunt_cfg,
            get_overlay_ctrl=lambda: getattr(app, "overlay_ctrl", None),
            get_notebook=lambda: getattr(app, "notebook", None),
            tab_setup=getattr(app, "tab_setup", None),
            tab_hunt=getattr(app, "tab_hunt", None),
        )
        app.hunt_runner = container.hunt_runner

        container.hunt_orchestrator = HuntOrchestrator(
            locate_target=TargetLocatorService.locate_target,
            prepare_skill_runtime=app.skill_caster_service.prepare_skill_runtime,
            try_cast_skills=app.skill_caster_service.try_cast_skills,
            bring_window_to_front=app.window_controller._bring_window_to_front,
            bring_window_to_front_by_hwnd=app.window_controller._bring_window_to_front_by_hwnd,
            bring_window_to_front_by_pid=app.window_controller._bring_window_to_front_by_pid,
            iconify_app=root.iconify,
            get_hunt_selected=lambda: app.state_controller.hunt_selected,
        )
        app.hunt_orchestrator = container.hunt_orchestrator

        container.hunt_controller = HuntController(
            state_controller=app.state_controller,
            hunt_orchestrator=app.hunt_orchestrator,
            app_root=app
        )
        app.hunt_controller = container.hunt_controller

        container.monster_rotation_controller = MonsterRotationController(
            state_controller=app.state_controller
        )
        app.monster_rotation_controller = container.monster_rotation_controller

        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
    finally:
        instance_lock.release()

if __name__ == "__main__":
    main()
