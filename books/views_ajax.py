from books.models import User, Message, Comment, Book
from django.http.response import HttpResponse, JsonResponse
from books.decorators import login_required

def add_book_ajax(request):
    print("EN ajax")
    print(request.POST)
    # form variables are received
    title = request.POST['title']
    description = request.POST['description']
    
    # errors dict is received
    errors = Book.objects.basic_validator(request.POST)
    
    # if there are errors
    if len(errors) > 0:
        errors_list = []
        for key, value in errors.items():
            errors_list.append(value)
        return JsonResponse({'errors': errors_list}, status=400, safe=False)    
    
    # si llegamos acá, los datos del formulario están correctos
    
    id = request.session['user_data']['user_id']
    this_user = User.objects.get(id=id)
    
    # save book
    this_book = Book.objects.create(title=title, desc=description, uploaded_by=this_user)
    
    # adding the book to user's favorites
    this_user.liked_books.add(this_book)
    
    new_book = {'id': this_book.id,
                'title': this_book.title, 
                'uploader': f"{this_user.first_name} {this_user.last_name}"}
        
    return JsonResponse(new_book, safe=False)
