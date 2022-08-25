from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import *
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def index(request):
    Posts = Post.objects.all().order_by("-timestamp")

    paginator = Paginator(Posts, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    print(Posts)


    context={'page_obj': page_obj}
    return render(request, "network/allpost.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            Posts = Post.objects.all().order_by("-timestamp")

            paginator = Paginator(Posts, 10) # Show 25 contacts per page.

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context={'page_obj': page_obj}
            return render(request, "network/allpost.html", context)
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    Posts = Post.objects.all().order_by("-timestamp")

    paginator = Paginator(Posts, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={'page_obj': page_obj}
    return render(request, "network/allpost.html", context)


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            profile = Profile(user = user)
            profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url="login")
def createPost(request):

    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        posts = request.POST["Post"]
        form = Post(post = posts, timestamp = datetime.datetime.now()  , user= profile)
        form.save()

    Posts = Post.objects.all().order_by("-timestamp")

    paginator = Paginator(Posts, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={'page_obj': page_obj}
    return render(request, 'network/allpost.html', context)

def userProfile(request,pk):
    userProf = get_object_or_404(Profile, id=pk)
    profilesPosts = Post.objects.filter(user= userProf).all()

    followed = False
    if userProf.follower.filter(id = request.user.id).exists():
        followed = True

    paginator = Paginator(profilesPosts, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={'followed':followed, 'userProf':userProf, 'page_obj': page_obj, 'pk':pk}
    return render(request, 'network/userProfile.html', context)

@login_required(login_url="login")
def followProfile(request, pk):
    Prof = get_object_or_404(Profile, id = request.POST.get('userProf_id'))
    followed = False
    if Prof.follower.filter(id = request.user.id).exists():
        Prof.follower.remove(request.user)
        followed = False
    else:
        Prof.follower.add(request.user)
        followed = True

    return HttpResponseRedirect(reverse('userProfile', args=[str(pk)]))

@login_required(login_url="login")
def following(request):
    allFollowingProfiles = get_object_or_404(Profile, follower = request.user)
    allPostsThatUserFollows = Post.objects.filter(user= allFollowingProfiles)

    paginator = Paginator(allPostsThatUserFollows, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={'page_obj': page_obj}
    return render(request, 'network/following.html', context)

@login_required
@csrf_exempt
def like(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        is_liked = request.POST.get('is_liked')
        try:
            post = Post.objects.get(id=post_id)
            if is_liked == 'no':
                post.like.add(request.user)
                is_liked = 'yes'
            elif is_liked == 'yes':
                post.like.remove(request.user)
                is_liked = 'no'
            post.save()

            return JsonResponse({'like_count': post.like.count(), 'is_liked': is_liked, "status": 201})
        except:
            return JsonResponse({'error': "Post not found", "status": 404})
    return JsonResponse({}, status=400)

@login_required
@csrf_exempt
def edit_post(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        new_post = request.POST.get('post')
        try:
            post = Post.objects.get(id=post_id)
            if post.user.user == request.user:
                post.post = new_post.strip()
                post.save()
                return JsonResponse({}, status=201)
        except:
            return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)
