"""
Google Books API Handler
Manages all interactions with the Google Books API for searching books.
"""

import requests
from urllib.parse import quote

class GoogleBooksAPI:
    """Handles Google Books API requests"""
    
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    @staticmethod
    def search_books(query, max_results=20):
        """
        Search for books using Google Books API
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of book dictionaries with relevant information
        """
        try:
            # Encode query for URL
            encoded_query = quote(query)
            url = f"{GoogleBooksAPI.BASE_URL}?q={encoded_query}&maxResults={max_results}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' not in data:
                return []
                
            books = []
            for item in data['items']:
                book_info = GoogleBooksAPI.parse_book_data(item)
                if book_info:
                    books.append(book_info)
                    
            return books
            
        except requests.RequestException as e:
            print(f"Error searching books: {e}")
            return []
            
    @staticmethod
    def parse_book_data(item):
        """
        Parse book data from Google Books API response
        
        Args:
            item: Single book item from API response
            
        Returns:
            Dictionary with formatted book information
        """
        try:
            volume_info = item.get('volumeInfo', {})
            
            # Extract authors
            authors = volume_info.get('authors', [])
            authors_str = ', '.join(authors) if authors else 'Unknown Author'
            
            # Extract categories
            categories = volume_info.get('categories', [])
            categories_str = ', '.join(categories) if categories else ''
            
            # Extract cover image
            image_links = volume_info.get('imageLinks', {})
            cover_url = image_links.get('thumbnail', '')
            
            # Use higher quality image if available
            if cover_url:
                cover_url = cover_url.replace('zoom=1', 'zoom=2')
                cover_url = cover_url.replace('http://', 'https://')
            
            book_data = {
                'google_books_id': item.get('id', ''),
                'title': volume_info.get('title', 'Unknown Title'),
                'authors': authors_str,
                'description': volume_info.get('description', 'No description available'),
                'cover_url': cover_url,
                'page_count': volume_info.get('pageCount', 0),
                'published_date': volume_info.get('publishedDate', ''),
                'categories': categories_str,
                'preview_link': volume_info.get('previewLink', ''),
                'info_link': volume_info.get('infoLink', '')
            }
            
            return book_data
            
        except Exception as e:
            print(f"Error parsing book data: {e}")
            return None
            
    @staticmethod
    def get_book_by_id(google_books_id):
        """
        Get detailed information for a specific book by its Google Books ID
        
        Args:
            google_books_id: The Google Books ID
            
        Returns:
            Dictionary with book information or None
        """
        try:
            url = f"{GoogleBooksAPI.BASE_URL}/{google_books_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return GoogleBooksAPI.parse_book_data(data)
            
        except requests.RequestException as e:
            print(f"Error getting book details: {e}")
            return None