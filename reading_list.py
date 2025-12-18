"""
Currently Reading View
Displays books currently being read with progress tracking and reading calendar.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
from datetime import datetime
from reading_calendar import ReadingCalendar

class ReadingListFrame(tk.Frame):
    """Frame for displaying currently reading books with progress tracker"""
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
        
        self.books = []
        self.book_images = {}
        
        self.create_widgets()
        self.load_books()
        
    def create_widgets(self):
        """Create the currently reading interface"""
        # Main container
        main_container = tk.Frame(self, bg=self.CREAM)
        main_container.pack(fill="both", expand=True)
        
        # Left side - Books list
        left_frame = tk.Frame(main_container, bg=self.CREAM)
        left_frame.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=20)
        
        # Header
        header = tk.Frame(left_frame, bg=self.LIGHT_BROWN, height=80)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Currently Reading",
            font=("Helvetica", 24, "bold"),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(side="left", padx=20, pady=20)
        
        # Books container with scrollbar
        books_container = tk.Frame(left_frame, bg=self.LIGHT_BROWN)
        books_container.pack(fill="both", expand=True)
        
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
        
        # Right side - Calendar
        right_frame = tk.Frame(main_container, bg="#f5f5f5", width=350)
        right_frame.pack(side="right", fill="y", padx=(10, 20), pady=20)
        right_frame.pack_propagate(False)
        
        # Calendar widget
        self.calendar = ReadingCalendar(right_frame, self.app, self.user_id)
        
    def load_books(self):
        """Load currently reading books from database"""
        self.books = self.app.db.get_user_books(self.user_id, 'currently_reading')
        self.display_books()
        
    def display_books(self):
        """Display the books in the frame"""
        for widget in self.books_frame.winfo_children():
            widget.destroy()
            
        if not self.books:
            tk.Label(
                self.books_frame,
                text="No books currently reading.\nAdd some from the search page!",
                font=("Helvetica", 14),
                bg=self.LIGHT_BROWN,
                fg=self.CREAM
            ).pack(pady=50, padx=285)
            return
            
        for book in self.books:
            self.create_book_card(book)
            
    def create_book_card(self, book):
        """Create a detailed card for a currently reading book"""
        card = tk.Frame(self.books_frame, bg=self.MEDIUM_BROWN, relief="flat")
        card.pack(fill="x", padx=10, pady=10)
        
        content = tk.Frame(card, bg=self.MEDIUM_BROWN)
        content.pack(fill="x", padx=20, pady=20)
        
        # Top section with cover and info
        top_section = tk.Frame(content, bg=self.MEDIUM_BROWN)
        top_section.pack(fill="x", pady=(0, 15))
        
        # Book cover
        cover_frame = tk.Frame(top_section, bg=self.MEDIUM_BROWN)
        cover_frame.pack(side="left", padx=(0, 20))
        
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
                    self.book_images[book['book_id']] = photo
                    cover_label.config(image=photo, text="")
                except:
                    pass
            threading.Thread(target=load_image, daemon=True).start()
        
        # Book info
        info_frame = tk.Frame(top_section, bg=self.MEDIUM_BROWN)
        info_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            info_frame,
            text=book['title'],
            font=("Helvetica", 16, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM,
            anchor="w",
            wraplength=400
        ).pack(fill="x")
        
        tk.Label(
            info_frame,
            text=f"by {book['authors']}",
            font=("Helvetica", 12),
            bg=self.MEDIUM_BROWN,
            fg=self.ACCENT_BROWN,
            anchor="w"
        ).pack(fill="x", pady=(5, 10))
        
        if book['page_count']:
            tk.Label(
                info_frame,
                text=f"Total Pages: {book['page_count']}",
                font=("Helvetica", 10),
                bg=self.MEDIUM_BROWN,
                fg=self.ACCENT_BROWN,
                anchor="w"
            ).pack(fill="x")
        
        # Progress section
        progress_section = tk.Frame(content, bg=self.MEDIUM_BROWN)
        progress_section.pack(fill="x", pady=(15, 0))

        # Get initial values
        current_page = book['current_page'] or 0
        total_pages = book['page_count'] or 1
        progress_pct = int((current_page / total_pages) * 100) if total_pages > 0 else 0

        # Progress label (will update dynamically)
        progress_label = tk.Label(
            progress_section,
            text=f"Progress: {current_page} / {total_pages} pages ({progress_pct}%)",
            font=("Helvetica", 11, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM
        )
        progress_label.pack(anchor="w", pady=(0, 10))

        # Progress slider
        slider_frame = tk.Frame(progress_section, bg=self.MEDIUM_BROWN)
        slider_frame.pack(fill="x", pady=(0, 15))

        progress_var = tk.IntVar(value=current_page)

        # Function to update progress label as slider moves
        def update_progress_display(value):
            """Update the progress label in real-time as slider moves"""
            try:
                current = int(float(value))
                percentage = int((current / total_pages) * 100) if total_pages > 0 else 0
                progress_label.config(
                text=f"Progress: {current} / {total_pages} pages ({percentage}%)"
            )
            except:
                pass

        slider = tk.Scale(
            slider_frame,
            from_=0,
            to=total_pages if total_pages > 0 else 100,
            orient="horizontal",
            variable=progress_var,
            bg="white",
            fg="#2c3e50",
            font=("Helvetica", 10),
            highlightthickness=0,
            troughcolor="#ecf0f1",
            activebackground=self.CREAM,
            showvalue=False,
            length=400,
            command=update_progress_display  # ← ADD THIS: Updates label as you slide
        )
        slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Update button
        update_btn = tk.Button(
            slider_frame,
            text="Update",
            font=("Helvetica", 10),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda: self.update_progress(book['user_book_id'], progress_var.get(), book),
            padx=20,
            pady=5
        )
        update_btn.pack(side="right")
        
        # Action buttons with better layout
        action_frame = tk.Frame(content, bg=self.MEDIUM_BROWN)
        action_frame.pack(fill="x", pady=(10, 0))
        
        # Left side buttons
        left_buttons = tk.Frame(action_frame, bg=self.MEDIUM_BROWN)
        left_buttons.pack(side="left")
        
        # Mark as Finished button with icon
        finished_btn = tk.Button(
            left_buttons,
            text="Mark as Finished",
            font=("Helvetica", 10),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda: self.mark_as_finished(book),
            padx=15,
            pady=8
        )
        finished_btn.pack(side="left", padx=(0, 10))
        
        # Add hover effect
        finished_btn.bind("<Enter>", lambda e: finished_btn.config(bg=self.DARK_BROWN))
        finished_btn.bind("<Leave>", lambda e: finished_btn.config(bg=self.DARK_BROWN))
        
        # Add to Favourites button
        fav_btn = tk.Button(
            left_buttons,
            text="Add to Favourites",
            font=("Helvetica", 10),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda: self.add_to_favourites(book),
            padx=15,
            pady=8
        )
        fav_btn.pack(side="left")
        
        # Add hover effect
        fav_btn.bind("<Enter>", lambda e: fav_btn.config(bg=self.DARK_BROWN))
        fav_btn.bind("<Leave>", lambda e: fav_btn.config(bg=self.DARK_BROWN))
        
        # Right side buttons
        right_buttons = tk.Frame(action_frame, bg="white")
        right_buttons.pack(side="right")
        
        # Remove button
        remove_btn = tk.Button(
            right_buttons,
            text="Remove",
            font=("Helvetica", 10),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda: self.remove_book(book['user_book_id']),
            padx=15,
            pady=8
        )
        remove_btn.pack(side="left")
        
        # Add hover effect
        remove_btn.bind("<Enter>", lambda e: remove_btn.config(bg=self.DARK_BROWN))
        remove_btn.bind("<Leave>", lambda e: remove_btn.config(bg=self.DARK_BROWN))
        
    def update_progress(self, user_book_id, current_page, book):
        """Update reading progress and add to reading streak"""
        if self.app.db.update_book_progress(user_book_id, current_page):
            # Add today to reading streak
            today = datetime.now().strftime('%Y-%m-%d')
            self.app.db.add_reading_streak(self.user_id, today, 1)
            
            # Refresh calendar
            self.calendar.load_streaks()
            
            # Show success message
            tk.messagebox.showinfo("Success", f"Progress updated to page {current_page}!")
            
            # Reload books to show updated progress
            self.load_books()
        else:
            tk.messagebox.showerror("Error", "Failed to update progress")
            
    def mark_as_finished(self, book):
        """Move book to finished list"""
        # Remove from currently reading
        self.app.db.remove_user_book(book['user_book_id'])
        
        # Add to finished
        self.app.db.add_user_book(self.user_id, book['book_id'], 'finished')
        
        tk.messagebox.showinfo("Success", f"'{book['title']}' moved to Finished Books!")
        self.load_books()
        
    def remove_book(self, user_book_id):
        """Remove book from currently reading"""
        if tk.messagebox.askyesno("Confirm", "Remove this book from your reading list?"):
            if self.app.db.remove_user_book(user_book_id):
                tk.messagebox.showinfo("Success", "Book removed!")
                self.load_books()
            else:
                tk.messagebox.showerror("Error", "Failed to remove book")

    def add_to_favourites(self, book):
        """Add book to favourites list"""
        if self.app.db.add_user_book(self.user_id, book['book_id'], 'favourite'):
            tk.messagebox.showinfo(
                "Success",
                f"'{book['title']}' added to Favourites!"
            )
        else:
            tk.messagebox.showinfo(
                "Note",
                "This book is already in your favourites!"
            )