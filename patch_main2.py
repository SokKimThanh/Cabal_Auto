with open("app_gui.py", "r") as f:
    content = f.read()

# We need to correctly initialize the DI container before passing it to App
main_logic = """        from lib.core.app_container import AppContainer
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
        container.db_skill_service = DbSkillService()
        container.db_class_service = DbClassService()
        container.db_scan_service = ScanService()
        container.skill_caster_service = SkillCasterService()

        app = App(root=root, di_container=container)

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
            iconify_app=lambda: root.iconify(),
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
        root.mainloop()"""

content = content.replace('''        from lib.core.app_container import AppContainer
        root = tk.Tk()
        container = AppContainer()
        app = App(root=root, di_container=container)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()''', main_logic)

with open("app_gui.py", "w") as f:
    f.write(content)
