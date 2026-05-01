from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        from apps.catalog.models import Publisher, Author, Genre, Language, Book, BookInstance
        from apps.members.models import MemberProfile, PatronCategory
        from apps.circulation.models import BorrowRecord
        from apps.fines.models import Fine

        publishers_data = ['Penguin Books', 'HarperCollins', 'Random House', 'Simon & Schuster', 'Macmillan', 'Oxford University Press', 'Cambridge University Press']
        publishers = [Publisher.objects.create(name=name) for name in publishers_data]
        self.stdout.write(f'  Created {len(publishers)} publishers')

        authors_data = [
            ('George', 'Orwell', '1903-06-25'),
            ('Harper', 'Lee', '1926-04-28'),
            ('F. Scott', 'Fitzgerald', '1896-09-24'),
            ('J.K.', 'Rowling', '1965-07-31'),
            ('Mark', 'Twain', '1835-11-30'),
            ('Jane', 'Austen', '1775-12-16'),
            ('Charles', 'Dickens', '1812-02-07'),
            ('Leo', 'Tolstoy', '1828-09-09'),
            ('Gabriel Garcia', 'Marquez', '1927-03-06'),
            ('Ernest', 'Hemingway', '1899-07-21'),
            ('J.D.', 'Salinger', '1919-01-01'),
        ]
        authors = [Author.objects.create(first_name=f, last_name=l, date_of_birth=d) for f, l, d in authors_data]
        author_map = {f"{a.first_name} {a.last_name}": a for a in authors}
        self.stdout.write(f'  Created {len(authors)} authors')

        genres_data = ['Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Mystery', 'Romance', 'Thriller', 'Biography', 'History', 'Science', 'Poetry', 'Drama']
        genres = [Genre.objects.create(name=name) for name in genres_data]
        self.stdout.write(f'  Created {len(genres)} genres')

        languages_data = [('English', 'en'), ('Spanish', 'es'), ('French', 'fr'), ('German', 'de'), ('Hindi', 'hi')]
        languages = [Language.objects.create(name=n, code=c) for n, c in languages_data]
        self.stdout.write(f'  Created {len(languages)} languages')

        books_data = [
            ('1984', 'George Orwell', 1949, publishers[0], ['Fiction', 'Science Fiction'], 'A dystopian social science fiction novel.', '978-0451524935'),
            ('To Kill a Mockingbird', 'Harper Lee', 1960, publishers[1], ['Fiction', 'Drama'], 'A novel about racial injustice in the American South.', '978-0061120084'),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 1925, publishers[2], ['Fiction', 'Romance'], 'A novel about the American Dream.', '978-0743273565'),
            ('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', 1997, publishers[3], ['Fantasy', 'Fiction'], 'A young wizard\'s journey begins.', '978-0590353427'),
            ('Adventures of Huckleberry Finn', 'Mark Twain', 1884, publishers[4], ['Fiction', 'Drama'], 'A boy\'s adventure along the Mississippi.', '978-0142437179'),
            ('Pride and Prejudice', 'Jane Austen', 1813, publishers[5], ['Romance', 'Fiction'], 'A classic romance novel.', '978-0141439518'),
            ('A Tale of Two Cities', 'Charles Dickens', 1859, publishers[6], ['Fiction', 'History'], 'Set during the French Revolution.', '978-0141439600'),
            ('War and Peace', 'Leo Tolstoy', 1869, publishers[0], ['Fiction', 'History'], 'Epic novel of Russian society.', '978-0140447934'),
            ('One Hundred Years of Solitude', 'Gabriel Garcia Marquez', 1967, publishers[1], ['Fiction', 'Drama'], 'Multi-generational story of the Buendia family.', '978-0060883287'),
            ('The Old Man and the Sea', 'Ernest Hemingway', 1952, publishers[2], ['Fiction', 'Drama'], 'An aging fisherman\'s struggle.', '978-0684801223'),
            ('Animal Farm', 'George Orwell', 1945, publishers[3], ['Fiction', 'Science Fiction'], 'An allegorical novella.', '978-0451526342'),
            ('The Catcher in the Rye', 'J.D. Salinger', 1951, publishers[4], ['Fiction', 'Drama'], 'A teenage boy\'s experiences in New York.', '978-0316769488'),
        ]

        books = []
        for title, author_name, year, publisher, genre_names, desc, isbn in books_data:
            author = author_map.get(author_name)
            if not author:
                self.stdout.write(self.style.WARNING(f'  Warning: Author "{author_name}" not found, skipping'))
                continue
            book = Book.objects.create(
                title=title,
                publisher=publisher,
                publish_date=f'{year}-01-01',
                description=desc,
                isbn_13=isbn,
                total_copies=random.randint(2, 5),
                available_copies=random.randint(1, 4),
            )
            book.authors.add(author)
            for g in genre_names:
                genre = Genre.objects.get(name=g)
                book.genres.add(genre)
            book.languages.add(languages[0])
            books.append(book)

        self.stdout.write(f'  Created {len(books)} books')

        for i, book in enumerate(books):
            for j in range(book.total_copies):
                BookInstance.objects.create(
                    book=book,
                    barcode=f'BC{book.id:03d}{j+1:02d}',
                    call_number=f'{book.dewey_decimal or str(random.randint(800, 899))}.{random.randint(10, 99)}',
                    status='available' if j < book.available_copies else 'on_loan',
                    shelf_location=f'Shelf {random.randint(1, 10)}-Row {random.randint(1, 5)}',
                )

        self.stdout.write(f'  Created book instances')

        categories_data = [
            ('Student', 'Student members', 5, 14, 2, 14, 0.50, 25.00),
            ('Faculty', 'Faculty members', 10, 30, 3, 30, 0.25, 50.00),
            ('General', 'General public', 3, 14, 1, 14, 1.00, 15.00),
            ('Premium', 'Premium members', 15, 30, 5, 30, 0.00, 0.00),
        ]
        categories = [PatronCategory.objects.create(
            name=n, description=d, max_books_allowed=m, loan_period_days=l,
            max_renewals=r, renewal_period_days=rp, daily_fine_rate=f, max_fine_amount=mf
        ) for n, d, m, l, r, rp, f, mf in categories_data]
        self.stdout.write(f'  Created {len(categories)} patron categories')

        admin_user = User.objects.create_superuser('admin', 'admin@library.com', 'admin123', role='admin', first_name='Admin', last_name='User')
        librarian = User.objects.create_user('librarian', 'librarian@library.com', 'lib123', role='librarian', first_name='John', last_name='Librarian')
        self.stdout.write('  Created admin and librarian users')

        member_names = [('Alice', 'Johnson'), ('Bob', 'Smith'), ('Carol', 'Williams'), ('David', 'Brown'), ('Emma', 'Davis')]
        members = []
        for i, (first, last) in enumerate(member_names):
            user = User.objects.create_user(
                username=f'member{i+1}',
                email=f'{first.lower()}@example.com',
                first_name=first,
                last_name=last,
                password='member123',
                role='member',
            )
            member = MemberProfile.objects.create(
                user=user,
                category=random.choice(categories),
                phone_number=f'555-{1000+i}',
                membership_start=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                status='active',
            )
            members.append(member)
        self.stdout.write(f'  Created {len(members)} members')

        for _ in range(15):
            book = random.choice(books)
            available_instances = book.instances.filter(status='available')
            if available_instances.exists():
                instance = available_instances.first()
                member = random.choice(members)
                issue_date = timezone.now() - timedelta(days=random.randint(1, 60))
                due_date = issue_date + timedelta(days=member.category.loan_period_days)

                borrow = BorrowRecord.objects.create(
                    book_instance=instance,
                    member=member,
                    issue_date=issue_date,
                    due_date=due_date.date(),
                    issued_by=librarian,
                )
                instance.status = 'on_loan'
                instance.save()
                book.available_copies = max(0, book.available_copies - 1)
                book.save()

        self.stdout.write('  Created 15 borrow records')

        overdue_records = BorrowRecord.objects.filter(return_date__isnull=True, due_date__lt=timezone.now().date())
        for record in overdue_records:
            days = record.overdue_days
            amount = days * record.member.category.daily_fine_rate
            amount = min(amount, record.member.category.max_fine_amount)
            Fine.objects.create(
                member=record.member,
                borrow_record=record,
                fine_type='overdue',
                amount=amount,
            )

        self.stdout.write(self.style.SUCCESS('\nSeed data created successfully!'))
        self.stdout.write(self.style.WARNING('\nLogin credentials:'))
        self.stdout.write(f'  Admin: admin / admin123')
        self.stdout.write(f'  Librarian: librarian / lib123')
        self.stdout.write(f'  Members: member1-5 / member123')
