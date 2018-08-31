from django.shortcuts import render, HttpResponse, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from template_email import TemplateEmail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from django.db.models import Count
from random import randint
import bcrypt
import json


######### function to generate random number of digits
def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)



############# GET THE NAVIGATION LANGUAGES ############
def navigation_language():
    # get all the snippets code languages except hmtl, css, javascript, python, mean, java, ruby
    langs = ["css","html","java","javascript","mean","python","ruby","sql"]
    temp_snippets = Snippet.objects.exclude(language__in=langs).order_by('language').values_list('language').distinct()
    langs = []
    for snippet in temp_snippets: # this an list of truples
        langs.append(snippet[0])
    return langs



############ FORMS RENDER ########################
def signin(request):
    # check if the user is logged in
    if 'user_id' in request.session:
        return redirect(reverse('home'))

    request.session.clear()
    return render(request, 'main/signin.html')

def signup(request):
    # check if the user is logged in
    if 'user_id' in request.session:
        return redirect(reverse('home'))
    
    request.session.clear()
    return render(request, 'main/signup.html')

############ SEND EMAIL TO THE USER ##############
def send_reset_email(request):
    # check if this email exist in the database
    user = User.objects.filter(email=request.POST['email'].strip().lower())
    if user:
        # generate a new 5 digits pin number and store in session
        request.session['session_pin'] = random_with_N_digits(5)

        # get the email
        email = request.POST['email'].strip().lower()

        # put this user in session
        request.session['reset_user_id'] = user[0].id
        
        data = {'username': user[0].username, 'pin': request.session['session_pin']}
        
        #### send the email now 
        subject, from_email, to = 'Snippet Reset Password Pin!', 'techboss30@gmail.com', email
        # text_content = f"Please use this temporatary pin number to reset your password. \nYour pin is: {request.session['session_pin']} \n\n\nThe Snippet Team."
        
        text_content = "Please use this temporatary pin number to reset your password. \nYour pin is:" + str(request.session['session_pin']) + "\n\n\nThe Snippet Team."
        
        email_msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        
        html_template = get_template('main/reset_pin_email.html').render(data)
        email_msg.attach_alternative(html_template, 'text/html')
        email_msg.send()
    else:
        return HttpResponse("Email was not send!")
    return HttpResponse("Email send!")


############# RENDER CONTRIBUTION PAGE ###########
def contribute(request):
    # get all the snippets with distinct (unique language)
    snippets = Snippet.objects.order_by('language').values_list('language').distinct()
    
    languages = []
    for snippet in snippets: # this an list of truples
        languages.append(snippet[0])
    return render(request, 'main/contribute.html', {'languages': languages})


################## HOME PAGE RENDER ###############
def home(request):
    # get all snippets from the database
    snippets = Snippet.objects.all().order_by("-created_at")
    navbar_languages = navigation_language()
    return render(request, 'main/home.html', {'snippets': snippets, 'navbar_languages': navbar_languages})


################# AJAX languages filter #####################
def languages(request, lang):
    # get all snippets from the database
    snippets = Snippet.objects.filter(language=lang).order_by("-created_at")

    # list of all the langs that have images available
    images_list = ["css", "html", "java", "javascript", "jquery", "mean", "mysql", "php", "python", "ruby", "sql", "swift"]

    is_available = False
    for image in images_list:
        if lang == image:
            is_available = True
    
    if not is_available:
        lang = "home"

    # get all the snippets code languages except hmtl, css, javascript, python, mean, java
    navbar_languages = navigation_language()
    return render(request, 'main/home.html', {'snippets': snippets, 'image_name': lang, 'navbar_languages': navbar_languages })


############## AJAX SEARCH PROCESS ################
def search(request):
    # get all snippets from the database
    search = request.POST['search_input'].strip().lower()
    snippets = Snippet.objects.filter(title__contains=search)|Snippet.objects.filter(language__contains=search)|Snippet.objects.filter(description__contains=search).order_by("-created_at")
    return render(request, 'main/search_results.html', {'snippets': snippets})


############## CHANGE ACCOUNT STATUS ############
def change_status(request):
    if 'user_id' not in request.session:
        return redirect(reverse('home'))

    # get the user object
    try:
        user = User.objects.get(id = request.session['user_id'])
    except:
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))

    # change the account status now
    # status 0 is private
    # status 1 is public
    if user.account_status == 0:
        user.account_status = 1
        message = "Your account is now public!"
    else:
        user.account_status = 0
        message = "Your account is now private!"

    user.save()
    messages.success(request, message, extra_tags='account_status')
    return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))


############## USER PROFILE #################
def profile(request, snippet_id):
    # check if the user is logged in
    if 'user_id' not in request.session:
        return redirect(reverse('home'))

    # get the logged in user object
    try:
        user = User.objects.get(id = request.session['user_id'])
    except:
        return redirect(reverse('home'))

    # get all the snippets that the user saved
    snippets = Snippet.objects.filter(favorite_users=user).order_by("-updated_at")

    # get the displaying snippet
    if snippet_id == "first":
        if snippets:
            saved = snippets[0]
            main_snippet = snippets[0] 
        else:
            saved = []
            main_snippet = {}
    else:
        try:
            main_snippet = Snippet.objects.get(id = int(snippet_id))
        except:
            return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))

        # check if the logged in user favorited this snippet
        saved = main_snippet
    # collect all data
    data = {
        'user': user,
        'snippets': snippets,
        'main_snippet': main_snippet,
        'saved': saved,
        'is_profile': 'true'
    }
    return render(request, 'main/profile.html', data)



############## USER FAVORITES SNIPPET #################
def favorites(request, fav_user_id, snippet_id):
    # get that user object whom we tryna see the favorites
    try:
        user = User.objects.get(id = fav_user_id)
    except:
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))
    
    # get all the snippets that the user saved
    snippets = Snippet.objects.filter(favorite_users=user).order_by("-updated_at")

    if 'user_id' in request.session: # check if the user is logged in
        # get logged in user objects
        try:
            logged_user = User.objects.get(id = request.session['user_id'])
        except:
            return redirect(reverse('home'))
        
        if snippet_id == 'first':
            if snippets:
                main_snippet = snippets[0] # get the displaying snippet
                favorite_users = snippets[0].favorite_users.all() # get the list of all users that favorites this snippet
                
                # check if the logged save this snippet
                if logged_user in favorite_users:
                    saved = main_snippet
                else:
                    saved = []
            else:
                main_snippet = {}
                saved = []
        else:
            try:
                main_snippet = Snippet.objects.get(id = snippet_id)
            except:
                return redirect(reverse('home'))
            
            favorite_users = main_snippet.favorite_users.all() # get the list of all users that favorites this snippet
            
            # check if the logged save this snippet
            if logged_user in favorite_users:
                saved = main_snippet
            else:
                saved = []

    # the user is not logged in
    else:
        saved = [] # since the user is not logged in
        if snippet_id == 'first':
            if snippets:
                main_snippet = snippets[0]
            else:
                main_snippet = {}
        else:
            try:
                main_snippet = Snippet.objects.get(id = snippet_id)
            except:
                return redirect(reverse('home'))

    # collect all data
    data = {
        'user': user,
        'snippets': snippets,
        'main_snippet': main_snippet,
        'saved': saved,
        'is_profile': 'false'
    }

    # create a favorite user id
    request.session['fav_user_id'] = fav_user_id
    return render(request, 'main/profiles_layout.html', data)



################ REMOVE A SNIPPET FROM THE USER FAVS ############
def remove_favorite(request, id):
    # check if the user is logged in
    if 'user_id' not in request.session:
        return redirect(reverse('home'))

    # get the user object
    try:
        user = User.objects.get(id = request.session['user_id'])
    except:
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))

    # get the snippet object
    try:
        snippet = Snippet.objects.get(id = id)
    except:
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))
    
    # remove this snippet from the user snippets
    snippet.favorite_users.remove(user)
    messages.success(request, 'A snippet was removed from your favorites!', extra_tags='account_status')
    
    return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))



################ ADD A SNIPPET TO THE USER FAVS ############
def add_favorite(request, snippet_id, page):
    if 'user_id' not in request.session:
        return redirect(reverse('home'))

    # get the user object
    try:
        user = User.objects.get(id = request.session['user_id'])
    except:
        return redirect(reverse('home'))

    # get the snippet object
    try:
        snippet = Snippet.objects.get(id = snippet_id)
    except:
        return redirect(reverse('home'))
    
    # add this snippet to the user favorites snippets 
    snippet.favorite_users.add(user)
    messages.success(request, 'This snippet was added to your favorites!', extra_tags='add_favorite')
    
    # redirect to the right page
    if page == 'profile':
        return redirect(reverse('profile', kwargs={'snippet_id': snippet_id}))
    elif page == 'favorites':
        return redirect(reverse('favorites', kwargs={'fav_user_id': request.session['fav_user_id'], 'snippet_id': snippet_id}))
    else:
        return redirect(reverse('snippet', kwargs={'snippet_id': snippet_id}))


################ POST A COMMENT ####################
def post_comment(request):
    # check if this is a POST request
    if request.method != 'POST':
        return redirect(reverse('home'))

    # check if there is an error
    if len(request.POST['comment'].strip()) == 0:
        messages.error(request, "You can't post an empty comment")

        # check the route to redirect to the right page
        if request.POST['page'] == 'profile':
            return redirect(reverse('profile', kwargs={'snippet_id': request.POST['snippet_id']}))
        elif request.POST['page'] == 'favorites':
            return redirect(reverse('favorites', kwargs={'fav_user_id':request.session['fav_user_id'], 'snippet_id': request.POST['snippet_id']}))
        else:
            return redirect(reverse('snippet', kwargs={'snippet_id': request.POST['snippet_id']}))
    
    # get the user that is posting the comment object
    try:
        user = User.objects.get(id = request.session['user_id'])
    except:
        return redirect(reverse('home'))

    # get the the snippet that was commented on object
    try:
        snippet = Snippet.objects.get(id = request.POST['snippet_id'])
    except:
        return redirect(reverse('home'))

    # get a commnet object
    comment = Comment.objects
    # post comment now
    comment.create(comment=request.POST['comment'], commenter=user, snippet=snippet)
    
    # redirect the page base on where the comment was made
    messages.success(request, "Comment Post it!")
    if request.POST['page'] == 'profile':
        return redirect(reverse('profile', kwargs={'snippet_id': snippet.id}))
    elif request.POST['page'] == 'favorites':
        return redirect(reverse('favorites', kwargs={'fav_user_id':request.session['fav_user_id'], 'snippet_id': snippet.id}))
    else:
        return redirect(reverse('snippet', kwargs={'snippet_id': snippet.id}))


################### SHOW A SNIPPET CODE #################
def snippet(request, snippet_id):
    # get this snippet code 
    try:
        snippet = Snippet.objects.get(id = snippet_id)
    except:
        return redirect(reverse('home'))

    # check if the logged in user favorited this snippet
    if 'user_id' in request.session:
        users = snippet.favorite_users.filter(id=request.session['user_id'])
    else:
        users = []
   
    # get all the snippets code languages except hmtl, css, javascript, python, mean, java
    navbar_languages = navigation_language()

    data = {
        'snippet': snippet,
        'navbar_languages': navbar_languages,
        'saved': len(users) == 1
    }
    return render(request, 'main/snippet.html', data)


############## PROCEED CONTRIBUTION #############
def process_contribute(request):
    # check if this is POST request
    if request.method != 'POST':
        return redirect(reverse('home'))

    # check for validation errors
    errors = Snippet.objects.basic_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)

        # record input information to request.session
        request.session['title'] = request.POST['title']
        request.session['language'] = request.POST['language']
        request.session['description'] = request.POST['description']
        request.session['snippet'] = request.POST['snippet']
        return redirect(reverse('contribute')) # redirect to the contribution page
    else:
        # no error proceed to submitting the data to the database
        # get the user object
        if 'user_id' in request.session:
            user = User.objects.get(id = int(request.session['user_id']))
        else:
            user = User.objects.get(id = 2) # get the anonymous user

        # get the input language
        if 'language_list' in request.POST:
            language = request.POST['language_list'].strip().lower()
        else:
            language = request.POST['language'].strip().lower()

        # get snippet objects
        snippet = Snippet.objects
        # create a new snippet now
        snippet.create(
            title = request.POST['title'].strip(),
            snippet = request.POST['snippet'].strip(),
            description = request.POST['description'].strip(),
            language = language,
            poster = user
        )
        
        # add this snippet code as this user favorite code
        snippet.last().favorite_users.add(user)

        # clear session without the login user
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            request.session.clear()
            request.session['user_id'] = user_id
        else:
            request.session.clear()

        messages.success(request, "Thank You for your contribution", extra_tags="contribution")
        return redirect(reverse('snippet', kwargs={'snippet_id': snippet.last().id}))


############## LOGOUT ####################
def logout(request):
    request.session.clear()
    return redirect(reverse('home'))


############## REGISTER NEW USER ###############
def register(request):
    if request.method != 'POST':
        return redirect(reverse('signup'))
    
    # check for validation errors
    errors = User.objects.basic_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        
        # record input information to request.session
        request.session['username'] = request.POST['username']
        request.session['email'] = request.POST['email']
        return redirect(reverse('signup')) # redirect back to signup page
    else:
        # at this point, there were no validation errors so process to creating a new user
        # hash the user password
        hash_pw = bcrypt.hashpw(request.POST['password'].strip().encode(), bcrypt.gensalt())
        user = User.objects # get an user object
        # create the user now
        user.create(
            username = request.POST['username'].strip(),
            email = request.POST['email'].strip().lower(),
            password = hash_pw
        )
        # new user has been successfully register
        request.session.clear()
        request.session['user_id'] = user.last().id # get the user id for login
        messages.success(request, "You have successfully registered", extra_tags="register")
        return redirect(reverse('home'))


############## LOGIN ################
def login(request):
    # check if this is a post request
    if request.method != 'POST':
        return redirect(reverse('home'))
    
    # check if this email exist in the data base
    user = User.objects.filter(email=request.POST['email'].strip().lower())
    if not user:
        messages.error(request, "Email or password invalid", extra_tags="login")
        # record input information to request.session
        request.session['email'] = request.POST['email']
        return redirect(reverse('signin')) # redirect back to signin page

    else:
        # no validation errors so proceed to the login in the user
        user = user[0] # since it is a list with only one element, get the first element
        if not bcrypt.checkpw(request.POST['password'].strip().encode(), user.password.encode()):
            # password did not match so redirect the user back to fix the error
            messages.error(request, '*Email or password is invalid', extra_tags='login')
            return redirect(reverse('signin')) # redirect back to signin page
        
        else:
            # password match so login the user
            request.session.clear()
            request.session['user_id'] = user.id
            return redirect(reverse('home'))



############### UPDATE PERSONAL INFORMATION ###########
def update_personal(request):
    # check if this is a POST request
    if request.method != 'POST':
        return redirect(reverse('home'))

    # check for validation errors
    errors = User.objects.update_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags="info_error")
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))

    # get the user object
    try:
        user = User.objects.get(id = request.session['user_id'])
    except:
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))
    
    # Update the user information
    user.username = request.POST['username'].strip()
    user.email = request.POST['email'].strip().lower()
    user.save()

    messages.error(request, "You have successfully updated your information", extra_tags="info_success")
    return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))



############### UPDATE PERSONAL PASSWORD ###########
def update_password(request):
    # check if this is a POST request
    if request.method != 'POST':
        return redirect(reverse('home'))

    # check for validation errors
    errors = User.objects.basic_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags="pass_error")
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))

    # get the user object
    try:
        user = User.objects.get(id = request.session['user_id'])
    except:
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))
    
    # check if the old password match the database
    if not bcrypt.checkpw(request.POST['old_password'].strip().encode(), user.password.encode()):
        messages.error(request, "Old password doesn't match!", "pass_error")
        return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))

    # at this point, there is no error, so Hash the user password first
    hash_pw = bcrypt.hashpw(request.POST['password'].strip().encode(), bcrypt.gensalt())
    user.password = hash_pw
    user.save()

    messages.error(request, "You have successfully updated your password!", extra_tags="pass_success")
    return redirect(reverse('profile', kwargs={'snippet_id': 'first'}))



############ RESET NEW PASSWORD #################
def reset_new_password(request):
    if 'reset_user_id' not in request.session:
        return redirect(reverse('signin'))
    
    # check if this a post request
    if request.method != 'POST':
        return redirect(reverse('signin'))

    # check for validation errors
    errors = User.objects.basic_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect(reverse('reset_password'))

    # get the user that need his password to be reset
    # get the user object
    try:
        user = User.objects.get(id = request.session['reset_user_id'])
    except:
        return redirect(reverse('signin'))
    
     # at this point, there is no error, so Hash the user password first
    hash_pw = bcrypt.hashpw(request.POST['password'].strip().encode(), bcrypt.gensalt())
    user.password = hash_pw
    user.save()

    messages.error(request, "Password successfully reset!", extra_tags="reset")
    return redirect(reverse('reset_password'))



############## CHECK PIN #############
def check_pin(request, pin):
    if 'try' not in request.session:
        request.session['try'] = 1
    else:
        request.session['try'] += 1

    # check if the user try more than 3 times 
    if request.session['try'] > 2:
        request.session.clear()
        return JsonResponse({'status': 'startover'})
    
    # check if the pin the match the session pin number
    if int(pin) != request.session['session_pin']:
        return JsonResponse({'status': 'wrong'})
    else:
        request.session['pin_is_check'] = 'True'
        return HttpResponse("pass")



############## RESET PASSWORD ##############
def reset_password(request):
    # check if this was a correct request
    # if it is a correct request, it should have a pin_is_check in session
    if 'pin_is_check' not in request.session:
        return redirect(reverse('signin'))
    return render(request, 'main/reset_password_form.html')