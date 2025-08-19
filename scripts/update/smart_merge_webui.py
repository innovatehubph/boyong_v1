#!/usr/bin/env python3
"""
Smart merge system for Pareng Boyong WebUI files
Preserves all Pareng Boyong branding and features while updating Agent Zero core.
"""

import re
import os
from pathlib import Path
from typing import Dict, List

class SmartWebUImerger:
    """Handles intelligent merging of WebUI files."""
    
    def __init__(self):
        self.pareng_boyong_markers = {
            "html": [
                "<!-- PARENG BOYONG BRANDING START -->",
                "<!-- PARENG BOYONG BRANDING END -->",
                "<!-- PARENG BOYONG MULTIMEDIA START -->", 
                "<!-- PARENG BOYONG MULTIMEDIA END -->",
                "<!-- PARENG BOYONG ENHANCED FEATURES START -->",
                "<!-- PARENG BOYONG ENHANCED FEATURES END -->"
            ],
            "js": [
                "// PARENG BOYONG MULTIMEDIA FEATURES START",
                "// PARENG BOYONG MULTIMEDIA FEATURES END",
                "// PARENG BOYONG ENHANCED UI START", 
                "// PARENG BOYONG ENHANCED UI END"
            ],
            "css": [
                "/* PARENG BOYONG STYLING START */",
                "/* PARENG BOYONG STYLING END */",
                "/* PARENG BOYONG MULTIMEDIA STYLES START */",
                "/* PARENG BOYONG MULTIMEDIA STYLES END */"
            ]
        }
    
    def extract_pareng_boyong_sections(self, content: str, file_type: str) -> Dict[str, str]:
        """Extract all Pareng Boyong sections from a file."""
        sections = {}
        markers = self.pareng_boyong_markers.get(file_type, [])
        
        for i in range(0, len(markers), 2):
            if i + 1 < len(markers):
                start_marker = markers[i]
                end_marker = markers[i + 1]
                
                pattern = f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
                matches = re.findall(pattern, content, re.DOTALL)
                
                if matches:
                    section_name = start_marker.split()[1]  # Get section name
                    sections[section_name] = start_marker + matches[0] + end_marker
        
        return sections
    
    def merge_run_ui_py(self, upstream_content: str, current_content: str) -> str:
        """Smart merge for run_ui.py preserving Pareng Boyong features."""
        
        # Extract Pareng Boyong imports
        pb_imports = []
        current_lines = current_content.split('\n')
        
        for line in current_lines:
            if any(keyword in line.lower() for keyword in [
                'pareng_boyong', 'multimedia', 'elevenlabs', 'toucan_tts', 
                'multimodal', 'enhanced_'
            ]) and ('import' in line or 'from' in line):
                pb_imports.append(line)
        
        # Extract Pareng Boyong route handlers
        pb_routes = []
        in_pb_route = False
        route_buffer = []
        
        for line in current_lines:
            if '@app.route' in line and any(keyword in line for keyword in [
                'multimedia', 'pareng_boyong', 'generate', 'tts'
            ]):
                in_pb_route = True
                route_buffer = [line]
            elif in_pb_route:
                route_buffer.append(line)
                if line.strip() == '' and len([l for l in route_buffer if l.strip()]) > 5:
                    pb_routes.extend(route_buffer)
                    in_pb_route = False
                    route_buffer = []
        
        # Start with upstream content
        result_lines = upstream_content.split('\n')
        
        # Add Pareng Boyong imports after standard imports
        import_insert_point = -1
        for i, line in enumerate(result_lines):
            if 'import' in line and not line.strip().startswith('#'):
                import_insert_point = i
        
        if import_insert_point > -1 and pb_imports:
            result_lines.insert(import_insert_point + 1, '')
            result_lines.insert(import_insert_point + 2, '# Pareng Boyong Multimedia Imports')
            for imp in pb_imports:
                result_lines.insert(import_insert_point + 3, imp)
                import_insert_point += 1
        
        # Add Pareng Boyong routes before app.run()
        app_run_point = -1
        for i, line in enumerate(result_lines):
            if 'app.run(' in line or 'if __name__' in line:
                app_run_point = i
                break
        
        if app_run_point > -1 and pb_routes:
            result_lines.insert(app_run_point, '')
            result_lines.insert(app_run_point + 1, '# Pareng Boyong Routes')
            for route_line in pb_routes:
                result_lines.insert(app_run_point + 2, route_line)
                app_run_point += 1
        
        return '\n'.join(result_lines)
    
    def merge_html_file(self, upstream_content: str, current_content: str) -> str:
        """Smart merge for HTML files preserving Pareng Boyong sections."""
        
        # Extract Pareng Boyong sections from current file
        pb_sections = self.extract_pareng_boyong_sections(current_content, 'html')
        
        # Start with upstream content
        result = upstream_content
        
        # Insert Pareng Boyong branding in head
        if 'BRANDING' in pb_sections:
            head_pattern = r'(<head[^>]*>)'
            if re.search(head_pattern, result):
                result = re.sub(head_pattern, f'\\1\n{pb_sections["BRANDING"]}\n', result)
        
        # Insert multimedia features in body
        if 'MULTIMEDIA' in pb_sections:
            body_pattern = r'(<body[^>]*>)'
            if re.search(body_pattern, result):
                result = re.sub(body_pattern, f'\\1\n{pb_sections["MULTIMEDIA"]}\n', result)
        
        # Insert enhanced features before closing body
        if 'ENHANCED' in pb_sections:
            result = result.replace('</body>', f'{pb_sections["ENHANCED"]}\n</body>')
        
        return result
    
    def merge_js_file(self, upstream_content: str, current_content: str) -> str:
        """Smart merge for JavaScript files preserving Pareng Boyong features."""
        
        pb_sections = self.extract_pareng_boyong_sections(current_content, 'js')
        result = upstream_content
        
        # Add Pareng Boyong features at the end
        for section_name, section_content in pb_sections.items():
            result += f'\n\n{section_content}\n'
        
        return result
    
    def merge_css_file(self, upstream_content: str, current_content: str) -> str:
        """Smart merge for CSS files preserving Pareng Boyong styling."""
        
        pb_sections = self.extract_pareng_boyong_sections(current_content, 'css')
        result = upstream_content
        
        # Add Pareng Boyong styles at the end
        for section_name, section_content in pb_sections.items():
            result += f'\n\n{section_content}\n'
        
        return result

def smart_merge_file(upstream_file: Path, current_file: Path, output_file: Path, file_type: str):
    """Perform smart merge based on file type."""
    
    merger = SmartWebUIMapper()
    
    if not upstream_file.exists() or not current_file.exists():
        print(f"⚠️ Cannot merge {current_file} - missing source files")
        return False
    
    try:
        with open(upstream_file, 'r', encoding='utf-8') as f:
            upstream_content = f.read()
        
        with open(current_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Perform appropriate merge
        if file_type == 'run_ui.py':
            result = merger.merge_run_ui_py(upstream_content, current_content)
        elif file_type == 'html':
            result = merger.merge_html_file(upstream_content, current_content)
        elif file_type == 'js':
            result = merger.merge_js_file(upstream_content, current_content)
        elif file_type == 'css':
            result = merger.merge_css_file(upstream_content, current_content)
        else:
            # Default: use upstream with warning
            print(f"⚠️ No smart merge for {file_type}, using upstream version")
            result = upstream_content
        
        # Write result
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"✅ Smart merged: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Smart merge failed for {current_file}: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 5:
        print("Usage: smart_merge_webui.py <upstream_file> <current_file> <output_file> <file_type>")
        sys.exit(1)
    
    upstream_file = Path(sys.argv[1])
    current_file = Path(sys.argv[2]) 
    output_file = Path(sys.argv[3])
    file_type = sys.argv[4]
    
    success = smart_merge_file(upstream_file, current_file, output_file, file_type)
    sys.exit(0 if success else 1)