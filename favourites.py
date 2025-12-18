"""
Favourites View
Displays favourite books with covers in a grid layout.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

class FavouritesFrame(tk.Frame):
    """Frame for displaying favourite books"""

    DARK_BROWN = "#3E2723"
    MEDIUM_BROWN = "#5D4037"
    LIGHT_BROWN = "#8D6E63"
    ACCENT_BROWN = "#A1887F"
    CREAM = "#EFEBE9"
    
    def __init__(self, parent, app, user_id):
        super().__init__(parent, bg=self.CREAM)
        self.app = app
        self.user_id = user_id
        self.pack(fill="both", expand=True)
        
        self.books = []
        self.book_images = {}
        
        self.create_widgets()
        self.load_books()
        
    def create_widgets(self):
        """Create the favourites interface"""
        # Header
        header = tk.Frame(self, bg=self.LIGHT_BROWN, height=100)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.LIGHT_BROWN)
        header_content.pack(fill="both", expand=True, padx=20)
        
        tk.Label(
            header_content,
            text="Favorite Books",
            font=("Helvetica", 24, "bold"),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(side="left", pady=20)
        
        self.count_label = tk.Label(
            header_content,
            text="0 books",
            font=("Helvetica", 14),
            bg=self.LIGHT_BROWN,
            fg=self.DARK_BROWN
        )
        self.count_label.pack(side="right", pady=20)
        
        # Books container with scrollbar
        books_container = tk.Frame(self, bg=self.LIGHT_BROWN)
        books_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        canvas = tk.Canvas(books_container, bg=self.LIGHT_BROWN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(books_container, orient="vertical", command=canvas.yview)
        
        self.books_frame = tk.Frame(canvas, bg=self.LIGHT_BROWN)
        
        self.books_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.books_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
    def load_books(self):
        """Load favourite books from database"""
        self.books = self.app.db.get_user_books(self.user_id, 'favourite')
        self.count_label.config(text=f"{len(self.books)} books")
        self.display_books()
        
    def display_books(self):
        """Display the books in a grid layout"""
        for widget in self.books_frame.winfo_children():
            widget.destroy()
            
        if not self.books:
            tk.Label(
                self.books_frame,
                text="No favorite books yet.\nAdd some from the search page!",
                font=("Helvetica", 14),
                bg=self.LIGHT_BROWN,
                fg=self.CREAM
            ).pack(pady=50, padx=450)
            return
            
        # Create grid of books
        row = 0
        col = 0
        max_cols = 4
        
        for book in self.books:
            self.create_book_card(book, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def create_book_card(self, book, row, col):
        """Create a card widget for a favourite book"""
        card = tk.Frame(self.books_frame, bg=self.MEDIUM_BROWN, relief="flat", width=200, height=350)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        card.grid_propagate(False)
        
        # Favourite star badge
        """badge = tk.Label(
            card,
            text="",
            font=("Helvetica", 20),
            bg="white"
        )
        badge.place(x=10, y=10)"""
        
        # Book cover
        cover_frame = tk.Frame(card, bg=self.DARK_BROWN)
        cover_frame.pack(pady=(15, 10))
        
        cover_label = tk.Label(
            cover_frame,
            bg=self.MEDIUM_BROWN,
            text="📚",
            font=("Helvetica", 50)
        )
        cover_label.pack()
        
        if book['cover_url']:
            def load_image():
                try:
                    response = requests.get(book['cover_url'], timeout=5)
                    img_data = response.content
                    img = Image.open(BytesIO(img_data))
                    img = img.resize((130, 180), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.book_images[book['book_id']] = photo
                    cover_label.config(image=photo, text="")
                except:
                    pass
            threading.Thread(target=load_image, daemon=True).start()
        
        # Book info
        info_frame = tk.Frame(card, bg=self.MEDIUM_BROWN)
        info_frame.pack(fill="x", padx=15)
        
        # Title (truncated)
        title_text = book['title'][:50] + ('...' if len(book['title']) > 50 else '')
        tk.Label(
            info_frame,
            text=title_text,
            font=("Helvetica", 11, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM,
            wraplength=170,
            justify="center"
        ).pack(pady=(0, 5))
        
        # Author (truncated)
        author_text = book['authors'][:40] + ('...' if len(book['authors']) > 40 else '')
        tk.Label(
            info_frame,
            text=author_text,
            font=("Helvetica", 9),
            bg=self.MEDIUM_BROWN,
            fg=self.ACCENT_BROWN,
            wraplength=170,
            justify="center"
        ).pack(pady=(0, 10))
        
        # Additional info
        if book['page_count']:
            tk.Label(
                info_frame,
                text=f"{book['page_count']} pages",
                font=("Helvetica", 8),
                bg=self.MEDIUM_BROWN,
                fg=self.ACCENT_BROWN
            ).pack()
        
        # Action buttons
        btn_frame = tk.Frame(card, bg=self.MEDIUM_BROWN)
        btn_frame.pack(side="bottom", pady=15)
        
        # Add to Reading button
        reading_btn = tk.Button(
            btn_frame,
            text="Read",
            font=("Helvetica", 9),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda b=book: self.add_to_reading(b),
            padx=10,
            pady=5
        )
        reading_btn.pack(side="left", padx=2)
        
        # Remove button
        remove_btn = tk.Button(
            btn_frame,
            text="✕",
            font=("Helvetica", 9),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda: self.remove_book(book['user_book_id']),
            padx=8,
            pady=5
        )
        remove_btn.pack(side="left", padx=2)
        
    def add_to_reading(self, book):
        """Add book to currently reading list"""
        # Add to currently reading (will create duplicate entry with different status)
        if self.app.db.add_user_book(self.user_id, book['book_id'], 'currently_reading'):
            messagebox.showinfo(
                "Success",
                f"'{book['title']}' added to Currently Reading!"
            )
        else:
            messagebox.showinfo(
                "Note",
                "This book is already in your currently reading list!"
            )
            
    def remove_book(self, user_book_id):
        """Remove book from favourites"""
        if messagebox.askyesno("Confirm", "Remove this book from favorites?"):
            if self.app.db.remove_user_book(user_book_id):
                messagebox.showinfo("Success", "Book removed from favorites!")
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to remove book")