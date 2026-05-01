import requests
from django.conf import settings
from apps.catalog.models import Book, Author, Publisher, Genre, Language


class SearchService:
    @staticmethod
    def fetch_book_by_isbn(isbn):
        api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', '')
        url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
        if api_key:
            url += f'&key={api_key}'
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('totalItems', 0) == 0:
                return None
            
            item = data['items'][0]['volumeInfo']
            
            return {
                'title': item.get('title', ''),
                'subtitle': item.get('subtitle', ''),
                'authors': item.get('authors', []),
                'publisher': item.get('publisher', ''),
                'publish_date': item.get('publishedDate', '')[:4] if item.get('publishedDate') else '',
                'pages': item.get('pageCount', 0),
                'description': item.get('description', ''),
                'isbn_10': next((i for i in item.get('industryIdentifiers', []) if i.get('type') == 'ISBN_10'), {}).get('identifier', ''),
                'isbn_13': next((i for i in item.get('industryIdentifiers', []) if i.get('type') == 'ISBN_13'), {}).get('identifier', ''),
                'categories': item.get('categories', []),
                'image_url': item.get('imageLinks', {}).get('thumbnail', ''),
                'language': item.get('language', 'en'),
            }
        except (requests.RequestException, ValueError, KeyError):
            return None
    
    @staticmethod
    def create_book_from_isbn_data(data):
        publisher = None
        if data.get('publisher'):
            publisher, _ = Publisher.objects.get_or_create(name=data['publisher'])
        
        authors = []
        for author_name in data.get('authors', []):
            parts = author_name.split(' ', 1)
            first_name = parts[0] if parts else ''
            last_name = parts[1] if len(parts) > 1 else ''
            author, _ = Author.objects.get_or_create(first_name=first_name, last_name=last_name)
            authors.append(author)
        
        book = Book.objects.create(
            title=data.get('title', ''),
            subtitle=data.get('subtitle', ''),
            isbn_10=data.get('isbn_10') or None,
            isbn_13=data.get('isbn_13') or None,
            publisher=publisher,
            publish_date=data.get('publish_date') if data.get('publish_date') else None,
            pages=data.get('pages') or None,
            description=data.get('description', ''),
        )
        
        for author in authors:
            book.authors.add(author)
        
        for category in data.get('categories', []):
            genre, _ = Genre.objects.get_or_create(name=category)
            book.genres.add(genre)
        
        lang_code = data.get('language', 'en')
        language, _ = Language.objects.get_or_create(code=lang_code, defaults={'name': lang_code})
        book.languages.add(language)
        
        return book
