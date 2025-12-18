"""
Finished Books View
Displays finished books with covers and review functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
from review_dialog import ReviewDialog

class FinishedBooksFrame(tk.Frame):
    """Frame for displaying finished books"""
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
        """Create the finished books interface"""
        # Header
        header = tk.Frame(self, bg=self.LIGHT_BROWN, height=100)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.LIGHT_BROWN)
        header_content.pack(fill="both", expand=True, padx=20)
        
        tk.Label(
            header_content,
            text="Finished Books",
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
        """Load finished books from database"""
        self.books = self.app.db.get_user_books(self.user_id, 'finished')
        self.count_label.config(text=f"{len(self.books)} books")
        self.display_books()
        
    def display_books(self):
        """Display the books in a grid layout"""
        for widget in self.books_frame.winfo_children():
            widget.destroy()
            
        if not self.books:
            tk.Label(
                self.books_frame,
                text="No finished books yet.\nMark books as finished from your reading list!",
                font=("Helvetica", 14),
                bg=self.LIGHT_BROWN,
                fg=self.CREAM
            ).pack(pady=50, padx=430)
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
        """Create a card widget for a finished book"""
        card = tk.Frame(self.books_frame, bg=self.MEDIUM_BROWN, relief="flat", width=200, height=350)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        card.grid_propagate(False)
        
        # Book cover
        cover_frame = tk.Frame(card, bg=self.MEDIUM_BROWN)
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
        
        # Check if book has a review
        review = self.app.db.get_review(self.user_id, book['book_id'])
        
        if review:
            # Display rating stars
            stars = "⭐" * review['rating']
            tk.Label(
                info_frame,
                text=stars,
                font=("Helvetica", 12),
                bg=self.MEDIUM_BROWN,
                fg=self.DARK_BROWN
            ).pack(pady=(0, 5))
        
        # Action button
        btn_frame = tk.Frame(card, bg=self.MEDIUM_BROWN)
        btn_frame.pack(side="bottom", pady=15)
        
        # Check if book has a review
        review = self.app.db.get_review(self.user_id, book['book_id'])
        
        # Review button - Changes based on whether review exists
        if review:
            # Edit Review button (green when review exists)
            review_btn = tk.Button(
                btn_frame,
                text="Edit",
                font=("Helvetica", 9),
                bg=self.DARK_BROWN,
                fg=self.CREAM,
                relief="flat",
                cursor="hand2",
                command=lambda b=book: self.open_review_dialog(b),
                padx=12,
                pady=5
            )
            review_btn.pack(side="left", padx=2)
            
            # View Review button
            view_btn = tk.Button(
                btn_frame,
                text="View",
                font=("Helvetica", 9),
                bg=self.DARK_BROWN,
                fg=self.CREAM,
                relief="flat",
                cursor="hand2",
                command=lambda b=book, r=review: self.view_review_details(b, r),
                padx=8,
                pady=5
            )
            view_btn.pack(side="left", padx=2)
        else:
            # Add Review button (blue when no review)
            review_btn = tk.Button(
                btn_frame,
                text="Review",
                font=("Helvetica", 9),
                bg=self.DARK_BROWN,
                fg=self.CREAM,
                relief="flat",
                cursor="hand2",
                command=lambda b=book: self.open_review_dialog(b),
                padx=10,
                pady=5
            )
            review_btn.pack(side="left", padx=2)
        
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
        
    def open_review_dialog(self, book):
        """Open dialog to add/edit book review"""
        # Get existing review if any
        existing_review = self.app.db.get_review(self.user_id, book['book_id'])
        
        dialog = ReviewDialog(
            self,
            book,
            existing_review,
            self.save_review,
            self.delete_review
        )
        
    def save_review(self, book_id, rating, review_text):
        """Save book review to database"""
        if self.app.db.add_review(self.user_id, book_id, rating, review_text):
            messagebox.showinfo("Success", "Review saved successfully!")
            self.load_books()  # Reload to show updated review
            return True
        else:
            messagebox.showerror("Error", "Failed to save review")
            return False
        
    def delete_review(self, book_id):
        """Delete book review from database"""
        if self.app.db.delete_review(self.user_id, book_id):
            messagebox.showinfo("Success", "Review deleted successfully!")
            self.load_books()  # Reload to remove review display
            return True
        else:
            messagebox.showerror("Error", "Failed to delete review")
            return False
        
    def view_review_details(self, book, review):
        """Display a popup with full review details"""
        # Create a new toplevel window
        detail_window = tk.Toplevel(self)
        detail_window.title(f"Review: {book['title'][:40]}")
        detail_window.geometry("450x650")
        detail_window.configure(bg="white")
        detail_window.resizable(False, False)
        
        # Make it modal
        detail_window.transient(self)
        detail_window.grab_set()
        
        # Center the window
        detail_window.update_idletasks()
        x = (detail_window.winfo_screenwidth() // 2) - (225)
        y = (detail_window.winfo_screenheight() // 2) - (200)
        detail_window.geometry(f'450x650+{x}+{y}')
        
        # Header with book title
        header = tk.Frame(detail_window, bg=self.MEDIUM_BROWN, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Review Details",
            font=("Helvetica", 16, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM
        ).pack(pady=25)
        
        # Content
        content = tk.Frame(detail_window, bg="white")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Book title
        tk.Label(
            content,
            text=book['title'],
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg=self.DARK_BROWN,
            wraplength=390
        ).pack(pady=(0, 5))
        
        # Author
        tk.Label(
            content,
            text=f"by {book['authors']}",
            font=("Helvetica", 10),
            bg="white",
            fg=self.MEDIUM_BROWN
        ).pack(pady=(0, 20))
        
        # Rating with stars
        rating_frame = tk.Frame(content, bg="white")
        rating_frame.pack(pady=(0, 15))
        
        tk.Label(
            rating_frame,
            text="Your Rating:",
            font=("Helvetica", 10, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(side="left", padx=(0, 10))
        
        # Display stars
        stars = "★" * review['rating'] + "☆" * (5 - review['rating'])
        tk.Label(
            rating_frame,
            text=stars,
            font=("Helvetica", 16),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(side="left")
        
        tk.Label(
            rating_frame,
            text=f"({review['rating']}/5)",
            font=("Helvetica", 10),
            bg="white",
            fg=self.MEDIUM_BROWN
        ).pack(side="left", padx=(5, 0))
        
        # Review text label
        tk.Label(
            content,
            text="Your Review:",
            font=("Helvetica", 10, "bold"),
            bg="white",
            fg=self.DARK_BROWN,
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        # Review text in a frame with border
        text_container = tk.Frame(content, bg="#ecf0f1", relief="flat")
        text_container.pack(fill="both", expand=True, pady=(0, 15))
        
        # Scrollable text widget
        from tkinter import scrolledtext
        review_display = scrolledtext.ScrolledText(
            text_container,
            font=("Helvetica", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            relief="flat",
            wrap="word",
            height=8,
            padx=10,
            pady=10
        )
        review_display.pack(fill="both", expand=True)
        
        # Insert review text
        if review['review_text']:
            review_display.insert("1.0", review['review_text'])
        else:
            review_display.insert("1.0", "(No review text provided)")
            review_display.config(fg="#95a5a6")
        
        # Make text read-only
        review_display.config(state="disabled")
        
        # Review date
        if review.get('updated_at'):
            date_str = review['updated_at'].strftime('%B %d, %Y at %I:%M %p')
            tk.Label(
                content,
                text=f"Last updated: {date_str}",
                font=("Helvetica", 8),
                bg="white",
                fg="#95a5a6"
            ).pack(pady=(5, 10))
        
        # Action buttons
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        # Edit button
        edit_btn = tk.Button(
            btn_frame,
            text="Edit Review",
            font=("Helvetica", 9),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda: [detail_window.destroy(), self.open_review_dialog(book)],
            padx=20,
            pady=8
        )
        edit_btn.pack(side="left")
        
        # Delete button
        delete_btn = tk.Button(
            btn_frame,
            text="Delete",
            font=("Helvetica", 9),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda: self.delete_from_detail_view(book['book_id'], detail_window),
            padx=20,
            pady=8
        )
        delete_btn.pack(side="left", padx=(10, 0))
        
        # Close button
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            font=("Helvetica", 9),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=detail_window.destroy,
            padx=20,
            pady=8
        )
        close_btn.pack(side="right")

    """
    ADD this helper method after view_review_details():
    """

    def delete_from_detail_view(self, book_id, detail_window):
        """Delete review from the detail view popup"""
        if self.delete_review(book_id):
            detail_window.destroy()
            
    def remove_book(self, user_book_id):
        """Remove book from finished list"""
        if messagebox.askyesno("Confirm", "Remove this book from finished list?"):
            if self.app.db.remove_user_book(user_book_id):
                messagebox.showinfo("Success", "Book removed!")
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to remove book")