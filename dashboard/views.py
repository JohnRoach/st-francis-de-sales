from blog.models import Post
from django.conf import settings as django_settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
import requests

@login_required
def index(request):
    context = {
        'meta_description': 'This is the meta description',
        'page_name': 'dashboard'
    }
    return render(request, 'dashboard/index.html', context)

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/dashboard')

def login_user(request):

    google_captcha_public_key = django_settings.GOOGLE_CAPTCHA_PUBLIC

    if request.method == 'POST':
        google_captcha_private_key = django_settings.GOOGLE_CAPTCHA_PRIVATE
        data = request.POST
        username = data['email']
        password = data['password']
        captcha_rs = data.get('g-recaptcha-response')
        url = "https://www.google.com/recaptcha/api/siteverify"
        params = {
            'secret': google_captcha_private_key,
            'response': captcha_rs,
            'remoteip': get_client_ip(request)
        }
        response = {}
        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()
        response["status"] = verify_rs.get("success", False)
        if response["status"]:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
        return HttpResponseRedirect('/dashboard')

    context = {
        'meta_description': 'This is the meta description',
        'page_name': 'login',
        'google_captcha_public_key': google_captcha_public_key,
    }
    return render(request, 'dashboard/login.html', context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def posts(request):
    if request.method == 'POST':
        data = request.POST

    all_blog_posts = Post.objects.order_by('-date').all()
    context = {
        'page_name': 'posts',
        'posts': all_blog_posts,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def post(request, post_id):
    if request.method == 'POST':
        data = request.POST
        title = data['title']
        text = data['text']
        post_id = data['id']

        post = Post.objects.get(id=post_id)
        post.title = title
        post.text = text
        post.save()
        return HttpResponseRedirect('/dashboard/posts/post/' + str(post_id))

    try:
        blog_post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        raise Http404()
    context = {
        'page_name': 'post',
        'post': blog_post,
    }
    return render(request, 'dashboard/index.html', context)
