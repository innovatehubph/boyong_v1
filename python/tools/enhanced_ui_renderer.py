import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

class EnhancedUIRenderer:
    """
    Enhanced UI Rendering System for Pareng Boyong
    Supports React components, Shadcn UI, and advanced HTML/CSS/JS
    """
    
    def __init__(self):
        self.component_library = self._initialize_components()
        self.theme_config = self._get_theme_config()
    
    def _initialize_components(self) -> Dict[str, Any]:
        """Initialize component library with Shadcn UI components"""
        return {
            "shadcn": {
                "button": self._shadcn_button,
                "card": self._shadcn_card,
                "alert": self._shadcn_alert,
                "progress": self._shadcn_progress
            },
            "custom": {
                "dashboard": self._custom_dashboard,
                "status_grid": self._custom_status_grid
            }
        }
    
    def _get_theme_config(self) -> Dict[str, Any]:
        """Get theme configuration for consistent styling"""
        return {
            "colors": {
                "primary": "#0f172a",
                "secondary": "#64748b", 
                "accent": "#3b82f6",
                "muted": "#f8fafc",
                "border": "#e2e8f0",
                "success": "#22c55e",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "info": "#3b82f6"
            },
            "fonts": {
                "sans": "Inter, system-ui, sans-serif",
                "mono": "JetBrains Mono, monospace"
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem", 
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem",
                "2xl": "3rem"
            },
            "radius": {
                "sm": "0.25rem",
                "md": "0.5rem",
                "lg": "0.75rem",
                "xl": "1rem"
            }
        }
    
    def render_component(self, component_type: str, component_name: str, 
                        props: Dict[str, Any] = None) -> str:
        """Render a specific component with props"""
        if props is None:
            props = {}
        
        if component_type in self.component_library:
            if component_name in self.component_library[component_type]:
                return self.component_library[component_type][component_name](props)
        
        return f"<div>Component {component_type}.{component_name} not found</div>"
    
    def _shadcn_button(self, props: Dict[str, Any]) -> str:
        """Render Shadcn UI button component"""
        variant = props.get('variant', 'default')
        size = props.get('size', 'md')
        children = props.get('children', 'Button')
        onclick = props.get('onclick', '')
        disabled = props.get('disabled', False)
        
        variant_classes = {
            'default': 'bg-slate-900 text-slate-50 hover:bg-slate-800',
            'destructive': 'bg-red-500 text-white hover:bg-red-600',
            'outline': 'border border-slate-200 bg-white hover:bg-slate-100',
            'secondary': 'bg-slate-100 text-slate-900 hover:bg-slate-200',
            'ghost': 'hover:bg-slate-100 hover:text-slate-900',
            'link': 'text-slate-900 underline-offset-4 hover:underline'
        }
        
        size_classes = {
            'sm': 'h-8 px-3 text-xs',
            'md': 'h-10 px-4 py-2',
            'lg': 'h-12 px-8 text-base',
            'icon': 'h-10 w-10'
        }
        
        base_classes = "inline-flex items-center justify-center rounded-md font-medium ring-offset-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
        
        classes = f"{base_classes} {variant_classes.get(variant, variant_classes['default'])} {size_classes.get(size, size_classes['md'])}"
        
        disabled_attr = 'disabled' if disabled else ''
        
        return f'''<button class="{classes}" onclick="{onclick}" {disabled_attr}>
            {children}
        </button>'''
    
    def _shadcn_card(self, props: Dict[str, Any]) -> str:
        """Render Shadcn UI card component"""
        title = props.get('title', '')
        description = props.get('description', '')
        children = props.get('children', '')
        footer = props.get('footer', '')
        
        return f'''<div class="rounded-lg border bg-card text-card-foreground shadow-sm">
            {f'<div class="flex flex-col space-y-1.5 p-6"><h3 class="font-semibold leading-none tracking-tight">{title}</h3>{f"<p class='text-sm text-muted-foreground'>{description}</p>" if description else ""}</div>' if title else ''}
            <div class="p-6 pt-0">{children}</div>
            {f'<div class="flex items-center p-6 pt-0">{footer}</div>' if footer else ''}
        </div>'''
    
    def _shadcn_alert(self, props: Dict[str, Any]) -> str:
        """Render Shadcn UI alert component"""
        variant = props.get('variant', 'default')
        title = props.get('title', '')
        children = props.get('children', '')
        
        variant_classes = {
            'default': 'border-slate-200 text-slate-950',
            'destructive': 'border-red-500/50 text-red-900 dark:border-red-500',
            'warning': 'border-yellow-500/50 text-yellow-900'
        }
        
        icons = {
            'default': '💡',
            'destructive': '🚨',
            'warning': '⚠️'
        }
        
        classes = f"relative w-full rounded-lg border p-4 {variant_classes.get(variant, variant_classes['default'])}"
        icon = icons.get(variant, icons['default'])
        
        return f'''<div class="{classes}">
            <div class="flex">
                <div class="flex-shrink-0">
                    <span class="text-lg">{icon}</span>
                </div>
                <div class="ml-3">
                    {f'<h5 class="mb-1 font-medium leading-none tracking-tight">{title}</h5>' if title else ''}
                    <div class="text-sm">{children}</div>
                </div>
            </div>
        </div>'''
    
    def _shadcn_progress(self, props: Dict[str, Any]) -> str:
        """Render Shadcn UI progress component"""
        value = props.get('value', 0)
        max_value = props.get('max', 100)
        label = props.get('label', '')
        show_percentage = props.get('show_percentage', True)
        
        percentage = (value / max_value) * 100
        
        return f'''<div class="w-full">
            {f'<div class="flex justify-between text-sm mb-1"><span>{label}</span><span>{percentage:.0f}%</span></div>' if label or show_percentage else ''}
            <div class="w-full bg-slate-200 rounded-full h-2">
                <div class="bg-slate-900 h-2 rounded-full transition-all duration-300" style="width: {percentage}%"></div>
            </div>
        </div>'''
    
    def _custom_dashboard(self, props: Dict[str, Any]) -> str:
        """Render custom dashboard component"""
        title = props.get('title', 'Dashboard')
        widgets = props.get('widgets', [])
        
        widget_html = ''
        for widget in widgets:
            widget_html += f'''<div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold mb-2">{widget.get('title', 'Widget')}</h3>
                <div class="text-2xl font-bold text-blue-600">{widget.get('value', '0')}</div>
                <p class="text-sm text-gray-500">{widget.get('description', '')}</p>
            </div>'''
        
        return f'''<div class="p-6 bg-gray-50 min-h-screen">
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900">{title}</h1>
                <p class="text-gray-600">Generated by Pareng Boyong at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {widget_html}
            </div>
        </div>'''
    
    def _custom_status_grid(self, props: Dict[str, Any]) -> str:
        """Render custom status grid component"""
        items = props.get('items', [])
        columns = props.get('columns', 3)
        
        grid_class = f"grid-cols-{columns}" if columns <= 4 else "grid-cols-4"
        
        item_html = ''
        for item in items:
            status = item.get('status', 'unknown')
            status_colors = {
                'success': 'bg-green-100 text-green-800',
                'warning': 'bg-yellow-100 text-yellow-800', 
                'error': 'bg-red-100 text-red-800',
                'info': 'bg-blue-100 text-blue-800',
                'unknown': 'bg-gray-100 text-gray-800'
            }
            
            status_icons = {
                'success': '✅',
                'warning': '⚠️',
                'error': '❌', 
                'info': '💡',
                'unknown': '❓'
            }
            
            color_class = status_colors.get(status, status_colors['unknown'])
            icon = status_icons.get(status, status_icons['unknown'])
            
            item_html += f'''<div class="bg-white rounded-lg border p-4 text-center">
                <div class="text-2xl mb-2">{icon}</div>
                <h3 class="font-semibold mb-1">{item.get('title', 'Item')}</h3>
                <span class="inline-block px-2 py-1 rounded-full text-xs font-medium {color_class}">
                    {status.title()}
                </span>
                <p class="text-sm text-gray-600 mt-2">{item.get('description', '')}</p>
            </div>'''
        
        return f'''<div class="grid {grid_class} gap-4">
            {item_html}
        </div>'''
    
    def create_interactive_page(self, title: str, components: List[Dict[str, Any]], 
                               theme: str = "light") -> str:
        """Create a complete interactive HTML page with components"""
        
        components_html = ''
        for comp in components:
            comp_type = comp.get('type', 'shadcn')
            comp_name = comp.get('name', 'card')
            comp_props = comp.get('props', {})
            
            components_html += f'<div class="mb-6">{self.render_component(comp_type, comp_name, comp_props)}</div>'
        
        # Enhanced CSS with Tailwind-like utilities
        css = f'''
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: {self.theme_config['fonts']['sans']};
                line-height: 1.6;
                color: #1e293b;
                background: {'#ffffff' if theme == 'light' else '#0f172a'};
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }}
            
            /* Tailwind-like utilities */
            .grid {{ display: grid; }}
            .grid-cols-1 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }}
            .grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
            .grid-cols-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
            .grid-cols-4 {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
            .gap-4 {{ gap: 1rem; }}
            .gap-6 {{ gap: 1.5rem; }}
            
            .flex {{ display: flex; }}
            .flex-col {{ flex-direction: column; }}
            .items-center {{ align-items: center; }}
            .justify-center {{ justify-content: center; }}
            .justify-between {{ justify-content: space-between; }}
            
            .p-4 {{ padding: 1rem; }}
            .p-6 {{ padding: 1.5rem; }}
            .px-2 {{ padding-left: 0.5rem; padding-right: 0.5rem; }}
            .px-3 {{ padding-left: 0.75rem; padding-right: 0.75rem; }}
            .px-4 {{ padding-left: 1rem; padding-right: 1rem; }}
            .py-1 {{ padding-top: 0.25rem; padding-bottom: 0.25rem; }}
            .py-2 {{ padding-top: 0.5rem; padding-bottom: 0.5rem; }}
            
            .m-2 {{ margin: 0.5rem; }}
            .mb-1 {{ margin-bottom: 0.25rem; }}
            .mb-2 {{ margin-bottom: 0.5rem; }}
            .mb-6 {{ margin-bottom: 1.5rem; }}
            .mb-8 {{ margin-bottom: 2rem; }}
            .mt-2 {{ margin-top: 0.5rem; }}
            .ml-3 {{ margin-left: 0.75rem; }}
            
            .text-xs {{ font-size: 0.75rem; }}
            .text-sm {{ font-size: 0.875rem; }}
            .text-base {{ font-size: 1rem; }}
            .text-lg {{ font-size: 1.125rem; }}
            .text-xl {{ font-size: 1.25rem; }}
            .text-2xl {{ font-size: 1.5rem; }}
            .text-3xl {{ font-size: 1.875rem; }}
            
            .font-medium {{ font-weight: 500; }}
            .font-semibold {{ font-weight: 600; }}
            .font-bold {{ font-weight: 700; }}
            
            .rounded {{ border-radius: 0.25rem; }}
            .rounded-md {{ border-radius: 0.375rem; }}
            .rounded-lg {{ border-radius: 0.5rem; }}
            .rounded-full {{ border-radius: 9999px; }}
            
            .border {{ border-width: 1px; }}
            .border-slate-200 {{ border-color: #e2e8f0; }}
            .border-red-500\\/50 {{ border-color: rgba(239, 68, 68, 0.5); }}
            
            .bg-white {{ background-color: #ffffff; }}
            .bg-slate-50 {{ background-color: #f8fafc; }}
            .bg-slate-100 {{ background-color: #f1f5f9; }}
            .bg-slate-200 {{ background-color: #e2e8f0; }}
            .bg-slate-900 {{ background-color: #0f172a; }}
            .bg-slate-800 {{ background-color: #1e293b; }}
            
            .bg-red-500 {{ background-color: #ef4444; }}
            .bg-red-600 {{ background-color: #dc2626; }}
            .bg-green-100 {{ background-color: #dcfce7; }}
            .bg-yellow-100 {{ background-color: #fef3c7; }}
            .bg-red-100 {{ background-color: #fee2e2; }}
            .bg-blue-100 {{ background-color: #dbeafe; }}
            .bg-gray-100 {{ background-color: #f3f4f6; }}
            
            .text-slate-50 {{ color: #f8fafc; }}
            .text-slate-900 {{ color: #0f172a; }}
            .text-slate-950 {{ color: #020617; }}
            .text-white {{ color: #ffffff; }}
            .text-red-900 {{ color: #7f1d1d; }}
            .text-yellow-900 {{ color: #713f12; }}
            .text-green-800 {{ color: #166534; }}
            .text-yellow-800 {{ color: #92400e; }}
            .text-red-800 {{ color: #991b1b; }}
            .text-blue-800 {{ color: #1e40af; }}
            .text-gray-800 {{ color: #1f2937; }}
            .text-gray-600 {{ color: #4b5563; }}
            .text-gray-500 {{ color: #6b7280; }}
            .text-blue-600 {{ color: #2563eb; }}
            
            .shadow {{ box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); }}
            .shadow-sm {{ box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }}
            
            .hover\\:bg-slate-800:hover {{ background-color: #1e293b; }}
            .hover\\:bg-slate-100:hover {{ background-color: #f1f5f9; }}
            .hover\\:bg-slate-200:hover {{ background-color: #e2e8f0; }}
            .hover\\:bg-red-600:hover {{ background-color: #dc2626; }}
            
            .transition-colors {{ transition-property: color, background-color, border-color, text-decoration-color, fill, stroke; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}
            .transition-all {{ transition-property: all; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}
            .duration-300 {{ transition-duration: 300ms; }}
            
            .inline-flex {{ display: inline-flex; }}
            .inline-block {{ display: inline-block; }}
            
            .w-full {{ width: 100%; }}
            .h-2 {{ height: 0.5rem; }}
            .h-8 {{ height: 2rem; }}
            .h-10 {{ width: 2.5rem; height: 2.5rem; }}
            .h-12 {{ height: 3rem; }}
            .w-10 {{ width: 2.5rem; }}
            
            .relative {{ position: relative; }}
            .leading-none {{ line-height: 1; }}
            .tracking-tight {{ letter-spacing: -0.025em; }}
            .text-center {{ text-align: center; }}
            .underline {{ text-decoration-line: underline; }}
            .underline-offset-4 {{ text-underline-offset: 4px; }}
            
            .min-h-screen {{ min-height: 100vh; }}
            .max-w-1200 {{ max-width: 1200px; }}
            
            /* Card styles */
            .bg-card {{ background-color: #ffffff; }}
            .text-card-foreground {{ color: #0f172a; }}
            .text-muted-foreground {{ color: #64748b; }}
            
            /* Focus states */
            .focus-visible\\:outline-none:focus-visible {{ outline: 2px solid transparent; outline-offset: 2px; }}
            .focus-visible\\:ring-2:focus-visible {{ box-shadow: 0 0 0 2px rgba(15, 23, 42, 1); }}
            .focus-visible\\:ring-slate-950:focus-visible {{ box-shadow: 0 0 0 2px rgba(15, 23, 42, 1); }}
            .focus-visible\\:ring-offset-2:focus-visible {{ box-shadow: 0 0 0 2px white, 0 0 0 4px rgba(15, 23, 42, 1); }}
            
            /* Disabled states */
            .disabled\\:pointer-events-none:disabled {{ pointer-events: none; }}
            .disabled\\:opacity-50:disabled {{ opacity: 0.5; }}
            
            /* Responsive utilities */
            @media (min-width: 768px) {{
                .md\\:grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
            }}
            
            @media (min-width: 1024px) {{
                .lg\\:grid-cols-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
            }}
            
            /* Custom animations */
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .animate-slide-in {{
                animation: slideIn 0.3s ease-out forwards;
            }}
            
            /* Interactive enhancements */
            button {{
                cursor: pointer;
                user-select: none;
            }}
            
            button:active {{
                transform: translateY(1px);
            }}
        </style>
        '''
        
        # Enhanced JavaScript for interactivity
        javascript = '''
        <script>
            // Enhanced interactivity
            document.addEventListener('DOMContentLoaded', function() {
                // Add slide-in animation to elements
                const elements = document.querySelectorAll('.animate-slide-in, .mb-6 > *');
                elements.forEach((el, index) => {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        el.style.transition = 'all 0.3s ease-out';
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    }, index * 100);
                });
                
                // Add hover effects to cards
                const cards = document.querySelectorAll('[class*="rounded-lg"][class*="border"]');
                cards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-2px)';
                        this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
                        this.style.transition = 'all 0.2s ease';
                    });
                    
                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
                    });
                });
                
                // Enhanced button interactions
                const buttons = document.querySelectorAll('button');
                buttons.forEach(button => {
                    button.addEventListener('click', function(e) {
                        // Ripple effect
                        const ripple = document.createElement('span');
                        const rect = this.getBoundingClientRect();
                        const size = Math.max(rect.width, rect.height);
                        const x = e.clientX - rect.left - size / 2;
                        const y = e.clientY - rect.top - size / 2;
                        
                        ripple.style.cssText = `
                            position: absolute;
                            width: ${size}px;
                            height: ${size}px;
                            left: ${x}px;
                            top: ${y}px;
                            background: rgba(255, 255, 255, 0.3);
                            border-radius: 50%;
                            transform: scale(0);
                            animation: ripple 0.6s linear;
                            pointer-events: none;
                        `;
                        
                        this.style.position = 'relative';
                        this.style.overflow = 'hidden';
                        this.appendChild(ripple);
                        
                        setTimeout(() => ripple.remove(), 600);
                    });
                });
                
                console.log('🎨 Pareng Boyong Enhanced UI System Loaded');
                console.log('✨ Interactive components ready');
            });
            
            // Ripple animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
            
            // Utility functions for component interactions
            window.ParengBoyongUI = {
                showAlert: function(message, type = 'info') {
                    const alertDiv = document.createElement('div');
                    const colors = {
                        info: 'bg-blue-100 text-blue-800 border-blue-500',
                        success: 'bg-green-100 text-green-800 border-green-500',
                        warning: 'bg-yellow-100 text-yellow-800 border-yellow-500',
                        error: 'bg-red-100 text-red-800 border-red-500'
                    };
                    
                    alertDiv.className = `fixed top-4 right-4 p-4 rounded-lg border ${colors[type]} shadow-lg z-50 animate-slide-in`;
                    alertDiv.innerHTML = `
                        <div class="flex items-center">
                            <span class="mr-2">${type === 'success' ? '✅' : type === 'warning' ? '⚠️' : type === 'error' ? '❌' : '💡'}</span>
                            <span>${message}</span>
                            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-lg">&times;</button>
                        </div>
                    `;
                    
                    document.body.appendChild(alertDiv);
                    setTimeout(() => alertDiv.remove(), 5000);
                },
                
                updateProgress: function(selector, value) {
                    const progressBar = document.querySelector(selector + ' .bg-slate-900');
                    if (progressBar) {
                        progressBar.style.width = value + '%';
                    }
                }
            };
        </script>
        '''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Pareng Boyong Enhanced UI</title>
    {css}
</head>
<body>
    <div class="container">
        <header class="mb-8">
            <h1 class="text-3xl font-bold mb-2">{title}</h1>
            <p class="text-slate-600">Enhanced UI by Pareng Boyong • Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <main>
            {components_html}
        </main>
        
        <footer class="mt-12 pt-8 border-t border-slate-200 text-center text-slate-500">
            <p>Powered by Pareng Boyong Enhanced UI System</p>
        </footer>
    </div>
    
    {javascript}
</body>
</html>'''


def enhanced_ui_renderer(operation: str = "demo", **kwargs) -> str:
    """
    Enhanced UI Renderer for Pareng Boyong
    
    Operations:
    - demo: Show demo components
    - component: Render specific component
    - page: Create full interactive page
    - dashboard: Create dashboard layout
    """
    
    renderer = EnhancedUIRenderer()
    
    try:
        if operation == "demo":
            # Create a comprehensive demo page
            demo_components = [
                {
                    "type": "shadcn",
                    "name": "alert", 
                    "props": {
                        "variant": "default",
                        "title": "Enhanced UI System Active",
                        "children": "Pareng Boyong now supports React-like components, Shadcn UI elements, and advanced interactivity!"
                    }
                },
                {
                    "type": "custom",
                    "name": "status_grid",
                    "props": {
                        "columns": 3,
                        "items": [
                            {"title": "UI Rendering", "status": "success", "description": "Advanced HTML/CSS/JS rendering active"},
                            {"title": "React Components", "status": "success", "description": "Component system implemented"},
                            {"title": "Shadcn UI", "status": "success", "description": "Design system components available"},
                            {"title": "Interactivity", "status": "success", "description": "Enhanced JavaScript interactions"},
                            {"title": "Multimedia", "status": "warning", "description": "Services need configuration"},
                            {"title": "Self-Awareness", "status": "success", "description": "System monitoring active"}
                        ]
                    }
                },
                {
                    "type": "shadcn",
                    "name": "card",
                    "props": {
                        "title": "Component Examples",
                        "description": "Interactive UI components powered by Pareng Boyong",
                        "children": f'''
                        <div class="space-y-4">
                            {renderer.render_component("shadcn", "button", {"children": "Primary Button", "variant": "default"})}
                            {renderer.render_component("shadcn", "button", {"children": "Destructive", "variant": "destructive"})}
                            {renderer.render_component("shadcn", "button", {"children": "Outline", "variant": "outline"})}
                            <div class="mt-4">
                                {renderer.render_component("shadcn", "progress", {"value": 75, "label": "System Health", "show_percentage": True})}
                            </div>
                        </div>
                        '''
                    }
                }
            ]
            
            return renderer.create_interactive_page("Pareng Boyong Enhanced UI Demo", demo_components)
        
        elif operation == "component":
            comp_type = kwargs.get('type', 'shadcn')
            comp_name = kwargs.get('name', 'button')
            comp_props = kwargs.get('props', {})
            
            return renderer.render_component(comp_type, comp_name, comp_props)
        
        elif operation == "page":
            title = kwargs.get('title', 'Pareng Boyong Page')
            components = kwargs.get('components', [])
            theme = kwargs.get('theme', 'light')
            
            return renderer.create_interactive_page(title, components, theme)
        
        elif operation == "dashboard":
            title = kwargs.get('title', 'Pareng Boyong Dashboard')
            widgets = kwargs.get('widgets', [
                {"title": "Active Users", "value": "1,234", "description": "Online now"},
                {"title": "System Health", "value": "98%", "description": "All systems operational"},
                {"title": "Multimedia Jobs", "value": "45", "description": "In queue"}
            ])
            
            dashboard_html = renderer.render_component("custom", "dashboard", {"title": title, "widgets": widgets})
            return dashboard_html
        
        else:
            return f"❌ **Error**: Unknown operation '{operation}'. Available: demo, component, page, dashboard"
    
    except Exception as e:
        return f"❌ **Enhanced UI Renderer Error**: {str(e)}"