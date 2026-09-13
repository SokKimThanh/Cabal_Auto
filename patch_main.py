import re

with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_main = """        # Initialize base app to pass to services that need it
        app = App()

        # Instantiate services
        container = AppContainer()
        container.monster_library_service = MonsterLibraryService()
        container.skill_service = SkillRuntimeService()
        container.db_skill_service = DbSkillService()
        container.db_class_service = DbClassService()
        container.db_scan_service = ScanService()
        container.overlay_controller = AppOverlayController(app)
        container.skill_caster_service = SkillCasterService()

        # Inject container into app for intermediate use
        app.monster_library_service = container.monster_library_service
        app.skill_service = container.skill_service
        app.db_skill_service = container.db_skill_service
        app.db_class_service = container.db_class_service
        app.db_scan_service = container.db_scan_service
        app.overlay_controller = container.overlay_controller
        app.skill_caster_service = container.skill_caster_service"""

new_main = """        # Instantiate base services
        container = AppContainer()
        container.monster_library_service = MonsterLibraryService()
        container.skill_service = SkillRuntimeService()
        container.db_skill_service = DbSkillService()
        container.db_class_service = DbClassService()
        container.db_scan_service = ScanService()
        container.skill_caster_service = SkillCasterService()

        # Initialize base app with DI container
        app = App(di_container=container)

        # Inject services that require app instance
        container.overlay_controller = AppOverlayController(app)
        app.overlay_controller = container.overlay_controller"""

content = content.replace(old_main, new_main)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch applied to main().")
