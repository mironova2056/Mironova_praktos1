from django.shortcuts import render, get_object_or_404, redirect
from .models import Book,Author,BookInstance,Genre,Language
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required, login_required
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


from  .forms import RenewBookForm

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
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 2

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = ('catalog.can_mark_returned')
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 2

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})
    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death':'12/10/2003'}
class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'
class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
@login_required
def change_copy_status(request, pk):
    copy = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(copy.LOAN_STATUS):
            copy.status = new_status
            copy.save()
            return redirect('book-detail', pk=copy.book.pk)

    return redirect('book-detail', pk=copy.book.pk)