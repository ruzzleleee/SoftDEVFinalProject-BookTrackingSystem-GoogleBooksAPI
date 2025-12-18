"""
Search Books View
Allows users to search for books using Google Books API and add them to their collection.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from google_books_api import GoogleBooksAPI
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

class SearchBooksFrame(tk.Frame):
    """Frame for searching and adding books"""  
    DARK_BROWN = "#3E2723"
    MEDIUM_BROWN = "#5D4037"
    LIGHT_BROWN = "#8D6E63"
    ACCENT_BROWN = "#A1887F"
    CREAM = "#EFEBE9"
    WHITE = "#f5f5f5"

    def __init__(self, parent, app, user_id):
        super().__init__(parent, bg=self.CREAM)
        self.app = app
        self.user_id = user_id
        self.pack(fill="both", expand=True)
        
        self.search_results = []
        self.book_images = {}  # Cache for book cover images
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the search interface"""
        # Header
        header = tk.Frame(self, bg=self.LIGHT_BROWN, height=100)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Search Books",
            font=("Helvetica", 24, "bold"),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(side="left", padx=20, pady=20)
        
        # Search bar
        search_frame = tk.Frame(self, bg="#f5f5f5")
        search_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        search_container = tk.Frame(search_frame, bg="white")
        search_container.pack(fill="x")
        
        self.search_entry = tk.Entry(
            search_container,
            font=("Helvetica", 14),
            bg="white",
            relief="flat",
            fg="#2c3e50"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=20, pady=15, ipady=5)
        self.search_entry.bind("<Return>", lambda e: self.search_books())
        
        search_btn = tk.Button(
            search_container,
            text="Search",
            font=("Helvetica", 12),
            bg=self.DARK_BROWN,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.search_books,
            padx=30,
            pady=10
        )
        search_btn.pack(side="right", padx=20)
        
        # Results container with scrollbar
        results_container = tk.Frame(self, bg=self.LIGHT_BROWN)
        results_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Canvas and scrollbar for results
        canvas = tk.Canvas(results_container, bg=self.LIGHT_BROWN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=canvas.yview)
        
        self.results_frame = tk.Frame(canvas, bg=self.LIGHT_BROWN)
        
        self.results_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
       
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Initial message
        self.show_message("Search for books to get started!")

    def show_message(self, message):
        """Display a message in the results area"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        tk.Label(
            self.results_frame,
            text=message,
            font=("Helvetica", 14),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(padx=455, pady=50)
        
    def search_books(self):
        """Search for books using the Google Books API"""
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Empty Search", "Please enter a search query")
            return
            
        self.show_message("Searching...")
        
        # Search in a separate thread to avoid blocking UI
        def search_thread():
            results = GoogleBooksAPI.search_books(query)
            self.search_results = results
            self.after(0, self.display_results)
            
        threading.Thread(target=search_thread, daemon=True).start()
        
    def display_results(self):
        """Display search results"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if not self.search_results:
            self.show_message("No books found. Try a different search.")
            return
            
        for book in self.search_results:
            self.create_book_card(book)
            
    def create_book_card(self, book):
        """Create a card widget for a book"""
        card = tk.Frame(self.results_frame, bg=self.MEDIUM_BROWN, relief="flat")
        card.pack(fill="x", pady=10, padx=10)
        
        # Add subtle border
        border = tk.Frame(card, bg=self.DARK_BROWN, height=2)
        border.pack(fill="x", side="bottom")
        
        content = tk.Frame(card, bg=self.MEDIUM_BROWN)
        content.pack(fill="x", padx=20, pady=20)
        
        # Book cover (left side)
        cover_frame = tk.Frame(content, bg=self.MEDIUM_BROWN)
        cover_frame.pack(side="left", padx=(0, 20))
        
        # Load cover image in separate thread
        cover_label = tk.Label(cover_frame, bg=self.MEDIUM_BROWN, text="📚", font=("Helvetica", 40))
        cover_label.pack()
        
        if book['cover_url']:
            def load_image():
                try:
                    response = requests.get(book['cover_url'], timeout=5)
                    img_data = response.content
                    img = Image.open(BytesIO(img_data))
                    img = img.resize((100, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.book_images[book['google_books_id']] = photo
                    cover_label.config(image=photo, text="")
                except:
                    pass
                    
            threading.Thread(target=load_image, daemon=True).start()
        
        # Book info (middle)
        info_frame = tk.Frame(content, bg=self.MEDIUM_BROWN)
        info_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            info_frame,
            text=book['title'][:60] + ('...' if len(book['title']) > 60 else ''),
            font=("Helvetica", 14, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM,
            anchor="w"
        ).pack(fill="x")
        
        tk.Label(
            info_frame,
            text=f"by {book['authors']}",
            font=("Helvetica", 11),
            bg=self.MEDIUM_BROWN,
            fg=self.ACCENT_BROWN,
            anchor="w"
        ).pack(fill="x", pady=(5, 10))
        
        # Description preview
        desc = book['description'][:200] + ('...' if len(book['description']) > 200 else '')
        tk.Label(
            info_frame,
            text=desc,
            font=("Helvetica", 10),
            bg=self.MEDIUM_BROWN,
            fg=self.ACCENT_BROWN,
            anchor="w",
            wraplength=500,
            justify="left"
        ).pack(fill="x")
        
        # Additional info
        info_text = []
        if book['page_count']:
            info_text.append(f"{book['page_count']} pages")
        if book['published_date']:
            info_text.append(f"Published: {book['published_date'][:4]}")
        if book['categories']:
            info_text.append(book['categories'])
            
        if info_text:
            tk.Label(
                info_frame,
                text=" • ".join(info_text),
                font=("Helvetica", 9),
                bg=self.MEDIUM_BROWN,
                fg=self.ACCENT_BROWN,
                anchor="w"
            ).pack(fill="x", pady=(10, 0))
        
        # Action buttons (right side)
        actions_frame = tk.Frame(content, bg=self.MEDIUM_BROWN)
        actions_frame.pack(side="right", padx=(20, 0))
        
        # Quick Add buttons with icons and tooltips
        reading_btn = tk.Button(
            actions_frame,
            text="Reading",
            font=("Helvetica", 10),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda b=book: self.add_to_list(b, 'currently_reading'),
            padx=15,
            pady=8,
            width=12
        )
        reading_btn.pack(pady=5)
        
        # Tooltip on hover
        self.create_tooltip(reading_btn, "Add to Currently Reading")
        
        finished_btn = tk.Button(
            actions_frame,
            text="Finished",
            font=("Helvetica", 10),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda b=book: self.add_to_list(b, 'finished'),
            padx=15,
            pady=8,
            width=12
        )
        finished_btn.pack(pady=5)
        
        self.create_tooltip(finished_btn, "Add to Finished Books")
        
        fav_btn = tk.Button(
            actions_frame,
            text="Favorite",
            font=("Helvetica", 10),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda b=book: self.add_to_list(b, 'favourite'),
            padx=15,
            pady=8,
            width=12
        )
        fav_btn.pack(pady=5)
        
        self.create_tooltip(fav_btn, "Add to Favourites")
        
    def add_to_list(self, book, status):
        """Add a book to user's collection with specified status"""
        # Add book to database
        book_id = self.app.db.add_book(book)
        
        if book_id:
            success = self.app.db.add_user_book(self.user_id, book_id, status)
            if success:
                status_names = {
                    'currently_reading': 'Currently Reading',
                    'finished': 'Finished Books',
                    'favourite': 'Favourites'
                }
                messagebox.showinfo(
                    "Success",
                    f"'{book['title']}' added to {status_names[status]}!"
                )
            else:
                messagebox.showerror("Error", "Failed to add book to your collection")
        else:
            messagebox.showerror("Error", "Failed to save book information")

    
    def create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                font=("Helvetica", 9),
                bg="#2c3e50",
                fg="white",
                relief="flat",
                padx=8,
                pady=4
            )
            label.pack()
            
            # Store tooltip reference
            widget.tooltip = tooltip
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)