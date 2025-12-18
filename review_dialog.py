import tkinter as tk
from tkinter import scrolledtext, messagebox

class ReviewDialog(tk.Toplevel):
    """Dialog window for creating/editing book reviews with delete functionality"""

    DARK_BROWN = "#3E2723"
    MEDIUM_BROWN = "#5D4037"
    LIGHT_BROWN = "#8D6E63"
    ACCENT_BROWN = "#A1887F"
    CREAM = "#EFEBE9"
    WHITE = "#f5f5f5"
    
    def __init__(self, parent, book, existing_review, save_callback, delete_callback=None):
        super().__init__(parent)
        
        self.book = book
        self.existing_review = existing_review
        self.save_callback = save_callback
        self.delete_callback = delete_callback
        self.selected_rating = existing_review['rating'] if existing_review else 0
        
        # Configure dialog
        self.title(f"Review: {book['title'][:50]}")
        self.geometry("500x750")  # Increased height for delete button
        self.configure(bg="white")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center dialog
        self.center_window()
        
        self.create_widgets()
        
    def center_window(self):
        """Center the dialog on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create the review dialog UI"""
        # Header
        header = tk.Frame(self, bg=self.MEDIUM_BROWN, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_text = "Edit Review" if self.existing_review else "Write a Review"
        tk.Label(
            header,
            text=header_text,
            font=("Helvetica", 18, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM
        ).pack(pady=25)
        
        # Content
        content = tk.Frame(self, bg="white")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Book title
        tk.Label(
            content,
            text=self.book['title'][:60] + ('...' if len(self.book['title']) > 60 else ''),
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg=self.DARK_BROWN,
            wraplength=440
        ).pack(pady=(0, 5))
        
        tk.Label(
            content,
            text=f"by {self.book['authors']}",
            font=("Helvetica", 10),
            bg="white",
            fg=self.MEDIUM_BROWN
        ).pack(pady=(0, 20))
        
        # Rating section
        rating_frame = tk.Frame(content, bg="white")
        rating_frame.pack(pady=(0, 20))
        
        tk.Label(
            rating_frame,
            text="Your Rating:",
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(pady=(0, 10))
        
        # Star rating buttons
        stars_frame = tk.Frame(rating_frame, bg="white")
        stars_frame.pack()
        
        self.star_buttons = []
        for i in range(1, 6):
            btn = tk.Button(
                stars_frame,
                text="☆",
                font=("Helvetica", 24),
                bg="white",
                fg=self.MEDIUM_BROWN,
                relief="flat",
                cursor="hand2",
                command=lambda r=i: self.set_rating(r),
                bd=0,
                padx=5
            )
            btn.pack(side="left", padx=2)
            self.star_buttons.append(btn)
            
            # Add hover effects
            btn.bind("<Enter>", lambda e, b=btn, r=i: self.preview_rating(r))
            btn.bind("<Leave>", lambda e: self.update_stars())
        
        # Update stars if editing existing review
        if self.selected_rating > 0:
            self.update_stars()
        
        # Review text section
        tk.Label(
            content,
            text="Your Review:",
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg=self.DARK_BROWN,
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        # Text area with character counter
        text_frame = tk.Frame(content, bg="white")
        text_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.review_text = scrolledtext.ScrolledText(
            text_frame,
            font=("Helvetica", 10),
            bg="#f8f9fa",
            fg="#2c3e50",
            relief="flat",
            wrap="word",
            height=7
        )
        self.review_text.pack(fill="both", expand=True)
        
        # Character counter
        self.char_count_label = tk.Label(
            text_frame,
            text="0 characters",
            font=("Helvetica", 8),
            bg="white",
            fg=self.MEDIUM_BROWN
        )
        self.char_count_label.pack(anchor="e", pady=(5, 0))
        
        # Bind text change event
        self.review_text.bind("<KeyRelease>", self.update_char_count)
        
        # Pre-fill existing review text
        if self.existing_review and self.existing_review['review_text']:
            self.review_text.insert("1.0", self.existing_review['review_text'])
            self.update_char_count()
        
        # Buttons frame
        button_frame = tk.Frame(content, bg="white")
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Left side - Delete button (only show if editing existing review)
        if self.existing_review and self.delete_callback:
            delete_btn = tk.Button(
                button_frame,
                text="Delete Review",
                font=("Helvetica", 9),
                bg=self.DARK_BROWN,
                fg=self.CREAM,
                relief="flat",
                cursor="hand2",
                command=self.delete_review,
                padx=20,
                pady=10
            )
            delete_btn.pack(side="left")
        
        # Right side - Cancel and Save buttons
        right_buttons = tk.Frame(button_frame, bg="white")
        right_buttons.pack(side="right")
        
        cancel_btn = tk.Button(
            right_buttons,
            text="Cancel",
            font=("Helvetica", 9),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.destroy,
            padx=20,
            pady=10
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = tk.Button(
            right_buttons,
            text="Save Review",
            font=("Helvetica", 9),
            bg=self.DARK_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=self.save_review,
            padx=20,
            pady=10
        )
        save_btn.pack(side="left")
        
    def set_rating(self, rating):
        """Set the star rating"""
        self.selected_rating = rating
        self.update_stars()
        
    def preview_rating(self, rating):
        """Preview rating on hover"""
        for i, btn in enumerate(self.star_buttons):
            if i < rating:
                btn.config(text="★", fg=self.DARK_BROWN)
            else:
                btn.config(text="☆", fg=self.DARK_BROWN)
        
    def update_stars(self):
        """Update star button appearances based on selected rating"""
        for i, btn in enumerate(self.star_buttons):
            if i < self.selected_rating:
                btn.config(text="★", fg=self.DARK_BROWN)
            else:
                btn.config(text="☆", fg=self.MEDIUM_BROWN)
                
    def update_char_count(self, event=None):
        """Update character count label"""
        text = self.review_text.get("1.0", "end-1c")
        char_count = len(text)
        self.char_count_label.config(text=f"{char_count} characters")
        
    def save_review(self):
        """Save the review"""
        if self.selected_rating == 0:
            messagebox.showwarning(
                "Rating Required",
                "Please select a star rating before saving.",
                parent=self
            )
            return
            
        review_text = self.review_text.get("1.0", "end-1c").strip()
        
        if not review_text:
            result = messagebox.askyesno(
                "Empty Review",
                "You haven't written any review text. Save with just a rating?",
                parent=self
            )
            if not result:
                return
        
        # Call the save callback
        success = self.save_callback(
            self.book['book_id'],
            self.selected_rating,
            review_text
        )
        
        if success:
            self.destroy()
            
    def delete_review(self):
        """Delete the review"""
        result = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this review? This cannot be undone.",
            parent=self
        )
        
        if result and self.delete_callback:
            success = self.delete_callback(self.book['book_id'])
            if success:
                self.destroy()
