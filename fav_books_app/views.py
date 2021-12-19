from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt


def index(request):
    return render(request, "index.html")

def register(request):
    errors = User.objects.register_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            password = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        )
        request.session['user_id'] = user.id
        request.session['greeting'] = user.first_name
        return redirect('/main_page')

def login(request):
    errors = User.objects.login_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        user = User.objects.get(email=request.POST['login_email'])
        request.session['user_id'] = user.id
        request.session['greeting'] = user.first_name
        return redirect('/main_page')

def main_page(request):
    if "user_id" not in request.session:
        return redirect('/')
    else:
        context = {
            'all_books': Book.objects.all(),
            'this_user': User.objects.get(id=request.session['user_id'])
        }
    return render(request, 'main_page.html', context)

def logout(request):
    request.session.flush()
    return redirect('/')
    
def add_book(request):
    errors = Book.objects.book_validator(request.POST)
    if len(errors):
        for e in errors.values():
            messages.error(request, e)
        return redirect('/main_page')
    else:
        user = User.objects.get(id=request.session["user_id"])
        book = Book.objects.create(
            title = request.POST['title'],
            description = request.POST['description'],
            creator = user
        )
        return redirect('/main_page')

def books(request, book_id):
    context = {
        'book': Book.objects.get(id=book_id),
        'this_user': User.objects.get(id=request.session['user_id'])
    }
    return render(request, 'books.html', context)

def favorite(request, book_id):
    user = User.objects.get(id=request.session["user_id"])
    book = Book.objects.get(id=book_id)
    user.favorited_books.add(book)
    return redirect('/main_page')


def unfavorite(request, book_id):
    user = User.objects.get(id=request.session["user_id"])
    book = Book.objects.get(id=book_id)
    user.favorited_books.remove(book)

    return redirect('/main_page')

def update(request, book_id):
    book = Book.objects.get(id=book_id)
    book.description = request.POST['description']
    book.save()

    return redirect(f"/books/{book_id}")

def delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()

    return redirect('/main_page')
