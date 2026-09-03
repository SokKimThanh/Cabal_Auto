#!/usr/bin/env python3
"""
Automated cleanup and verification before merge.

This script runs after session changes to ensure:
1. All temporary files are cleaned
2. Mock/patch state is verified
3. Tests pass and don't leave side effects
4. Code is ready to merge
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import shutil


class CleanupManager:
    """Manage cleanup and verification before merge."""
    
    def __init__(self, project_root: Path = None):
        self.root = project_root or Path(__file__).parent.parent
        self.reports = {}
        self.issues = []
    
    # ========== PHASE 1: TEMPORARY FILE CLEANUP ==========
    
    def cleanup_temp_files(self) -> bool:
        """Remove temporary files created during testing."""
        print("\n🧹 Phase 1: Cleaning temporary files...")
        
        temp_patterns = [
            "*.pyc",           # Compiled Python
            "__pycache__/",    # Cache directories
            "*.tmp",           # Temp files
            "*.log",           # Log files (except hunt_structured.jsonl)
            ".pytest_cache/",  # Pytest cache
            ".coverage",       # Coverage report
            "htmlcov/",        # Coverage HTML
        ]
        
        cleaned_count = 0
        
        for pattern in temp_patterns:
            for path in self.root.rglob(pattern if "/" not in pattern else pattern.rstrip("/")):
                try:
                    if path.is_file():
                        path.unlink()
                        cleaned_count += 1
                    elif path.is_dir():
                        shutil.rmtree(path)
                        cleaned_count += 1
                except Exception as e:
                    self.issues.append(f"Failed to delete {path}: {e}")
        
        print(f"  ✅ Cleaned {cleaned_count} temporary items")
        return True
    
    # ========== PHASE 2: PYTEST CACHE CLEANUP ==========
    
    def cleanup_pytest_cache(self) -> bool:
        """Clean pytest cache and state."""
        print("\n🧹 Phase 2: Cleaning pytest cache...")
        
        pytest_cache_dirs = [
            ".pytest_cache",
            "tests/.pytest_cache",
            ".coverage",
        ]
        
        for cache_dir in pytest_cache_dirs:
            cache_path = self.root / cache_dir
            if cache_path.exists():
                try:
                    shutil.rmtree(cache_path)
                    print(f"  ✅ Removed {cache_dir}")
                except Exception as e:
                    self.issues.append(f"Failed to remove {cache_dir}: {e}")
        
        return True
    
    # ========== PHASE 3: DATABASE CLEANUP ==========
    
    def cleanup_test_databases(self) -> bool:
        """Clean up test databases."""
        print("\n🧹 Phase 3: Cleaning test databases...")
        
        # Remove test database if it exists
        test_db_patterns = [
            "tests/*.db",
            "tests/**/*.db",
            "tmp/*.db",
        ]
        
        db_count = 0
        for pattern in test_db_patterns:
            for db_file in self.root.glob(pattern):
                # Only delete if it looks like a test database
                if "test" in db_file.name or db_file.parent.name == "tmp":
                    try:
                        db_file.unlink()
                        db_count += 1
                        print(f"  ✅ Removed {db_file.relative_to(self.root)}")
                    except Exception as e:
                        self.issues.append(f"Failed to delete {db_file}: {e}")
        
        if db_count == 0:
            print("  ℹ️ No test databases found")
        
        return True
    
    # ========== PHASE 4: RUN VERIFICATION TESTS ==========
    
    def verify_tests_pass(self) -> bool:
        """Run tests to ensure they pass and don't leave side effects."""
        print("\n🧪 Phase 4: Running verification tests...")
        
        try:
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short", "-x"],
                cwd=self.root,
                capture_output=True,
                timeout=300
            )
            
            self.reports["test_exit_code"] = result.returncode
            
            if result.returncode == 0:
                print("  ✅ All tests passed!")
                return True
            else:
                self.issues.append(f"Tests failed with exit code {result.returncode}")
                print(f"  ❌ Tests failed! Output:\n{result.stdout.decode()}")
                return False
        except subprocess.TimeoutExpired:
            self.issues.append("Tests timed out (>5 minutes)")
            return False
        except Exception as e:
            self.issues.append(f"Failed to run tests: {e}")
            return False
    
    # ========== PHASE 5: VERIFY NO LEFTOVER FILES ==========
    
    def verify_no_leftover_files(self) -> bool:
        """Verify tests didn't leave files behind."""
        print("\n📋 Phase 5: Verifying no leftover test files...")
        
        test_temp_files = []
        
        # Check for common leftover files
        leftover_patterns = [
            "tests/**/tmp*.json",
            "tests/**/test_*.db",
            "tests/**/mock_*.json",
        ]
        
        for pattern in leftover_patterns:
            for file in self.root.glob(pattern):
                test_temp_files.append(str(file.relative_to(self.root)))
        
        if test_temp_files:
            print(f"  ⚠️ Found {len(test_temp_files)} leftover files:")
            for f in test_temp_files:
                print(f"     - {f}")
                try:
                    (self.root / f).unlink()
                except:
                    pass
            return False
        else:
            print("  ✅ No leftover files found")
            return True
    
    # ========== PHASE 6: CHECK MOCK COUNT ==========
    
    def verify_mock_reduction(self, expected_range: Tuple[int, int] = None) -> bool:
        """Verify mock count is within expected range."""
        print("\n📊 Phase 6: Verifying mock reduction metrics...")
        
        try:
            result = subprocess.run(
                ["python", "analyze_mocks.py"],
                cwd=self.root,
                capture_output=True,
                timeout=60
            )
            
            output = result.stdout.decode()
            
            # Parse mock count from output
            # Expect format: "Total Mock/Patch Instances: XXX"
            for line in output.split("\n"):
                if "Total Mock/Patch Instances:" in line:
                    mock_count = int(line.split(":")[-1].strip())
                    self.reports["mock_count"] = mock_count
                    
                    if expected_range:
                        min_count, max_count = expected_range
                        if min_count <= mock_count <= max_count:
                            print(f"  ✅ Mock count: {mock_count} (expected: {min_count}-{max_count})")
                            return True
                        else:
                            self.issues.append(
                                f"Mock count {mock_count} outside expected range {min_count}-{max_count}"
                            )
                            print(f"  ❌ Mock count: {mock_count} (expected: {min_count}-{max_count})")
                            return False
                    else:
                        print(f"  ℹ️ Mock count: {mock_count}")
                        return True
            
            self.issues.append("Could not parse mock count from analyze_mocks.py")
            return False
        
        except Exception as e:
            self.issues.append(f"Failed to verify mock count: {e}")
            return False
    
    # ========== PHASE 7: GIT STATUS CHECK ==========
    
    def verify_git_status(self) -> bool:
        """Verify Git working directory is clean."""
        print("\n📁 Phase 7: Checking Git status...")
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.root,
                capture_output=True
            )
            
            status_output = result.stdout.decode().strip()
            
            if not status_output:
                print("  ✅ Git working directory clean")
                return True
            else:
                # Check if only expected files are modified
                allowed_modifications = [
                    "tests/",
                    "lib/",
                    ".gitignore",
                    "docs/",
                    "scripts/",
                    "app_gui.py",
                ]
                
                unexpected = []
                for line in status_output.split("\n"):
                    file_path = line[3:]  # Remove status prefix
                    is_allowed = any(file_path.startswith(prefix) for prefix in allowed_modifications)
                    if not is_allowed:
                        unexpected.append(file_path)
                
                if unexpected:
                    self.issues.append(f"Unexpected modifications: {unexpected}")
                    print(f"  ⚠️ Found unexpected files: {unexpected}")
                    return False
                else:
                    print(f"  ✅ Modified files are all expected ({len(status_output.split())} files)")
                    return True
        
        except Exception as e:
            self.issues.append(f"Failed to check Git status: {e}")
            return False
    
    # ========== PHASE 8: GENERATE CLEANUP REPORT ==========
    
    def generate_cleanup_report(self) -> Dict:
        """Generate comprehensive cleanup report."""
        print("\n📊 Phase 8: Generating cleanup report...")
        
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "status": "PASS" if not self.issues else "FAIL",
            "issues": self.issues,
            "metrics": self.reports,
        }
        
        # Save report
        report_file = self.root / "cleanup_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"  ✅ Report saved to cleanup_report.json")
        
        return report
    
    # ========== MAIN CLEANUP FLOW ==========
    
    def run_full_cleanup(self, expected_mock_range: Tuple[int, int] = None, skip_tests: bool = False) -> bool:
        """Run complete cleanup workflow."""
        print("\n" + "="*60)
        print("🧹 AUTOMATED CLEANUP & MERGE VERIFICATION")
        print("="*60)
        
        phases = [
            ("Temporary Files", self.cleanup_temp_files),
            ("Pytest Cache", self.cleanup_pytest_cache),
            ("Test Databases", self.cleanup_test_databases),
        ]
        
        if not skip_tests:
            phases.append(("Verification Tests", self.verify_tests_pass))
        
        phases.extend([
            ("Leftover Files", self.verify_no_leftover_files),
            ("Mock Metrics", lambda: self.verify_mock_reduction(expected_mock_range)),
            ("Git Status", self.verify_git_status),
        ])
        
        results = {}
        for phase_name, phase_func in phases:
            try:
                results[phase_name] = phase_func()
            except Exception as e:
                self.issues.append(f"Phase '{phase_name}' failed: {e}")
                results[phase_name] = False
        
        # Generate report
        report = self.generate_cleanup_report()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 CLEANUP SUMMARY")
        print("="*60)
        
        for phase_name, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {phase_name}")
        
        if self.issues:
            print("\n⚠️ ISSUES FOUND:")
            for issue in self.issues:
                print(f"  - {issue}")
        
        success = all(results.values()) and not self.issues
        
        print("\n" + "="*60)
        if success:
            print("✅ CLEANUP SUCCESSFUL - READY TO MERGE")
        else:
            print("❌ CLEANUP FAILED - FIX ISSUES BEFORE MERGE")
        print("="*60 + "\n")
        
        return success


def main():
    """Run cleanup workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup and verify before merge")
    parser.add_argument(
        "--mock-range",
        type=str,
        help="Expected mock count range (e.g., '200-250')"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests (for quick cleanup)"
    )
    
    args = parser.parse_args()
    
    manager = CleanupManager()
    
    # Parse mock range
    mock_range = None
    if args.mock_range:
        parts = args.mock_range.split("-")
        mock_range = (int(parts[0]), int(parts[1]))
    
    # Run cleanup
    success = manager.run_full_cleanup(expected_mock_range=mock_range, skip_tests=args.skip_tests)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
