"""
Book Tracking Application - Main Entry Point
A comprehensive book tracking system with user authentication, Google Books API integration,
reading progress tracking, and reading streak calendar.
"""

import tkinter as tk
from auth_page import AuthPage
from database import Database

class BookTrackerApp:
    """Main application class that manages the window and navigation"""
    
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("MyBookieeee - Your Reading Companion")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")
        
        # Center window on screen
        self.center_window()
        
        # Initialize database
        self.db = Database()
        
        # Store current user
        self.current_user = None
        
        # Store current frame
        self.current_frame = None
        
        # Show authentication page
        self.show_auth_page()
        
    def center_window(self):
        """Center the application window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def show_auth_page(self):
        """Display the authentication (login/register) page"""
        self.clear_frame()
        self.current_frame = AuthPage(self.root, self)
        
    def show_main_dashboard(self, user_id):
        """Display the main dashboard after successful login"""
        from main_dashboard import MainDashboard
        self.current_user = user_id
        self.clear_frame()
        self.current_frame = MainDashboard(self.root, self, user_id)
        
    def clear_frame(self):
        """Clear the current frame from window"""
        if self.current_frame:
            self.current_frame.destroy()
            
    def logout(self):
        """Logout current user and return to auth page"""
        self.current_user = None
        self.show_auth_page()
        
    def run(self):
        """Start the application main loop"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BookTrackerApp()
    app.run() 