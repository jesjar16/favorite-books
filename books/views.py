from datetime import datetime, timezone
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from books.models import User, Message, Comment, Book
from django.contrib import messages
import bcrypt
from django.db import IntegrityError
from books.decorators import login_required

# Create your views here.
def index(request):
    return render(request, "index.html")

def register(request):
    # getting form variables
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    birthday = request.POST['birthday']
    password = request.POST['password']
    password2 = request.POST['password2']
    
    # errors dict is received
    errors = User.objects.basic_validator(request.POST)
    
    # if there are errors
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        
        # getting the current form values
        form_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'birthday': birthday
        }
        
        request.session['form_data'] = form_data
        
        return redirect(reverse("my_index"))
    else:
        try:
            # hashing password
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            # creating the user
            this_user = User.objects.create(first_name=first_name, last_name=last_name, email=email, birthday=birthday, password=hashed_password) 

            # creating dictionary with user's data
            user_data = {
                    'user_id': this_user.id,
                    'first_name': this_user.first_name.capitalize(),
                    'last_name': this_user.last_name.capitalize(),
                    'email': this_user.email,
                    'action': 'register'
            }
            
            # saving user dictionary to session variable
            request.session['user_data'] = user_data
                
            messages.success(request, "User successfully created and logged in")
        
            return redirect(reverse("my_success"))
        except IntegrityError as e:
            if 'UNIQUE constraint' in str(e.args):
                messages.error(request, 'Email is already registered, try logging in')
                
                # getting the current form values
                form_data = {
                    'first_name': first_name.capitalize(),
                    'last_name': last_name.capitalize(),
                    'email': email,
                    'birthday': birthday
                }
                
                request.session['form_data'] = form_data

            return redirect(reverse("my_index"))

def login(request):
    # form variables are received
    email_login = request.POST['email_login']
    password_login = request.POST['password_login']
    
    # errors dict is received
    errors = User.objects.basic_validator2(request.POST)
    
    # if there are errors
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        
        # saving form data into form_data dictionary
        form_data = {
            'email_login': email_login
        }
        
        request.session['form_data'] = form_data
        
        return redirect(reverse("my_index"))
    else: # no errors
        user = User.objects.filter(email=email_login)
        if user:
            logged_user = user[0] 
            if bcrypt.checkpw(password_login.encode(), logged_user.password.encode()):
                # creating session variables for logged in user
                user_data = {
                    'user_id': logged_user.id,
                    'first_name': logged_user.first_name.capitalize(),
                    'last_name': logged_user.last_name.capitalize(),
                    'email': logged_user.email,
                    'action': 'login'
                }
                
                request.session['user_data'] = user_data
                
                messages.success(request, "You have successfully login")
                
                return redirect(reverse("my_success"))
            else:
                messages.error(request, "Wrong email or password")
                
                return redirect(reverse("my_index"))
        else:
            messages.error(request, "Wrong email or password")
                
            return redirect(reverse("my_index"))

@login_required
def success(request):
    return redirect(reverse("my_books"))
    
@login_required    
def homepage(request):
    return render(request, "homepage.html")

@login_required    
def books(request):
    # retrieving books
    all_books = Book.objects.all().order_by('-id')
    
    # retrieving current logged in user
    this_user = User.objects.get(id=request.session['user_data']['user_id'])
    
    # retrieving all books liked by this user
    liked_by_this_user = this_user.liked_books.all() 
    
    # retrieving all books uploaded by this user
    uploaded_by_this_user = Book.objects.filter(uploaded_by=this_user)
    
    context = {
        'all_books': all_books,
        'liked_by_this_user': liked_by_this_user,
        'uploaded_by_this_user': uploaded_by_this_user,
        'form_send': True
    }
    
    if 'form_data' in request.session:
        del request.session['form_data']
    
    return render(request, "books.html", context)    

@login_required    
def add_book(request):
    # form variables are received
    title = request.POST['title']
    description = request.POST['description']
    
    # errors dict is received
    errors = Book.objects.basic_validator(request.POST)
    
    # retrieving books
    all_books = Book.objects.all()
    
    context = {
        'all_books': all_books,
        'form_send': True
    }
        
    # if there are errors
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)

        form_data = {
            'title': title,
            'desc': description
        } 
        
        request.session['form_data'] = form_data
            
        return render(request, "books.html", context)
    else: # no errors
        id = request.session['user_data']['user_id']
        this_user = User.objects.get(id=id)
        
        # save book
        this_book = Book.objects.create(title=title, desc=description, uploaded_by=this_user)
        
        # adding the book to user's favorites
        this_user.liked_books.add(this_book)
        
        messages.success(request, "Book successfully added")
        
        if 'form_data' in request.session:
            del request.session['form_data']

        return redirect(reverse("my_books"))

                

@login_required    
def favorite(request, book_id, source):
    # getting current user
    id = request.session['user_data']['user_id']
    this_user = User.objects.get(id=id)
    
    # save book
    this_book = Book.objects.get(id=book_id)
    
    # adding the book to user's favorites
    this_user.liked_books.add(this_book)
    
    messages.success(request, "Book added to favorites")
    
    return my_redirect(source, book_id)

@login_required    
def unfavorite(request, book_id, source):
    # getting current user 
    id = request.session['user_data']['user_id']
    this_user = User.objects.get(id=id)
    
    # save book
    this_book = Book.objects.get(id=book_id)
    
    # adding the book to user's favorites
    this_user.liked_books.remove(this_book)
    
    messages.success(request, "Book removed from favorites")
    
    if 'form_data' in request.session:
        del request.session['form_data']
    
    return my_redirect(source, book_id)

def my_redirect(source, book_id):
    # redirect will depend on the request source page
    if source == "books":
        return redirect(reverse("my_books"))
    elif source == "edit":
        return redirect(reverse("my_edit", args=(book_id,)))
    elif source == "view":
        return redirect(reverse("my_view", args=(book_id,)))
    elif source == "all_favs":
        return redirect(reverse("my_all_favs"))    
    
@login_required    
def edit(request, book_id):
    # getting book information
    this_book = Book.objects.get(id=book_id)
    
    id = request.session['user_data']['user_id']
    this_user = User.objects.get(id=id)
    
    # getting users who like this book
    users_who_like = User.objects.filter(liked_books=this_book)

    context = {
        'this_user': this_user,
        'this_book': this_book,
        'users_who_like': users_who_like
    }
    
    if 'form_data' not in request.session:
        form_data = {
            'title': this_book.title,
            'desc': this_book.desc
        } 
        
        request.session['form_data'] = form_data

    return render(request, "edit.html", context)

@login_required    
def update(request, book_id):
    if request.POST:        
        # getting form variables
        title = request.POST['title']    
        description = request.POST['description']
    
        # receiving errors dict
        errors = Book.objects.basic_validator(request.POST)
        
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            
            form_data = {
                'title': title,
                'desc': description
            } 
        
            request.session['form_data'] = form_data
                
            return redirect(reverse("my_edit", args=(book_id,)))
        else:
            # updating book
            book_to_update= Book.objects.get(id=book_id)
            
            book_to_update.title = title
            book_to_update.desc = description

            book_to_update.save()
            
            form_data = {
                'title': book_to_update.title,
                'desc': book_to_update.desc
            } 
            
            request.session['form_data'] = form_data
            
            messages.success(request, "Book successfully updated")

            # once updated, redirect to edit page (books)
            return redirect(reverse("my_edit", args=(book_id,)))

@login_required    
def delete(request, book_id):
    # getting book information
    book_to_delete = Book.objects.get(id=book_id)
    
    # deleting book
    book_to_delete.delete()
    
    if 'form_data' in request.session:
        del request.session['form_data']

    return redirect(reverse("my_books"))

@login_required    
def view(request, book_id):
    # getting book information
    this_book = Book.objects.get(id=book_id)
    
    id = request.session['user_data']['user_id']
    this_user = User.objects.get(id=id)
    
    # getting users who like this book
    print(User.objects.filter(liked_books=this_book))
    users_who_like = User.objects.filter(liked_books=this_book)

    context = {
        'this_user': this_user,
        'this_book': this_book,
        'users_who_like': users_who_like
    }

    return render(request, "view.html", context) 

@login_required    
def all_favs(request):
    # getting current user
    id = request.session['user_data']['user_id']
    this_user = User.objects.get(id=id)
    
    liked_by_this_user = this_user.liked_books.all().order_by('-id') 

    context = {
        'liked_by_this_user': liked_by_this_user
    }

    return render(request, "favorite.html", context) 
    
@login_required
def about(request):
    return render(request, "about.html")

def logout(request):
    # deleting session variables
    if 'form_data' in request.session:
        del request.session['form_data']
        
    if 'user_data' in request.session:
        del request.session['user_data']
        messages.success(request, "You have successfully logout")
    
    return redirect(reverse("my_index")) 