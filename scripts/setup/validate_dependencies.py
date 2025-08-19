#!/usr/bin/env python3
"""
Pareng Boyong - Comprehensive Dependency Validator
Validates and fixes all dependencies with Python version compatibility.
"""

import sys
import subprocess
import json
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class DependencyValidator:
    """Validates and manages all Pareng Boyong dependencies."""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.platform_system = platform.system()
        self.repo_root = Path.cwd()
        
        # Python version compatibility map
        self.version_compatibility = {
            "kokoro": {
                "3.13": ">=0.7.16",
                "3.12": ">=0.9.2", 
                "3.11": ">=0.9.2",
                "3.10": ">=0.9.2"
            },
            "unstructured": {
                "3.13": ">=0.15.0",
                "3.12": ">=0.16.23",
                "3.11": ">=0.16.23"
            },
            "playwright": {
                "3.13": ">=1.40.0",
                "default": ">=1.52.0"
            }
        }
        
        # Missing dependencies discovered during testing
        self.additional_dependencies = [
            "crontab>=1.0.1",
            "inputimeout>=1.0.4", 
            "flaredantic>=0.1.4",
            "requests>=2.31.0",
            "openai>=1.0.0",
            "setuptools>=75.0.0"  # For Python 3.13 compatibility
        ]
    
    def get_python_version_key(self) -> str:
        """Get Python version key for compatibility lookup."""
        return f"{self.python_version.major}.{self.python_version.minor}"
    
    def get_compatible_version(self, package: str) -> str:
        """Get compatible version for current Python version."""
        if package in self.version_compatibility:
            version_map = self.version_compatibility[package]
            py_version = self.get_python_version_key()
            
            if py_version in version_map:
                return version_map[py_version]
            elif "default" in version_map:
                return version_map["default"]
        
        return ""  # Use version from requirements.txt
    
    def read_requirements(self, requirements_file: Path) -> List[str]:
        """Read and parse requirements file."""
        if not requirements_file.exists():
            return []
        
        requirements = []
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
        
        return requirements
    
    def fix_requirements_compatibility(self, requirements: List[str]) -> List[str]:
        """Fix requirements for current Python version."""
        fixed_requirements = []
        
        for req in requirements:
            package_name = req.split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
            compatible_version = self.get_compatible_version(package_name)
            
            if compatible_version:
                # Replace version with compatible one
                fixed_req = f"{package_name}{compatible_version}"
                fixed_requirements.append(fixed_req)
                print(f"🔧 Fixed {package_name}: {req} → {fixed_req}")
            else:
                fixed_requirements.append(req)
        
        # Add additional dependencies
        for additional_dep in self.additional_dependencies:
            if not any(additional_dep.split('>=')[0] in req for req in fixed_requirements):
                fixed_requirements.append(additional_dep)
                print(f"➕ Added missing: {additional_dep}")
        
        return fixed_requirements
    
    def create_compatible_requirements(self) -> bool:
        """Create Python version compatible requirements file."""
        try:
            original_req = self.repo_root / "config/settings/requirements.txt"
            compatible_req = self.repo_root / f"config/settings/requirements-py{self.get_python_version_key()}.txt"
            
            if not original_req.exists():
                print(f"❌ Requirements file not found: {original_req}")
                return False
            
            # Read original requirements
            requirements = self.read_requirements(original_req)
            
            # Fix for compatibility
            fixed_requirements = self.fix_requirements_compatibility(requirements)
            
            # Write compatible requirements
            compatible_req.parent.mkdir(parents=True, exist_ok=True)
            with open(compatible_req, 'w') as f:
                f.write(f"# Python {self.get_python_version_key()} Compatible Requirements for Pareng Boyong\n")
                f.write(f"# Auto-generated on {sys.version}\n\n")
                
                for req in sorted(fixed_requirements):
                    f.write(f"{req}\n")
            
            print(f"✅ Created compatible requirements: {compatible_req}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create compatible requirements: {e}")
            return False
    
    def validate_installation(self) -> Dict:
        """Validate current installation."""
        results = {
            "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
            "platform": self.platform_system,
            "compatible": True,
            "missing_packages": [],
            "incompatible_packages": [],
            "installation_issues": []
        }
        
        print(f"🐍 Python Version: {results['python_version']}")
        print(f"💻 Platform: {results['platform']}")
        
        # Check Python version compatibility
        if self.python_version >= (3, 14):
            results["compatible"] = False
            results["installation_issues"].append("Python 3.14+ not yet supported")
            print("⚠️ Python 3.14+ may have compatibility issues")
        elif self.python_version >= (3, 13):
            print("⚠️ Python 3.13+ detected - applying compatibility fixes")
        
        # Test critical imports
        critical_packages = [
            ('flask', 'Flask web framework'),
            ('flask_basicauth', 'Flask authentication'),
            ('litellm', 'LiteLLM for AI models'),
            ('docker', 'Docker client'),
            ('sentence_transformers', 'Embeddings'),
            ('tiktoken', 'Token counting'),
            ('paramiko', 'SSH client')
        ]
        
        for package, description in critical_packages:
            try:
                __import__(package)
                print(f"✅ {package}: {description}")
            except ImportError:
                results["missing_packages"].append(package)
                print(f"❌ {package}: Missing - {description}")
        
        # Test Pareng Boyong specific modules
        pareng_boyong_modules = [
            ('python.helpers.files', 'File system utilities'),
            ('python.helpers.tool', 'Tool framework'),
            ('agent', 'Main agent module')
        ]
        
        original_path = sys.path[:]
        sys.path.insert(0, str(self.repo_root))
        
        for module, description in pareng_boyong_modules:
            try:
                __import__(module)
                print(f"✅ {module}: {description}")
            except ImportError as e:
                results["installation_issues"].append(f"{module}: {e}")
                print(f"❌ {module}: Failed - {description}")
        
        sys.path = original_path
        
        return results
    
    def install_missing_dependencies(self, missing_packages: List[str]) -> bool:
        """Install missing dependencies."""
        if not missing_packages:
            return True
        
        print(f"📦 Installing {len(missing_packages)} missing packages...")
        
        try:
            # Use compatible requirements file if available
            py_version = self.get_python_version_key()
            compatible_req = self.repo_root / f"config/settings/requirements-py{py_version}.txt"
            
            if compatible_req.exists():
                print(f"📋 Using compatible requirements: {compatible_req}")
                cmd = [sys.executable, "-m", "pip", "install", "-r", str(compatible_req), "--quiet"]
            else:
                # Install missing packages individually
                cmd = [sys.executable, "-m", "pip", "install"] + missing_packages + ["--quiet"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
            else:
                print(f"❌ Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    
    def generate_installation_report(self, results: Dict) -> str:
        """Generate detailed installation report."""
        report = f"""
# Pareng Boyong Installation Report

## System Information
- **Python Version**: {results['python_version']}
- **Platform**: {results['platform']}
- **Repository**: {self.repo_root}
- **Compatibility**: {'✅ Compatible' if results['compatible'] else '❌ Issues detected'}

## Validation Results

### Missing Packages
"""
        if results['missing_packages']:
            for package in results['missing_packages']:
                report += f"- ❌ {package}\n"
        else:
            report += "- ✅ All critical packages available\n"
        
        report += "\n### Installation Issues\n"
        if results['installation_issues']:
            for issue in results['installation_issues']:
                report += f"- ⚠️ {issue}\n"
        else:
            report += "- ✅ No installation issues detected\n"
        
        report += f"""
## Recommendations

### For Python 3.13+ Users:
1. Use compatible requirements file: `config/settings/requirements-py{self.get_python_version_key()}.txt`
2. Consider using Python 3.12 for best compatibility
3. Ensure setuptools >= 75.0.0 for package building

### For Production Deployment:
1. Use virtual environment
2. Pin dependency versions
3. Regular dependency updates
4. Monitor for security advisories

## Quick Fix Commands

```bash
# Install compatible requirements
pip install -r config/settings/requirements-py{self.get_python_version_key()}.txt

# Validate installation  
python scripts/setup/validate_dependencies.py

# Test installation
python scripts/test/test_installation.py
```
"""
        return report
    
    def run_validation(self) -> bool:
        """Run complete validation process."""
        print("🔍 Starting Pareng Boyong dependency validation...")
        print("=" * 60)
        
        # Create compatible requirements
        if not self.create_compatible_requirements():
            return False
        
        # Validate current installation
        results = self.validate_installation()
        
        # Install missing dependencies
        if results['missing_packages']:
            if not self.install_missing_dependencies(results['missing_packages']):
                return False
            
            # Re-validate after installation
            print("\n🔄 Re-validating after dependency installation...")
            results = self.validate_installation()
        
        # Generate report
        report = self.generate_installation_report(results)
        
        # Save report
        report_file = self.repo_root / "validation_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📋 Validation report saved: {report_file}")
        
        success = results['compatible'] and not results['missing_packages'] and not results['installation_issues']
        
        if success:
            print("🎉 Validation completed successfully!")
        else:
            print("⚠️ Validation completed with issues - check report for details")
        
        return success

def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pareng Boyong Dependency Validator")
    parser.add_argument("--fix", action="store_true", help="Automatically fix compatibility issues")
    parser.add_argument("--install", action="store_true", help="Install missing dependencies")
    parser.add_argument("--report-only", action="store_true", help="Generate report only")
    
    args = parser.parse_args()
    
    validator = DependencyValidator()
    
    if args.report_only:
        results = validator.validate_installation()
        report = validator.generate_installation_report(results)
        print(report)
    else:
        success = validator.run_validation()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()