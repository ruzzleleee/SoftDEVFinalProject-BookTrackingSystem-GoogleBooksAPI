"""
Main Dashboard for Book Tracking Application
Central hub with navigation and different views for book management.
"""

import tkinter as tk
from tkinter import ttk
from search_books import SearchBooksFrame
from reading_list import ReadingListFrame
from finished_books import FinishedBooksFrame
from favourites import FavouritesFrame

class MainDashboard(tk.Frame):

    DARK_BROWN = "#3E2723"
    MEDIUM_BROWN = "#5D4037"
    LIGHT_BROWN = "#8D6E63"
    ACCENT_BROWN = "#A1887F"
    CREAM = "#EFEBE9"
    CONTENT_BG = "#f5f5f5"  # Light gray for content area
    WHITE = "#ffffff"
    
    """Main dashboard with sidebar navigation and content area"""
    
    def __init__(self, parent, app, user_id):
        super().__init__(parent, bg="#f5f5f5")
        self.app = app
        self.user_id = user_id
        self.pack(fill="both", expand=True)
        
        self.current_view = None
        
        self.create_widgets()
        
        # Show search view by default
        self.show_search()
        
    def create_widgets(self):
        """Create the dashboard layout with sidebar and content area"""
        # Sidebar
        sidebar = tk.Frame(self, bg="#5D4037", width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Title in sidebar
        logo_frame = tk.Frame(sidebar, bg="#5D4037")
        logo_frame.pack(pady=30, padx=20)
        
        tk.Label(
            logo_frame,
            text="📚",
            font=("Helvetica", 30),
            bg="#5D4037"
        ).pack()
        
        tk.Label(
            logo_frame,
            text="MyBookieeee",
            font=("Helvetica", 16, "bold"),
            bg="#5D4037",
            fg="#EFEBE9"
        ).pack()
        
        # Navigation buttons
        nav_frame = tk.Frame(sidebar, bg="#5D4037")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=20)
        
        self.nav_buttons = {}
        
        # Search Books button
        self.nav_buttons['search'] = self.create_nav_button(
            nav_frame,
            "Search Books",
            self.show_search,
            active=True
        )
        
        # Currently Reading button
        self.nav_buttons['reading'] = self.create_nav_button(
            nav_frame,
            "Currently Reading",
            self.show_reading_list
        )
        
        # Finished Books button
        self.nav_buttons['finished'] = self.create_nav_button(
            nav_frame,
            "Finished Books",
            self.show_finished
        )
        
        # Favourites button
        self.nav_buttons['favourites'] = self.create_nav_button(
            nav_frame,
            "Favorites",
            self.show_favourites
        )
        
        # Spacer
        tk.Frame(nav_frame, bg="#3E2723", height=50).pack()
        
        # Logout button at bottom
        logout_btn = tk.Button(
            sidebar,
            text="Logout",
            font=("Helvetica", 11),
            bg="#3E2723",
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=self.app.logout,
            pady=10
        )
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=20)
        
        # Content area
        self.content_area = tk.Frame(self, bg=self.CREAM)
        self.content_area.pack(side="left", fill="both", expand=True)
        
    def create_nav_button(self, parent, text, command, active=False):
        """Create a navigation button with hover effects"""
        bg_color = "#8D6E63" if active else self.DARK_BROWN
        
        btn = tk.Button(
            parent,
            text=text,
            font=("Helvetica", 12),
            bg=bg_color,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=command,
            anchor="center",
            padx=20,
            pady=12
        )
        btn.pack(fill="x", pady=2)
        
        # Hover effects
        btn.bind("<Enter>", lambda e: btn.config(bg="#8D6E63"))
        btn.bind("<Leave>", lambda e: btn.config(
            bg="#8D6E63" if btn == self.get_active_button() else self.DARK_BROWN
        ))
        
        return btn
        
    def get_active_button(self):
        """Get the currently active navigation button"""
        for btn in self.nav_buttons.values():
            if btn['bg'] == self.LIGHT_BROWN:
                return btn
        return None
        
    def set_active_button(self, button_key):
        """Set a navigation button as active"""
        for key, btn in self.nav_buttons.items():
            if key == button_key:
                btn.config(bg=self.LIGHT_BROWN)
            else:
                btn.config(bg=self.DARK_BROWN)
                
    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
    def show_search(self):
        """Show search books view"""
        self.set_active_button('search')
        self.clear_content()
        self.current_view = SearchBooksFrame(self.content_area, self.app, self.user_id)
        
    def show_reading_list(self):
        """Show currently reading view"""
        self.set_active_button('reading')
        self.clear_content()
        self.current_view = ReadingListFrame(self.content_area, self.app, self.user_id)
        
    def show_finished(self):
        """Show finished books view"""
        self.set_active_button('finished')
        self.clear_content()
        self.current_view = FinishedBooksFrame(self.content_area, self.app, self.user_id)
        
    def show_favourites(self):
        """Show favourites view"""
        self.set_active_button('favourites')
        self.clear_content()
        self.current_view = FavouritesFrame(self.content_area, self.app, self.user_id)