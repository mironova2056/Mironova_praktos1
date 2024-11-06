from django.shortcuts import render
from .models import Book,Author,BookInstance,Genre,Language
from django.views import generic

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact = 'a').count()
    num_authors = Author.objects.count()
    genre_count = Genre.objects.count()

    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    return render(
        request, 'index.html',context={'num_books':num_books,
                                         'num_instances':num_instances,
                                         'num_instances_available':num_instances_available,
                                         'num_authors':num_authors,
                                       'genre_count':genre_count,
                                       'num_visits':num_visits}
    )
class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
class BookDetailView(generic.DetailView):
    model = Book
class AuthorsListView(generic.ListView):
    model = Author
    paginate_by = 2
class AuthorsDetailView(generic.DetailView):
    model = Author
class LanguageListView(generic.ListView):
    model = Language
    paginate_by = 2
class LanguageDetailView(generic.DetailView):
    model = Language
