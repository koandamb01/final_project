from __future__ import unicode_literals
from django.db import models
from datetime import datetime
import re
from time import gmtime, strftime

# create a regular expression object that we can use run operations on
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
WORD_SPACE_REGEX = re.compile(r'^[A-Za-z ]+')


class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        # validation for username
        if 'username' in postData:
            if len(postData['username'].strip()) == 0:
                errors['username'] = "*Username is required"
            elif len(postData['username'].strip()) < 3:
                errors['username'] = "*Username must be at least 3 characters"
            elif User.objects.filter(username=postData['username'].strip()):
                errors['username'] = "*Username already exist"

        # validation for email
        if 'email' in postData:
            if len(postData['email'].strip().lower()) == 0:
                errors['email'] = "*Email is required"
            elif not EMAIL_REGEX.match(postData['email'].strip().lower()):
                errors['email'] = "*Email is Invalid"
            elif User.objects.filter(email=postData['email'].strip().lower()):
                errors['username'] = "*Email already exist"

        # validation for password
        if 'password' in postData:
            if len(postData['password'].strip()) == 0:
                errors['password'] = "*Password is required"
            elif len(postData['password'].strip()) < 8:
                errors['password'] = "*Password must be at least 8 characters"
            elif postData['password'].strip() != postData['confirm_password'].strip():
                errors['password'] = "*Password must be match"
        return errors

    def update_validator(self, postData):
        errors = {}
        # validation for username
        if 'username' in postData:
            if len(postData['username'].strip()) == 0:
                errors['username'] = "*Username is required"
            elif len(postData['username'].strip()) < 3:
                errors['username'] = "*Username must be at least 3 characters"
            elif User.objects.filter(username=postData['username'].strip()).exclude(username=postData['username'].strip()):
                errors['username'] = "*Username already exist"

        # validation for email
        if 'email' in postData:
            if len(postData['email'].strip().lower()) == 0:
                errors['email'] = "*Email is required"
            elif not EMAIL_REGEX.match(postData['email'].strip().lower()):
                errors['email'] = "*Email is Invalid"
            elif User.objects.filter(email=postData['email'].strip().lower()).exclude(email=postData['email'].strip().lower()):
                errors['username'] = "*Email already exist"
        return errors


class SnippetManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        # validation for title
        if len(postData['title'].strip()) == 0:
            errors['title'] = "*Title is required"
        elif len(postData['title'].strip()) < 10:
            errors['title'] = "*Title must be at least 10 characters"
        
        
        # validation for language
        if 'language_list' not in postData and len(postData['language'].strip().lower()) == 0:
            errors['language'] = "*Snippet language is required"
        elif 'language_list' in postData and len(postData['language'].strip().lower()) != 0:
            errors['language'] = "*You cannot select two languages"
        # elif 'language_list' not in postData and len(postData['language'].strip().lower()) == 0:
        #     errors['language_list'] = "*Snippet language is required"


        # validation for description
        if len(postData['description'].strip()) == 0:
            errors['description'] = "*Description is required"
        elif len(postData['description'].strip()) < 10:
            errors['description'] = "*Description must be at least 10 characters"

        # validation for snippet
        if len(postData['snippet'].strip()) == 0:
            errors['snippet'] = "*Snippet is required"
        
        return errors


class CommentManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        # validation for title
        if len(postData['comment'].strip()) == 0:
            errors['comment'] = "*Comment is required"

        return errors


class User(models.Model):
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    user_level = models.IntegerField(default=0)
    account_status = models.IntegerField(default=1)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

class Snippet(models.Model):
    title = models.CharField(max_length=255)
    snippet = models.TextField()
    description = models.TextField()
    language = models.CharField(max_length=100)
    poster = models.ForeignKey(User, related_name="posted_snippets")
    favorite_users = models.ManyToManyField(User, related_name="favorite_snippets")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = SnippetManager()

class Comment(models.Model):
    comment = models.TextField()
    commenter = models.ForeignKey(User, related_name="user_comments")
    snippet = models.ForeignKey(Snippet, related_name="snippet_comments")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = CommentManager()

