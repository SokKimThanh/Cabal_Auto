#!/usr/bin/env python3
"""
Automated Cleanup Sessions Runner
Orchestrates execution of 5 cleanup sessions for Sprint 26
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class SessionPhase(Enum):
    ANALYSIS = "analysis"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"
    CLEANUP = "cleanup"

@dataclass
class SessionTask:
    name: str
    description: str
    phase: SessionPhase
    estimated_time: str  # e.g., "2 hours"
    effort: str  # "Low", "Medium", "High"
    risk: str   # "Very Low", "Low", "Low-Medium", "Medium"
    files_affected: List[str]
    dependent_sessions: List[int]  # Session numbers this depends on

class CleanupSession:
    def __init__(self, session_num: int, title: str, objective: str):
        self.session_num = session_num
        self.title = title
        self.objective = objective
        self.tasks: List[SessionTask] = []
        self.status = "pending"  # pending, running, completed, failed
        
    def add_task(self, task: SessionTask):
        self.tasks.append(task)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session": self.session_num,
            "title": self.title,
            "objective": self.objective,
            "status": self.status,
            "tasks": [
                {
                    "name": t.name,
                    "phase": t.phase.value,
                    "time": t.estimated_time,
                    "effort": t.effort,
                    "risk": t.risk,
                    "files": t.files_affected,
                    "dependencies": t.dependent_sessions
                }
                for t in self.tasks
            ]
        }

def create_sessions() -> Dict[int, CleanupSession]:
    """Define all 5 cleanup sessions"""
    sessions = {}
    
    # Session 1: Consolidate Platform Mocks
    session1 = CleanupSession(
        1,
        "Consolidate Platform Mocks",
        "Remove duplicated sys.modules patches from test files into centralized conftest.py"
    )
    session1.add_task(SessionTask(
        "Analysis", "Search and inventory platform mocks",
        SessionPhase.ANALYSIS, "10 min", "Low", "Very Low",
        ["tests/"],
        []
    ))
    session1.add_task(SessionTask(
        "Create Fixture", "Add platform mock fixture to conftest.py",
        SessionPhase.IMPLEMENTATION, "20 min", "Low", "Very Low",
        ["tests/conftest.py"],
        []
    ))
    session1.add_task(SessionTask(
        "Remove Duplication", "Remove mocks from 6 test files",
        SessionPhase.IMPLEMENTATION, "30 min", "Low", "Very Low",
        [
            "tests/unit/test_action_bar.py",
            "tests/ui/test_footer_visibility.py",
            "tests/ui/test_hunt_bottom_logs.py",
            "tests/unit/features/hunt/test_orchestrator_ocr_fallback.py",
            "tests/unit/features/hunt/test_window_selection_service.py",
            "tests/unit/ui/controllers/test_hotkey_controller.py",
        ],
        []
    ))
    session1.add_task(SessionTask(
        "Verify", "Run full test suite to confirm no regressions",
        SessionPhase.VERIFICATION, "15 min", "Low", "Very Low",
        ["tests/"],
        []
    ))
    sessions[1] = session1
    
    # Session 2: Create Standard Test Fixtures
    session2 = CleanupSession(
        2,
        "Create Standard Test Fixtures",
        "Create reusable test fixtures to eliminate mock boilerplate code"
    )
    session2.add_task(SessionTask(
        "Analyze Mock Patterns", "Identify common mock setup across test files",
        SessionPhase.ANALYSIS, "30 min", "Medium", "Low",
        ["tests/test_hunt_orchestrator.py", "tests/unit/test_action_bar.py"],
        []
    ))
    session2.add_task(SessionTask(
        "Design Fixtures", "Design 4-5 main fixtures for common patterns",
        SessionPhase.DESIGN, "30 min", "Medium", "Low",
        [],
        []
    ))
    session2.add_task(SessionTask(
        "Implement Fixtures", "Add fixtures to tests/conftest.py",
        SessionPhase.IMPLEMENTATION, "1.5 hours", "Medium", "Low",
        ["tests/conftest.py"],
        [1]  # Depends on Session 1
    ))
    session2.add_task(SessionTask(
        "Refactor Test Files", "Update 12+ test files to use fixtures",
        SessionPhase.IMPLEMENTATION, "2-3 hours", "Medium", "Low-Medium",
        [
            "tests/test_hunt_orchestrator.py",
            "tests/unit/features/hunt/test_orchestrator_ocr_fallback.py",
            "tests/unit/features/hunt/test_orchestrator_loop.py",
            "tests/unit/test_action_bar.py",
        ],
        [1]
    ))
    sessions[2] = session2
    
    # Session 3: Replace Nested Patch Chains
    session3 = CleanupSession(
        3,
        "Replace Nested Patch Chains",
        "Convert nested with patch() chains to clean @patch decorators"
    )
    session3.add_task(SessionTask(
        "Identify Files", "Find files with nested patch() statements",
        SessionPhase.ANALYSIS, "20 min", "Low", "Very Low",
        ["tests/unit/ui/"],
        []
    ))
    session3.add_task(SessionTask(
        "Refactor Decorators", "Convert nested patches to @patch decorators",
        SessionPhase.IMPLEMENTATION, "2 hours", "Low", "Very Low",
        [
            "tests/unit/ui/test_monster_editor_left_panel.py",
            "tests/unit/ui/test_monster_editor_save.py",
            "tests/unit/ui/test_monster_editor_data.py",
        ],
        []
    ))
    session3.add_task(SessionTask(
        "Extract Fixtures", "Move common patch chains to fixtures",
        SessionPhase.IMPLEMENTATION, "1 hour", "Low", "Low",
        ["tests/conftest.py"],
        []
    ))
    sessions[3] = session3
    
    # Session 4: Refactor HuntOrchestrator
    session4 = CleanupSession(
        4,
        "Refactor HuntOrchestrator (MAJOR)",
        "Reduce HuntOrchestrator callbacks from 15 to 1 via handler object"
    )
    session4.add_task(SessionTask(
        "Design Handler", "Create HuntStatusHandler abstract class",
        SessionPhase.DESIGN, "2 hours", "High", "Medium",
        ["lib/orchestrator/"],
        []
    ))
    session4.add_task(SessionTask(
        "Update Orchestrator", "Refactor orchestrator to accept handler",
        SessionPhase.IMPLEMENTATION, "1 day", "High", "Medium",
        ["lib/orchestrator/hunt_orchestrator.py"],
        [1, 2]
    ))
    session4.add_task(SessionTask(
        "Create Adapter", "Implement AppHuntHandler in app_gui.py",
        SessionPhase.IMPLEMENTATION, "1 hour", "High", "Medium",
        ["app_gui.py"],
        [1, 2]
    ))
    session4.add_task(SessionTask(
        "Update Library Code", "Refactor callback invocations across library",
        SessionPhase.IMPLEMENTATION, "1 day", "High", "Medium",
        ["lib/features/hunt/", "lib/orchestrator/"],
        [1, 2]
    ))
    session4.add_task(SessionTask(
        "Verify", "Run all tests and manual app testing",
        SessionPhase.VERIFICATION, "1 day", "High", "Medium",
        ["tests/"],
        [1, 2]
    ))
    sessions[4] = session4
    
    # Session 5: Split Integration/Unit Tests
    session5 = CleanupSession(
        5,
        "Split Integration/Unit Tests",
        "Separate integration tests from unit tests into distinct directories"
    )
    session5.add_task(SessionTask(
        "Classify Tests", "Determine unit vs integration for all tests",
        SessionPhase.ANALYSIS, "4 hours", "Medium", "Low",
        ["tests/"],
        []
    ))
    session5.add_task(SessionTask(
        "Reorganize", "Move files to new tests/unit/ and tests/integration/",
        SessionPhase.IMPLEMENTATION, "3 hours", "Medium", "Low",
        ["tests/"],
        []
    ))
    session5.add_task(SessionTask(
        "Fix Imports", "Update all import statements in moved files",
        SessionPhase.IMPLEMENTATION, "3 hours", "Medium", "Low-Medium",
        ["tests/"],
        []
    ))
    session5.add_task(SessionTask(
        "Configure Pytest", "Set up conftest files and pytest markers",
        SessionPhase.IMPLEMENTATION, "1 hour", "Medium", "Low",
        ["pytest.ini", "tests/conftest.py"],
        []
    ))
    session5.add_task(SessionTask(
        "Verify", "Run unit and integration test suites",
        SessionPhase.VERIFICATION, "1 hour", "Medium", "Low",
        ["tests/"],
        [1, 2, 3, 4]
    ))
    sessions[5] = session5
    
    return sessions

def print_session_summary(sessions: Dict[int, CleanupSession]):
    """Print summary of all sessions"""
    print("=" * 80)
    print("🧹 SPRINT 26 CLEANUP SESSIONS - EXECUTION PLAN")
    print("=" * 80)
    print()
    
    for num in sorted(sessions.keys()):
        session = sessions[num]
        print(f"\n📋 Session {num}: {session.title}")
        print(f"   Objective: {session.objective}")
        print(f"   Tasks: {len(session.tasks)}")
        
        total_time = 0
        for task in session.tasks:
            print(f"   ✓ {task.name} ({task.phase.value})")
        
        print(f"   Affects: {len(session.tasks[0].files_affected)} files")

def export_json(sessions: Dict[int, CleanupSession], output_path: str):
    """Export sessions to JSON for tooling"""
    data = {
        "project": "Cabal_Auto",
        "sprint": 26,
        "initiative": "Test & Mock Cleanup",
        "sessions": [sessions[i].to_dict() for i in sorted(sessions.keys())],
        "execution_order": "1 → 2 → 3 ↓ | 4 → 5",
        "total_effort_weeks": 3,
        "estimated_duration_days": 10,
        "risk_level": "Low-Medium",
        "rollback_capability": "Full (via git commit)"
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Exported session configuration to {output_path}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automated cleanup sessions runner for Sprint 26"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print session summary"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export sessions to JSON file"
    )
    parser.add_argument(
        "--session",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific session"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Execute all sessions in order"
    )
    
    args = parser.parse_args()
    
    sessions = create_sessions()
    
    if args.summary or (not args.export and not args.session and not args.all):
        print_session_summary(sessions)
    
    if args.export:
        export_json(sessions, args.export)
    
    if args.session:
        print(f"\n🚀 Executing Session {args.session}...")
        print(f"   Title: {sessions[args.session].title}")
        print(f"   Prompt: See AUTOMATED_EXECUTION_PROMPTS.md")
    
    if args.all:
        print("\n🚀 Executing ALL sessions...")
        print("   Order: 1 → 2 → 3 (parallel) ↓ | 4 → 5")
        print("   See AUTOMATED_EXECUTION_PROMPTS.md for detailed prompts")

if __name__ == "__main__":
    main()
