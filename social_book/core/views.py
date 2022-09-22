
from cmath import log
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages,auth

from .models import Profile, Post, LikePost, Followerscount

# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_profile = Profile.objects.get(user=request.user)

    # get all posts feed that the current user following
    user = request.user.username
    follow_pairs = Followerscount.objects.filter(follower=user)
    following_users = []
    for follow in follow_pairs:
        following_users.append(follow.user)
    following_users_whole_model = [user for user in User.objects.all() if user.username in following_users]
    
    posts_list=[]
    for following_user in following_users:
        posts = Post.objects.filter(user=following_user)
        posts_list.append(posts)

    all_posts_array=[p for posts in posts_list for p in posts]

    # get suggestions for 'to follow' right side box
    users_not_following = [user for user in User.objects.all() if user not in following_users_whole_model]
    users_not_following = [user for user in users_not_following if user != request.user]
    print(f'length of Not FOLLOWING: {len(users_not_following)}')
    suggested_profiles = [ profile for profile in Profile.objects.all() if profile.user in users_not_following]
    return render(request,'index.html', {'user_profile': user_profile, 'posts': all_posts_array, 'suggested_profiles': suggested_profiles})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'This email has been taken')
                return redirect('signup')
            elif User.objects.filter(username = username).exists():
                messages.info(request, 'This Username has been taken' )
                return redirect('signup')
            else: 
                user = User.objects.create_user(username = username, email= email, password = password)
                user.save()    

                # create a new profile object from this new user
                new_user = User.objects.get(username = username)
                new_profile = Profile.objects.create(user = new_user, id_user=new_user.id)
                new_profile.save()

                # log user in and redirect to setting page
                user_logedin = auth.authenticate(username=username, password=password)
                auth.login(request, user_logedin) 
                return redirect('setting')

        else:
            messages.info(request, 'Passords not matching')
            return redirect('signup')


    else: 
        return render(request, 'signup.html')

def signin(request):
    if request.method == "POST":
        username= request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials invalid, please try again')
            return redirect('signin')
    return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def setting(request):
    # get the profile object from this user
    user_profile = Profile.objects.get(user=request.user)

    if request.method== "POST":
        user_profile.bio = request.POST['bio']
        user_profile.location = request.POST['location']
        if request.FILES.get('image'):
            user_profile.profileimg = request.FILES.get('image')
            
        user_profile.save()
        return redirect('/setting')

    return render(request, 'setting.html', {"user_profile":user_profile})


@login_required(login_url='signin')
def upload(request):
    user = request.user.username
    if request.method == 'POST':
        caption = request.POST.get('caption')
        image = request.FILES.get('image_upload')
        if caption and image:
            post = Post.objects.create(user=user, caption=caption, image=image)
            post.save()
            return redirect('/')
    return redirect('/')

@login_required(login_url='signin')
def like_post(request):  
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    user = request.user.username
    # check if this user has liked this post
    like = LikePost.objects.filter(post_id = post_id, username = user)
    if not like:
        likepost = LikePost.objects.create(post_id=post_id, username=user)
        likepost.save()    
        post.no_of_likes += 1
        post.save()
        return redirect('/')
    return redirect('/')


@login_required(login_url='signin')
def profile(request, username):
    current_user = request.user.username
    user_object = User.objects.get(username = username)
    user_profile =  Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user=username)
    user_post_length = len(user_posts)
    user_followers = Followerscount.objects.filter(user=username)
    user_followers_count = user_followers.count()

    
    user_following = Followerscount.objects.filter(follower=username)

    following_users = []
    for follow in user_following:
        following_users.append(follow.user)
    following_users_whole_model = [user for user in User.objects.all() if user.username in following_users]
    following_profiles = [ profile for profile in Profile.objects.all() if profile.user in following_users_whole_model]
    
    user_following_count= user_following.count()
    followed=False
    button_text='follow'
    follow_count= Followerscount.objects.filter(follower=current_user, user=username)
    if follow_count:
        followed = True
        button_text = 'unfollow'
    # rotate button_text
   
    context = {
        'user_object':user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'followed': followed,
        'user_followers': user_followers_count,
        'user_following': user_following_count, 
        'user_I_am_following': following_profiles,
        'user_I_am_followed': user_followers,

    }

    return render(request, 'profile.html', context=context)
    
@login_required(login_url='signin')
def follow(request):
    current_user = request.user.username
    if request.method == 'POST':
        user_to_be_followed = request.POST.get('user')
        new_follow = Followerscount.objects.filter(follower=current_user, user=user_to_be_followed).first()
        if not new_follow:
           
            new_fol = Followerscount.objects.create(follower=current_user, user=user_to_be_followed)
            new_fol.save()
            return redirect('/profile/'+user_to_be_followed) 
        else:
            new_follow.delete()
    return redirect('/profile/'+ user_to_be_followed)

@login_required(login_url='signin')
def search(request):
    user_profile = Profile.objects.get(user = request.user)
    if request.method=='POST':
        searched_username = request.POST.get('username')
        if searched_username:
            # users = User.objects.filter(username__icontains = searched_username)   
            profiles = Profile.objects.filter(user__username__icontains=searched_username)         
            context = {
                'user_profile':user_profile,
                'username': searched_username,
                'profiles':profiles,
            }
            return render(request, 'search.html', context)
        else:
            return redirect('/')
    return redirect('/')
    
    


