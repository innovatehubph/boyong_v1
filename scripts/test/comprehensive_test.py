#!/usr/bin/env python3
"""
Pareng Boyong - Comprehensive Installation Test
Tests all functionality including multimedia, auto-updates, and integration features.
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Tuple

class ComprehensiveTest:
    """Comprehensive testing suite for Pareng Boyong installation."""
    
    def __init__(self):
        self.repo_root = Path.cwd()
        self.test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {},
            "summary": {"passed": 0, "failed": 0, "skipped": 0}
        }
        
        # Add current directory to Python path
        sys.path.insert(0, str(self.repo_root))
    
    def log_test(self, test_name: str, status: str, message: str = "", details: Dict = None):
        """Log test result."""
        self.test_results["tests"][test_name] = {
            "status": status,
            "message": message,
            "details": details or {}
        }
        
        if status == "PASS":
            self.test_results["summary"]["passed"] += 1
            print(f"✅ {test_name}: {message}")
        elif status == "FAIL":
            self.test_results["summary"]["failed"] += 1
            print(f"❌ {test_name}: {message}")
        else:  # SKIP
            self.test_results["summary"]["skipped"] += 1
            print(f"⏭️ {test_name}: {message}")
    
    def test_file_structure(self):
        """Test that all required files exist."""
        required_files = [
            "README.md",
            "INSTALL.md",
            "GITHUB_SETUP.md",
            "INSTALLATION_FIXES_APPLIED.md",
            "agent.py",
            "models.py",
            "initialize.py",
            "run_ui.py",
            "webui/index.html",
            "python/helpers/files.py",
            "config/settings/requirements.txt",
            "scripts/setup/enhanced_quick_install.sh",
            "scripts/update/auto_update_agent_zero.py",
            "scripts/setup/validate_dependencies.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.repo_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("file_structure", "FAIL", 
                         f"Missing files: {missing_files}", 
                         {"missing_count": len(missing_files)})
        else:
            self.log_test("file_structure", "PASS", 
                         f"All {len(required_files)} required files present")
    
    def test_basic_imports(self):
        """Test that basic modules can be imported."""
        try:
            import agent
            self.log_test("basic_imports", "PASS", "Agent module imported successfully")
        except Exception as e:
            self.log_test("basic_imports", "FAIL", f"Import failed: {e}")
    
    def test_dependency_validation(self):
        """Test dependency validation system."""
        try:
            validator_path = self.repo_root / "scripts/setup/validate_dependencies.py"
            result = subprocess.run([
                sys.executable, str(validator_path), "--report-only"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_test("dependency_validation", "PASS", 
                             "Dependency validator runs successfully")
            else:
                self.log_test("dependency_validation", "FAIL", 
                             f"Validator failed: {result.stderr}")
        except Exception as e:
            self.log_test("dependency_validation", "FAIL", f"Validator error: {e}")
    
    def test_auto_update_system(self):
        """Test auto-update system configuration."""
        try:
            config_file = self.repo_root / "config/update/update_config.json"
            
            if not config_file.exists():
                self.log_test("auto_update_system", "FAIL", "Update config missing")
                return
            
            with open(config_file) as f:
                config = json.load(f)
            
            required_keys = [
                "auto_update_enabled",
                "pareng_boyong_protected_files",
                "agent_zero_core_files_to_update",
                "merge_strategy"
            ]
            
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                self.log_test("auto_update_system", "FAIL", 
                             f"Missing config keys: {missing_keys}")
            else:
                protected_count = len(config.get("pareng_boyong_protected_files", []))
                self.log_test("auto_update_system", "PASS", 
                             f"Update system configured, {protected_count} protected files")
        except Exception as e:
            self.log_test("auto_update_system", "FAIL", f"Config error: {e}")
    
    def test_multimedia_system(self):
        """Test multimedia system availability."""
        try:
            # Check for multimedia directories
            multimedia_dirs = [
                "pareng_boyong_deliverables/images",
                "pareng_boyong_deliverables/videos", 
                "pareng_boyong_deliverables/audio",
                "services/multimodal"
            ]
            
            existing_dirs = [d for d in multimedia_dirs if (self.repo_root / d).exists()]
            
            # Check for multimedia tools
            multimedia_tools = [
                "python/tools/multimedia_generator.py",
                "python/tools/advanced_video_generator.py",
                "python/helpers/multimodal.py"
            ]
            
            existing_tools = [t for t in multimedia_tools if (self.repo_root / t).exists()]
            
            if existing_dirs and existing_tools:
                self.log_test("multimedia_system", "PASS", 
                             f"{len(existing_dirs)} directories, {len(existing_tools)} tools")
            elif existing_dirs or existing_tools:
                self.log_test("multimedia_system", "PASS", 
                             "Partial multimedia system detected")
            else:
                self.log_test("multimedia_system", "SKIP", 
                             "Multimedia system not installed")
        except Exception as e:
            self.log_test("multimedia_system", "FAIL", f"Multimedia test error: {e}")
    
    def test_web_ui_structure(self):
        """Test web UI structure and assets."""
        try:
            webui_files = [
                "webui/index.html",
                "webui/index.js", 
                "webui/index.css"
            ]
            
            missing_ui_files = [f for f in webui_files if not (self.repo_root / f).exists()]
            
            if missing_ui_files:
                self.log_test("web_ui_structure", "FAIL", 
                             f"Missing UI files: {missing_ui_files}")
                return
            
            # Check for Pareng Boyong branding
            html_file = self.repo_root / "webui/index.html"
            with open(html_file) as f:
                html_content = f.read()
            
            pareng_boyong_indicators = [
                "pareng-boyong", "Pareng Boyong", "InnovateHub"
            ]
            
            found_branding = [indicator for indicator in pareng_boyong_indicators 
                            if indicator.lower() in html_content.lower()]
            
            if found_branding:
                self.log_test("web_ui_structure", "PASS", 
                             f"UI structure complete with branding: {found_branding}")
            else:
                self.log_test("web_ui_structure", "PASS", 
                             "Basic UI structure present")
                
        except Exception as e:
            self.log_test("web_ui_structure", "FAIL", f"UI test error: {e}")
    
    def test_configuration_system(self):
        """Test configuration system."""
        try:
            config_dirs = ["config/env", "config/mcp", "config/update", "config/settings"]
            existing_configs = [d for d in config_dirs if (self.repo_root / d).exists()]
            
            # Test requirements files
            req_files = list(self.repo_root.glob("config/settings/requirements*.txt"))
            
            self.log_test("configuration_system", "PASS", 
                         f"{len(existing_configs)} config dirs, {len(req_files)} requirement files")
        except Exception as e:
            self.log_test("configuration_system", "FAIL", f"Config test error: {e}")
    
    def test_security_hardening(self):
        """Test security measures."""
        try:
            # Check for .gitignore
            gitignore = self.repo_root / ".gitignore"
            if not gitignore.exists():
                self.log_test("security_hardening", "FAIL", ".gitignore missing")
                return
            
            with open(gitignore) as f:
                gitignore_content = f.read()
            
            security_patterns = [
                "*.env", "*.key", "*.token", "__pycache__", 
                "node_modules", "*.log"
            ]
            
            missing_patterns = [p for p in security_patterns 
                              if p not in gitignore_content]
            
            if missing_patterns:
                self.log_test("security_hardening", "FAIL", 
                             f"Missing gitignore patterns: {missing_patterns}")
            else:
                self.log_test("security_hardening", "PASS", 
                             "Security patterns in .gitignore")
        except Exception as e:
            self.log_test("security_hardening", "FAIL", f"Security test error: {e}")
    
    def test_python_compatibility(self):
        """Test Python version compatibility."""
        try:
            python_version = sys.version_info
            py_version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            
            if python_version >= (3, 14):
                self.log_test("python_compatibility", "FAIL", 
                             f"Python {py_version_str} not yet supported")
            elif python_version >= (3, 13):
                # Check for compatibility requirements
                compat_req = self.repo_root / f"config/settings/requirements-py{python_version.major}.{python_version.minor}.txt"
                if compat_req.exists():
                    self.log_test("python_compatibility", "PASS", 
                                 f"Python {py_version_str} with compatibility fixes")
                else:
                    self.log_test("python_compatibility", "FAIL", 
                                 f"Python {py_version_str} missing compatibility file")
            elif python_version >= (3, 8):
                self.log_test("python_compatibility", "PASS", 
                             f"Python {py_version_str} fully supported")
            else:
                self.log_test("python_compatibility", "FAIL", 
                             f"Python {py_version_str} too old (minimum 3.8)")
        except Exception as e:
            self.log_test("python_compatibility", "FAIL", f"Version test error: {e}")
    
    def test_documentation_completeness(self):
        """Test documentation completeness."""
        try:
            docs = ["README.md", "INSTALL.md", "GITHUB_SETUP.md", "INSTALLATION_FIXES_APPLIED.md"]
            doc_scores = {}
            
            for doc in docs:
                doc_path = self.repo_root / doc
                if doc_path.exists():
                    with open(doc_path) as f:
                        content = f.read()
                    
                    # Simple completeness check
                    word_count = len(content.split())
                    has_headers = content.count('#') > 3
                    has_code_blocks = '```' in content
                    
                    score = (word_count > 100) + has_headers + has_code_blocks
                    doc_scores[doc] = score
            
            avg_score = sum(doc_scores.values()) / len(doc_scores) if doc_scores else 0
            
            if avg_score >= 2.5:
                self.log_test("documentation_completeness", "PASS", 
                             f"Documentation complete (score: {avg_score:.1f}/3)")
            else:
                self.log_test("documentation_completeness", "FAIL", 
                             f"Documentation incomplete (score: {avg_score:.1f}/3)")
        except Exception as e:
            self.log_test("documentation_completeness", "FAIL", f"Doc test error: {e}")
    
    def test_installation_scripts(self):
        """Test installation scripts."""
        try:
            scripts = [
                "scripts/setup/enhanced_quick_install.sh",
                "scripts/setup/validate_dependencies.py",
                "scripts/update/auto_update_agent_zero.py",
                "scripts/test/test_installation.py"
            ]
            
            executable_scripts = []
            for script in scripts:
                script_path = self.repo_root / script
                if script_path.exists() and os.access(script_path, os.X_OK):
                    executable_scripts.append(script)
            
            self.log_test("installation_scripts", "PASS", 
                         f"{len(executable_scripts)}/{len(scripts)} scripts executable")
        except Exception as e:
            self.log_test("installation_scripts", "FAIL", f"Script test error: {e}")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🧪 Running Comprehensive Pareng Boyong Installation Tests")
        print("=" * 60)
        
        tests = [
            self.test_file_structure,
            self.test_basic_imports,
            self.test_python_compatibility,
            self.test_dependency_validation,
            self.test_configuration_system,
            self.test_web_ui_structure,
            self.test_multimedia_system,
            self.test_auto_update_system,
            self.test_security_hardening,
            self.test_documentation_completeness,
            self.test_installation_scripts
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "")
                self.log_test(test_name, "FAIL", f"Test execution error: {e}")
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        summary = self.test_results["summary"]
        total_tests = sum(summary.values())
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"✅ Passed: {summary['passed']}/{total_tests}")
        print(f"❌ Failed: {summary['failed']}/{total_tests}")
        print(f"⏭️ Skipped: {summary['skipped']}/{total_tests}")
        
        success_rate = (summary['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Save detailed report
        report_file = self.repo_root / "comprehensive_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📋 Detailed report saved: {report_file}")
        
        # Overall assessment
        if summary['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED - Installation is excellent!")
            return True
        elif summary['failed'] <= 2:
            print("\n✅ MOSTLY PASSED - Installation is good with minor issues")
            return True
        else:
            print("\n⚠️ MULTIPLE FAILURES - Installation needs attention")
            return False

def main():
    """Main function."""
    test_suite = ComprehensiveTest()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()