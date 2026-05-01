from django.db import models
from django.utils.text import slugify


class Publisher(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [models.Index(fields=['last_name', 'first_name'])]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    dewey_decimal = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name_plural = 'Genres'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True)
    isbn_10 = models.CharField(max_length=13, unique=True, blank=True, null=True)
    isbn_13 = models.CharField(max_length=17, unique=True, blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    publish_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='books')
    languages = models.ManyToManyField(Language, related_name='books')
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True)
    dewey_decimal = models.CharField(max_length=20, blank=True)
    lc_classification = models.CharField(max_length=50, blank=True)
    subject_keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords")
    total_copies = models.PositiveIntegerField(default=0)
    available_copies = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn_13']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        return self.available_copies > 0


class BookInstance(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('on_loan', 'On Loan'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
        ('withdrawn', 'Withdrawn'),
    )
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='instances')
    barcode = models.CharField(max_length=100, unique=True)
    call_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    acquisition_date = models.DateField(null=True, blank=True)
    acquisition_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shelf_location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['book__title', 'barcode']
        indexes = [
            models.Index(fields=['barcode']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.book.title} ({self.barcode})"
