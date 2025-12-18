"""
Reading Calendar Widget
Displays a calendar with highlighted reading streak days.
"""

import tkinter as tk
from datetime import datetime, timedelta
import calendar

class ReadingCalendar(tk.Frame):
    """Calendar widget that highlights reading streak days"""
    DARK_BROWN = "#3E2723"
    MEDIUM_BROWN = "#5D4037"
    LIGHT_BROWN = "#8D6E63"
    ACCENT_BROWN = "#A1887F"
    CREAM = "#EFEBE9"
    WHITE = "#f5f5f5"
    
    def __init__(self, parent, app, user_id):
        super().__init__(parent, bg="white")
        self.app = app
        self.user_id = user_id
        self.pack(fill="both", expand=True)
        
        # Current month and year
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        
        # Store streak dates
        self.streak_dates = set()
        
        self.create_widgets()
        self.load_streaks()
        
    def create_widgets(self):
        """Create the calendar interface"""
        # Header
        header = tk.Frame(self, bg=self.MEDIUM_BROWN, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Reading Calendar",
            font=("Helvetica", 16, "bold"),
            bg=self.MEDIUM_BROWN,
            fg=self.CREAM
        ).pack(pady=15)
        
        # Month navigation
        nav_frame = tk.Frame(self, bg="white")
        nav_frame.pack(fill="x", pady=15)
        
        prev_btn = tk.Button(
            nav_frame,
            text="◀",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg=self.DARK_BROWN,
            relief="flat",
            cursor="hand2",
            command=self.prev_month,
            padx=10
        )
        prev_btn.pack(side="left", padx=10)
        
        self.month_label = tk.Label(
            nav_frame,
            text="",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        )
        self.month_label.pack(side="left", expand=True)
        
        next_btn = tk.Button(
            nav_frame,
            text="▶",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg=self.DARK_BROWN,
            relief="flat",
            cursor="hand2",
            command=self.next_month,
            padx=10
        )
        next_btn.pack(side="right", padx=10)
        
        # Calendar grid
        self.calendar_frame = tk.Frame(self, bg="white")
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Streak stats
        stats_frame = tk.Frame(self, bg="white")
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        self.streak_label = tk.Label(
            stats_frame,
            text="Current Streak: 0 days",
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg=self.DARK_BROWN
        )
        self.streak_label.pack()
        
        self.total_label = tk.Label(
            stats_frame,
            text="Total Days: 0",
            font=("Helvetica", 10),
            bg="white",
            fg=self.MEDIUM_BROWN
        )
        self.total_label.pack(pady=(5, 0))
        
        # Legend
        legend_frame = tk.Frame(self, bg="white")
        legend_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        legend_item1 = tk.Frame(legend_frame, bg="white")
        legend_item1.pack(anchor="w", pady=2)
        
        tk.Label(
            legend_item1,
            text="●",
            font=("Helvetica", 16),
            bg="white",
            fg=self.DARK_BROWN
        ).pack(side="left")
        
        tk.Label(
            legend_item1,
            text="Reading Day",
            font=("Helvetica", 9),
            bg="white",
            fg=self.MEDIUM_BROWN
        ).pack(side="left", padx=(5, 0))
        
        legend_item2 = tk.Frame(legend_frame, bg="white")
        legend_item2.pack(anchor="w", pady=2)
        
        tk.Label(
            legend_item2,
            text="●",
            font=("Helvetica", 16),
            bg="white",
            fg=self.LIGHT_BROWN
        ).pack(side="left")
        
        tk.Label(
            legend_item2,
            text="Today",
            font=("Helvetica", 9),
            bg="white",
            fg=self.MEDIUM_BROWN
        ).pack(side="left", padx=(5, 0))
        
    def display_calendar(self):
        """Display the calendar for current month"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
            
        # Update month label
        month_name = calendar.month_name[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            tk.Label(
                self.calendar_frame,
                text=day,
                font=("Helvetica", 9, "bold"),
                bg="white",
                fg=self.MEDIUM_BROWN,
                width=4
            ).grid(row=0, column=i, padx=2, pady=5)
        
        # Get calendar for current month
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Current date
        today = datetime.now().date()
        
        # Display days
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell
                    tk.Label(
                        self.calendar_frame,
                        text="",
                        bg="white",
                        width=4,
                        height=2
                    ).grid(row=week_num + 1, column=day_num, padx=2, pady=2)
                else:
                    # Create date for this day
                    date_obj = datetime(self.current_year, self.current_month, day).date()
                    date_str = date_obj.strftime('%Y-%m-%d')
                    
                    # Determine colors
                    is_today = date_obj == today
                    has_streak = date_str in self.streak_dates
                    
                    if is_today and has_streak:
                        bg_color = self.DARK_BROWN
                        fg_color = "white"
                    elif is_today:
                        bg_color = self.LIGHT_BROWN
                        fg_color = "white"
                    elif has_streak:
                        bg_color = self.DARK_BROWN
                        fg_color = "white"
                    else:
                        bg_color = "#f8f9fa"
                        fg_color = "#2c3e50"
                    
                    day_label = tk.Label(
                        self.calendar_frame,
                        text=str(day),
                        font=("Helvetica", 10, "bold" if is_today else "normal"),
                        bg=bg_color,
                        fg=fg_color,
                        width=4,
                        height=2,
                        cursor="hand2" if date_obj <= today else "arrow"
                    )
                    day_label.grid(row=week_num + 1, column=day_num, padx=2, pady=2)
                    
                    # Allow clicking to toggle streak (only for today or past days)
                    if date_obj <= today:
                        day_label.bind("<Button-1>", 
                                     lambda e, d=date_str: self.toggle_streak(d))
                        
    def load_streaks(self):
        """Load reading streaks from database"""
        streaks = self.app.db.get_reading_streaks(
            self.user_id,
            self.current_year,
            self.current_month
        )
        
        self.streak_dates = set()
        for streak in streaks:
            date_str = streak['date'].strftime('%Y-%m-%d')
            self.streak_dates.add(date_str)
            
        # Calculate current streak
        current_streak = self.calculate_current_streak()
        self.streak_label.config(text=f"Current Streak: {current_streak} days")
        
        # Total reading days
        total_days = len(self.streak_dates)
        self.total_label.config(text=f"Total Days This Month: {total_days}")
        
        self.display_calendar()
        
    def calculate_current_streak(self):
        """Calculate current consecutive reading streak"""
        if not self.streak_dates:
            return 0
            
        today = datetime.now().date()
        streak = 0
        current_date = today
        
        # Count backwards from today
        while current_date.strftime('%Y-%m-%d') in self.streak_dates:
            streak += 1
            current_date -= timedelta(days=1)
            
        return streak
        
    def toggle_streak(self, date_str):
        """Toggle reading streak for a date"""
        if date_str in self.streak_dates:
            # Remove streak - not implemented as we want to keep history
            pass
        else:
            # Add streak
            self.app.db.add_reading_streak(self.user_id, date_str, 0)
            self.load_streaks()
            
    def prev_month(self):
        """Go to previous month"""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.load_streaks()
        
    def next_month(self):
        """Go to next month"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.load_streaks()