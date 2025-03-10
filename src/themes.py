from typing import Dict


class ThemeManager:
    def __init__(self):
        self.colors = {
            "light": {
                "background": "#ffffff",
                "text": "#000000",
                "primary": "#0078d4",
                "secondary": "#f0f0f0",
                "border": "#e0e0e0",
            },
            "dark": {
                "background": "#1a1a1a",
                "text": "#ffffff",
                "primary": "#0078d4",
                "secondary": "#252526",
                "border": "#3a3a3a",
            },
        }

    def get_dark_theme(self) -> str:
        """Get dark theme stylesheet."""
        c = self.colors["dark"]
        return f"""
        QMainWindow, QWidget {{
            background-color: {c['background']};
            color: {c['text']};
        }}
        
        QPushButton {{
            background-color: {c['primary']};
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: #1884d9;
        }}
        
        /* ...rest of dark theme... */
        """

    def get_light_theme(self) -> str:
        """Get light theme stylesheet."""
        c = self.colors["light"]
        return f"""
        QMainWindow, QWidget {{
            background-color: {c['background']};
            color: {c['text']};
        }}
        
        QPushButton {{
            background-color: {c['primary']};
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: #1884d9;
        }}
        
        /* ...rest of light theme... */
        """

    @staticmethod
    def get_system_colors() -> Dict[str, str]:
        return {
            "success": "#2ed573",
            "warning": "#f7b731",
            "error": "#ff4757",
            "info": "#0078d4",
            "text": "#ffffff",
            "text_secondary": "#8c8c8c",
            "border": "#3a3a3a",
            "background": "#1a1a1a",
            "background_secondary": "#2d2d2d",
        }
