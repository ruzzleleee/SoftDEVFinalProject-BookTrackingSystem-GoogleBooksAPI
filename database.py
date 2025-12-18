"""
Database Manager for Book Tracking Application
Handles all MySQL database operations including user authentication,
book management, reviews, and reading streaks.
"""

import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime

class Database:
    """Manages all database operations for the book tracking system"""
    
    def __init__(self):
        """Initialize database connection and create tables if they don't exist"""
        self.connection = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',  # Change to your MySQL username
                password='',  # Change to your MySQL password
                database='book_tracker'
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            # Try to create database if it doesn't exist
            try:
                temp_conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password=''
                )
                cursor = temp_conn.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS book_tracker")
                temp_conn.close()
                self.connect()  # Reconnect to the newly created database
            except Error as e2:
                print(f"Error creating database: {e2}")
                
    def create_tables(self):
        """Create all necessary tables in the database"""
        if not self.connection or not self.connection.is_connected():
            return
            
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                book_id INT AUTO_INCREMENT PRIMARY KEY,
                google_books_id VARCHAR(50),
                title VARCHAR(255) NOT NULL,
                authors TEXT,
                description TEXT,
                cover_url TEXT,
                page_count INT,
                published_date VARCHAR(50),
                categories TEXT
            )
        """)
        
        # User books table (tracks reading status)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                status ENUM('currently_reading', 'finished', 'favourite') NOT NULL,
                current_page INT DEFAULT 0,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_finished TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_book_status (user_id, book_id, status)
            )
        """)
        
        # Reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                rating INT CHECK (rating BETWEEN 1 AND 5),
                review_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_review (user_id, book_id)
            )
        """)
        
        # Reading streaks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reading_streaks (
                streak_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                date DATE NOT NULL,
                pages_read INT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_date (user_id, date)
            )
        """)
        
        self.connection.commit()
        cursor.close()
        
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def register_user(self, username, password, email=""):
        """Register a new user"""
        try:
            cursor = self.connection.cursor()
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                (username, password_hash, email)
            )
            self.connection.commit()
            cursor.close()
            return True, "Registration successful!"
        except mysql.connector.IntegrityError:
            return False, "Username already exists!"
        except Error as e:
            return False, f"Error: {e}"
            
    def login_user(self, username, password):
        """Authenticate user login"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            password_hash = self.hash_password(password)
            cursor.execute(
                "SELECT user_id, username FROM users WHERE username = %s AND password_hash = %s",
                (username, password_hash)
            )
            user = cursor.fetchone()
            cursor.close()
            if user:
                return True, user['user_id'], user['username']
            return False, None, "Invalid username or password"
        except Error as e:
            return False, None, f"Error: {e}"
            
    def add_book(self, book_data):
        """Add a book to the database or return existing book_id"""
        try:
            cursor = self.connection.cursor()
            
            # Check if book already exists
            cursor.execute(
                "SELECT book_id FROM books WHERE google_books_id = %s",
                (book_data.get('google_books_id'),)
            )
            result = cursor.fetchone()
            
            if result:
                cursor.close()
                return result[0]
                
            # Insert new book
            cursor.execute("""
                INSERT INTO books (google_books_id, title, authors, description, 
                                 cover_url, page_count, published_date, categories)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                book_data.get('google_books_id'),
                book_data.get('title'),
                book_data.get('authors'),
                book_data.get('description'),
                book_data.get('cover_url'),
                book_data.get('page_count'),
                book_data.get('published_date'),
                book_data.get('categories')
            ))
            
            book_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            return book_id
        except Error as e:
            print(f"Error adding book: {e}")
            return None
            
    def add_user_book(self, user_id, book_id, status):
        """Add a book to user's collection with a specific status"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO user_books (user_id, book_id, status)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE date_added = CURRENT_TIMESTAMP
            """, (user_id, book_id, status))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error adding user book: {e}")
            return False
            
    def get_user_books(self, user_id, status):
        """Get all books for a user with a specific status"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT b.*, ub.current_page, ub.date_added, ub.date_finished, ub.id as user_book_id
                FROM books b
                JOIN user_books ub ON b.book_id = ub.book_id
                WHERE ub.user_id = %s AND ub.status = %s
                ORDER BY ub.date_added DESC
            """, (user_id, status))
            books = cursor.fetchall()
            cursor.close()
            return books
        except Error as e:
            print(f"Error getting user books: {e}")
            return []
            
    def update_book_progress(self, user_book_id, current_page):
        """Update the current page for a book being read"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE user_books SET current_page = %s WHERE id = %s",
                (current_page, user_book_id)
            )
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error updating progress: {e}")
            return False
            
    def add_review(self, user_id, book_id, rating, review_text):

        """Add or update a book review"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO reviews (user_id, book_id, rating, review_text)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    rating = VALUES(rating),
                    review_text = VALUES(review_text),
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, book_id, rating, review_text))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error adding review: {e}")
            return False
        
    def delete_review(self, user_id, book_id):

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM reviews WHERE user_id = %s AND book_id = %s",
                (user_id, book_id)
            )
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            return rows_affected > 0
        except Error as e:
            print(f"Error deleting review: {e}")
            return False
            
    def get_review(self, user_id, book_id):
        """Get a user's review for a specific book"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM reviews WHERE user_id = %s AND book_id = %s",
                (user_id, book_id)
            )
            review = cursor.fetchone()
            cursor.close()
            return review
        except Error as e:
            print(f"Error getting review: {e}")
            return None
            
    def add_reading_streak(self, user_id, date, pages_read=0):
        """Add or update a reading streak for a specific date"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO reading_streaks (user_id, date, pages_read)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE pages_read = pages_read + VALUES(pages_read)
            """, (user_id, date, pages_read))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error adding reading streak: {e}")
            return False
            
    def get_reading_streaks(self, user_id, year, month):
        """Get all reading streak dates for a user in a specific month"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT date, pages_read FROM reading_streaks
                WHERE user_id = %s 
                AND YEAR(date) = %s 
                AND MONTH(date) = %s
            """, (user_id, year, month))
            streaks = cursor.fetchall()
            cursor.close()
            return streaks
        except Error as e:
            print(f"Error getting streaks: {e}")
            return []
            
    def remove_user_book(self, user_book_id):
        """Remove a book from user's collection"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM user_books WHERE id = %s", (user_book_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error removing book: {e}")
            return False
            
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")