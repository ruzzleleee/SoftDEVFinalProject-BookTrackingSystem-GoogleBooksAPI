"""
Authentication Page for Book Tracking Application
Handles user registration and login with modern UI design.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import re  # For email validation

class AuthPage(tk.Frame):
    """Authentication page with login and registration functionality"""
    
    DARK_BROWN = "#3E2723"
    MEDIUM_BROWN = "#5D4037"
    LIGHT_BROWN = "#8D6E63"
    ACCENT_BROWN = "#A1887F"
    CREAM = "#EFEBE9"

    def __init__(self, parent, app):
        super().__init__(parent, bg=self.DARK_BROWN)
        self.app = app
        self.pack(fill="both", expand=True)
        
        # Track which form is showing
        self.showing_login = True
        
        self.create_widgets()

    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle on canvas"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def forgot_password(self):
        """Handle forgot password functionality"""
        # Create a custom dialog for username and email
        dialog = tk.Toplevel(self)
        dialog.title("Forgot Password")
        dialog.geometry("400x300")
        dialog.configure(bg="white")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 150
        dialog.geometry(f'400x345+{x}+{y}')
        
        # Header
        header = tk.Frame(dialog, bg=self.MEDIUM_BROWN, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Forgot Password",
            font=("Helvetica", 16, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM
        ).pack(pady=15)
        
        # Content
        content = tk.Frame(dialog, bg="white")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        tk.Label(
            content,
            text="Enter your username and email to reset password",
            font=("Helvetica", 10),
            bg="white",
            fg="#7f8c8d",
            wraplength=340
        ).pack(pady=(0, 20))
        
        # Username field
        tk.Label(
            content,
            text="Username:",
            font=("Helvetica", 10, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(anchor="w")
        
        username_entry = tk.Entry(
            content,
            font=("Helvetica", 11),
            bg="#f8f9fa",
            relief="flat"
        )
        username_entry.pack(fill="x", pady=(5, 15), ipady=8)
        
        # Email field
        tk.Label(
            content,
            text="Email:",
            font=("Helvetica", 10, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(anchor="w")
        
        email_entry = tk.Entry(
            content,
            font=("Helvetica", 11),
            bg="#f8f9fa",
            relief="flat"
        )
        email_entry.pack(fill="x", pady=(5, 20), ipady=8)
        
        # Buttons frame
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x")
        
        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Helvetica", 9),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=dialog.destroy,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side="left")
        
        # Submit button
        submit_btn = tk.Button(
            btn_frame,
            text="Reset Password",
            font=("Helvetica", 9, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=lambda: self.process_password_reset(
                username_entry.get().strip(),
                email_entry.get().strip(),
                dialog
            ),
            padx=20,
            pady=8
        )
        submit_btn.pack(side="right")

    def process_password_reset(self, username, email, dialog):
        """Process the password reset request"""
        if not username or not email:
            messagebox.showerror("Error", "Please fill in all fields", parent=dialog)
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address", parent=dialog)
            return
        
        # Verify username and email match in database
        try:
            cursor = self.app.db.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT user_id FROM users WHERE username = %s AND email = %s",
                (username, email)
            )
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                messagebox.showerror(
                    "Error",
                    "No account found with this username and email combination",
                    parent=dialog
                )
                return
            
            # Close the forgot password dialog
            dialog.destroy()
            
            # Open new password dialog
            self.create_new_password_dialog(user['user_id'], username)
            
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}", parent=dialog)

    def create_new_password_dialog(self, user_id, username):
        """Dialog to create new password"""
        dialog = tk.Toplevel(self)
        dialog.title("Create New Password")
        dialog.geometry("400x350")
        dialog.configure(bg="white")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 175
        dialog.geometry(f'400x395+{x}+{y}')
        
        # Header
        header = tk.Frame(dialog, bg=self.MEDIUM_BROWN, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Create New Password",
            font=("Helvetica", 16, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM
        ).pack(pady=15)
        
        # Content
        content = tk.Frame(dialog, bg="white")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        tk.Label(
            content,
            text=f"Creating new password for: {username}",
            font=("Helvetica", 10, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(pady=(0, 20))
        
        # New password field
        tk.Label(
            content,
            text="New Password:",
            font=("Helvetica", 10, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(anchor="w")

        # modified
        # New password container with show/hide button
        new_password_container = tk.Frame(content, bg="#f8f9fa")
        new_password_container.pack(fill="x", pady=(5, 15))
        
        new_password_entry = tk.Entry(
            new_password_container,
            font=("Helvetica", 11),
            bg="#f8f9fa",
            relief="flat",
            show="●",
            border=0
        )
        new_password_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(8, 0))

        # modified 
        # Show/Hide new password button
        new_password_visible = [False]  # Use list to avoid scope issues
        new_password_toggle_btn = tk.Button(
            new_password_container,
            text="👁",
            font=("Helvetica", 12),
            bg="#f8f9fa",
            fg=self.DARK_BROWN, 
            relief="flat", 
            cursor="hand2",
            command=lambda: self.toggle_dialog_password(
                new_password_entry, 
                new_password_toggle_btn, 
                new_password_visible
            ),
            bd=0,
            padx=8
        )
        new_password_toggle_btn.pack(side="right", ipady=8)
        
        # Confirm password field
        tk.Label(
            content,
            text="Confirm Password:",
            font=("Helvetica", 10, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(anchor="w")

        # modified
        # Confirm password container with show/hide button
        confirm_password_container = tk.Frame(content, bg="#f8f9fa")
        confirm_password_container.pack(fill="x", pady=(5, 15))
        
        confirm_password_entry = tk.Entry(
            confirm_password_container,
            font=("Helvetica", 11),
            bg="#f8f9fa",
            relief="flat",
            show="●",
            border=0
        )
        confirm_password_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(8, 0))

        # modified
        # Show/Hide confirm password button
        confirm_password_visible = [False]  # Use list to avoid scope issues
        confirm_password_toggle_btn = tk.Button(
            confirm_password_container,
            text="👁",
            font=("Helvetica", 12),
            bg="#f8f9fa",
            fg=self.DARK_BROWN,
            relief="flat",
            cursor="hand2",
            command=lambda: self.toggle_dialog_password(
                confirm_password_entry,
                confirm_password_toggle_btn,
                confirm_password_visible
            ),
            bd=0,
            padx=8
        )
        confirm_password_toggle_btn.pack(side="right", ipady=8)

        
        # Password requirements
        tk.Label(
            content,
            text="Password must be at least 6 characters",
            font=("Helvetica", 8),
            bg="white",
            fg="#95a5a6"
        ).pack(anchor="w", pady=(0, 20))
        
        # Buttons frame
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x")
        
        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Helvetica", 9),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=dialog.destroy,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side="left")
        
        # Save button
        save_btn = tk.Button(
            btn_frame,
            text="Save New Password",
            font=("Helvetica", 9, "bold"),
            bg="#5D4037",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=lambda: self.save_new_password(
                user_id,
                new_password_entry.get(),
                confirm_password_entry.get(),
                dialog
            ),
            padx=20,
            pady=8
        )
        save_btn.pack(side="right")

    def save_new_password(self, user_id, new_password, confirm_password, dialog):
        """Save the new password to database"""
        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields", parent=dialog)
            return
        
        if len(new_password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters", parent=dialog)
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match", parent=dialog)
            return
        
        # Update password in database
        try:
            cursor = self.app.db.connection.cursor()
            password_hash = self.app.db.hash_password(new_password)
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (password_hash, user_id)
            )
            self.app.db.connection.commit()
            cursor.close()
            
            dialog.destroy()
            messagebox.showinfo(
                "Success",
                "Password has been reset successfully!\nYou can now login with your new password."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update password: {e}", parent=dialog)
        
    def create_widgets(self):
        """Create the authentication page UI with rounded corners"""
        # Main container - TRANSPARENT BACKGROUND
        container = tk.Frame(self, bg=self.DARK_BROWN)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title - ON TRANSPARENT BACKGROUND
        title = tk.Label(
            container,
            text="📚 MyBookieee",
            font=("Helvetica", 32, "bold"),
            bg=self.DARK_BROWN,  # Changed from MEDIUM_BROWN to DARK_BROWN (transparent with page bg)
            fg=self.CREAM
        )
        title.pack(pady=(20, 5))
        
        subtitle = tk.Label(
            container,
            text="Your Personal Reading Companion",
            font=("Helvetica", 12),
            bg=self.DARK_BROWN,  # Changed from MEDIUM_BROWN to DARK_BROWN (transparent with page bg)
            fg=self.ACCENT_BROWN
        )
        subtitle.pack(pady=(10, 20))
        
        # Create canvas for rounded rectangle form
        form_width = 420
        form_height = 550
        
        canvas = tk.Canvas(
            container,
            width=form_width,
            height=form_height,
            bg=self.DARK_BROWN,
            highlightthickness=0
        )
        canvas.pack(padx=40, pady=20)
        
        # Draw rounded rectangle
        self.create_rounded_rectangle(
            canvas,
            0, 0,
            form_width, form_height,
            radius=20,
            fill=self.LIGHT_BROWN,
            outline=""
        )
        
        # Form frame inside canvas - with rounded effect
        self.form_frame = tk.Frame(canvas, bg=self.LIGHT_BROWN)
        canvas.create_window(form_width//2, form_height//2, window=self.form_frame)
        
        # Form title
        self.form_title = tk.Label(
            self.form_frame,
            text="Welcome Back",
            font=("Helvetica", 20, "bold"),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        )
        self.form_title.pack(pady=(30, 20))
        
        # Username field
        username_frame = tk.Frame(self.form_frame, bg=self.LIGHT_BROWN)
        username_frame.pack(pady=10, padx=40)
        
        tk.Label(
            username_frame,
            text="Username",
            font=("Helvetica", 10),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(anchor="w")
        
        self.username_entry = tk.Entry(
            username_frame,
            font=("Helvetica", 12),
            bg=self.CREAM,
            relief="flat",
            width=30,
        )
        self.username_entry.pack(pady=(5, 0), ipady=8)
        
        
        
        # modified
        # Password field
        password_frame = tk.Frame(self.form_frame, bg=self.LIGHT_BROWN)
        password_frame.pack(pady=10, padx=40)
        
        tk.Label(
            password_frame,
            text="Password",
            font=("Helvetica", 10),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(anchor="w")

        # modified
        # Password entry container with show/hide button
        password_container = tk.Frame(password_frame, bg=self.CREAM)
        password_container.pack(pady=(5, 0), fill="x")
        
        self.password_entry = tk.Entry(
            password_container,
            font=("Helvetica", 12),
            bg=self.CREAM,
            relief="flat",
            width=25,
            show="●",
            border=0
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(8,0))

        # modified
        # Show/Hide password button
        self.password_visible = False
        self.password_toggle_btn = tk.Button(
            password_container,
            text="👁",
            font=("Helvetica", 11),
            bg=self.CREAM,
            fg=self.DARK_BROWN,
            relief="flat",
            cursor="hand2",
            command=self.toggle_password_visibility,
            bd=0,
            padx=8
        )
        self.password_toggle_btn.pack(side="right", ipady=8)

        
        # Forgot Password link
        self.forgot_password_btn = tk.Button(
            password_frame,
            text="Forgot Password?",
            font=("Helvetica", 9, "underline"),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=self.forgot_password,
            bd=0,
            activebackground=self.LIGHT_BROWN,
            activeforeground=self.CREAM
        )
        self.forgot_password_btn.pack(anchor="e", pady=(5, 0))
        
        # Email field (for registration, initially hidden)
        self.email_frame = tk.Frame(self.form_frame, bg=self.LIGHT_BROWN)
        
        tk.Label(
            self.email_frame,
            text="Email",
            font=("Helvetica", 10),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(anchor="w")
        
        self.email_entry = tk.Entry(
            self.email_frame,
            font=("Helvetica", 12),
            bg=self.CREAM,
            relief="flat",
            width=30
        )
        self.email_entry.pack(pady=(5, 0), ipady=8)


        # Confirm Password field (for registration, initially hidden)
        self.confirm_password_frame = tk.Frame(self.form_frame, bg=self.LIGHT_BROWN)

        tk.Label(
            self.confirm_password_frame,
            text="Confirm Password",
            font=("Helvetica", 10),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(anchor="w")

        # Confirm password entry container with show/hide button
        confirm_password_container = tk.Frame(self.confirm_password_frame, bg=self.CREAM)
        confirm_password_container.pack(pady=(5, 0), fill="x")

        self.confirm_password_entry = tk.Entry(
            confirm_password_container,
            font=("Helvetica", 12),
            bg=self.CREAM,
            relief="flat",
            width=25,
            show="●",
            border=0
        )
        self.confirm_password_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(8,0))

        # Show/Hide confirm password button
        self.confirm_password_visible = False
        self.confirm_password_toggle_btn = tk.Button(
            confirm_password_container,
            text="👁",
            font=("Helvetica", 11),
            bg=self.CREAM,
            fg=self.DARK_BROWN,
            relief="flat",
            cursor="hand2",
            command=self.toggle_confirm_password_visibility,
            bd=0,
            padx=8
        )
        self.confirm_password_toggle_btn.pack(side="right", ipady=8)

        # Submit button
        self.submit_btn = tk.Button(
            self.form_frame,
            text="Login",
            font=("Helvetica", 12, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM,
            relief="flat",
            cursor="hand2",
            command=self.handle_submit,
            padx=40,
            pady=10
        )
        self.submit_btn.pack(pady=(20, 10))
        
        # Toggle button
        self.toggle_frame = tk.Frame(self.form_frame, bg=self.LIGHT_BROWN)
        self.toggle_frame.pack(pady=(10, 30))
        
        tk.Label(
            self.toggle_frame,
            text="Don't have an account?",
            font=("Helvetica", 10),
            bg=self.LIGHT_BROWN,
            fg=self.CREAM
        ).pack(side="left")
        
        self.toggle_btn = tk.Button(
            self.toggle_frame,
            text="Register",
            font=("Helvetica", 10, "bold"),
            bg=self.LIGHT_BROWN,
            fg=self.MEDIUM_BROWN,
            relief="flat",
            cursor="hand2",
            command=self.toggle_form,
            bd=0
        )
        self.toggle_btn.pack(side="left", padx=(5, 0))
        
        # Bind Enter key to submit
        self.username_entry.bind("<Return>", lambda e: self.handle_submit())
        self.email_entry.bind("<Return>", lambda e: self.handle_submit())
        self.password_entry.bind("<Return>", lambda e: self.handle_submit())
        self.confirm_password_entry.bind("<Return>", lambda e: self.handle_submit())

    # modified
    def toggle_password_visibility(self):
        """Toggle password visibility between shown and hidden"""
        self.password_visible = not self.password_visible
    
        if self.password_visible:
            # Show password
            self.password_entry.config(show="")
            self.password_toggle_btn.config(text="🙈")  # Monkey covering eyes
        else:
            # Hide password
            self.password_entry.config(show="●")
            self.password_toggle_btn.config(text="👁")  # Eye icon

    # confirm password toggle
    def toggle_confirm_password_visibility(self):
        """Toggle confirm password visibility between shown and hidden"""
        self.confirm_password_visible = not self.confirm_password_visible

        if self.confirm_password_visible:
            # Show password
            self.confirm_password_entry.config(show="")
            self.confirm_password_toggle_btn.config(text="🙈")  # Monkey covering eyes
        else:
            # Hide password
            self.confirm_password_entry.config(show="●")
            self.confirm_password_toggle_btn.config(text="👁")

    # modified
    def toggle_dialog_password(self, entry_widget, button_widget, visible_state):
        """Toggle password visibility in dialog windows"""
        visible_state[0] = not visible_state[0]
    
        if visible_state[0]:
            # Show password
            entry_widget.config(show="")
            button_widget.config(text="🙈")  # Monkey covering eyes
        else:
            # Hide password
            entry_widget.config(show="●")
            button_widget.config(text="👁")  # Eye icon
        
    def toggle_form(self):
        """Switch between login and registration forms"""
        self.showing_login = not self.showing_login
        
        if self.showing_login:
            # Switch to login
            self.form_title.config(text="Welcome Back")
            self.submit_btn.config(text="Login")

            self.email_frame.pack_forget()
            # added confirm pass
            self.confirm_password_frame.pack_forget()

            # Show forgot password button (added)
            self.forgot_password_btn.pack(anchor="e", pady=(5, 0))

            self.toggle_frame.pack_forget()
            self.toggle_frame = tk.Frame(self.form_frame, bg=self.LIGHT_BROWN)
            self.toggle_frame.pack(pady=(10, 30))
            
            tk.Label(
                self.toggle_frame,
                text="Don't have an account?",
                font=("Helvetica", 10),
                bg=self.LIGHT_BROWN,
                fg=self.CREAM
            ).pack(side="left")
            
            self.toggle_btn = tk.Button(
                self.toggle_frame,
                text="Register",
                font=("Helvetica", 10, "bold"),
                bg=self.LIGHT_BROWN,
                fg=self.MEDIUM_BROWN,
                relief="flat",
                cursor="hand2",
                command=self.toggle_form,
                bd=0
            )
            self.toggle_btn.pack(side="left", padx=(5, 0))
        else:
            # Switch to registration
            self.form_title.config(text="Create Account")
            self.submit_btn.config(text="Register")

            # Hide forgot password button in registration mode (added)
            self.forgot_password_btn.pack_forget()
            
            # Get the password_frame reference (parent of password_entry container)
            password_frame = self.password_entry.master.master
            password_frame.pack_forget()

            self.email_frame.pack(pady=10, padx=40, before=self.submit_btn)
            
            #added
            password_frame.pack(pady=10, padx=40, before=self.submit_btn)

            #added
            self.confirm_password_frame.pack(pady=10, padx=40, before=self.submit_btn)

            self.toggle_frame.pack_forget()
            self.toggle_frame = tk.Frame(self.form_frame, bg=self.LIGHT_BROWN)
            self.toggle_frame.pack(pady=(10, 30))
            
            tk.Label(
                self.toggle_frame,
                text="Already have an account?",
                font=("Helvetica", 10),
                bg=self.LIGHT_BROWN,
                fg=self.CREAM
            ).pack(side="left")
            
            self.toggle_btn = tk.Button(
                self.toggle_frame,
                text="Login",
                font=("Helvetica", 10, "bold"),
                bg=self.LIGHT_BROWN,
                fg=self.MEDIUM_BROWN,
                relief="flat",
                cursor="hand2",
                command=self.toggle_form,
                bd=0
            )
            self.toggle_btn.pack(side="left", padx=(5, 0))
            
        # Clear fields
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        # added
        self.confirm_password_entry.delete(0, tk.END)
        
    def handle_submit(self):
        """Handle form submission for login or registration"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
            
        if self.showing_login:
            # Handle login
            success, user_id, message = self.app.db.login_user(username, password)
            if success:
                self.app.show_main_dashboard(user_id)
            else:
                messagebox.showerror("Login Failed", message)
        else:
            # Handle registration
            email = self.email_entry.get().strip()
            #added
            confirm_password = self.confirm_password_entry.get()

            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters")
                return
            #added
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return
                
            success, message = self.app.db.register_user(username, password, email)
            if success:
                messagebox.showinfo("Success", "Account created successfully! Please login.")
                self.toggle_form()
            else:
                messagebox.showerror("Registration Failed", message)