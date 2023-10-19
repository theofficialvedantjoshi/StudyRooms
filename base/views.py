from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Room,Topic,Message,Profile
from .forms import RoomForm,ProfileForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm




# Create your views here.

def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password is incorrect')
    context = {'page':page}
    return render(request, 'base/login_register.html',context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'


    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occured during registration')
    context = {'page':page,'form':form}
    
    return render(request, 'base/login_register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q)
                                | Q(name__icontains=q)
                                | Q(description__icontains=q))
    topics = Topic.objects.all()

    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    #room_messages_count = room_messages.
    context = {
        'rooms':rooms,
        'topics':topics,
        'room_count':room_count,
        'room_messages':room_messages,
        #'room_messages_count':room_messages_count,
    }
    return render(request, 'base/home.html',context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = request.POST.get('message')
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)

    context = {'room':room, 'room_messages':room_messages,'participants':participants}
    return render(request, 'base/room.html',context)
@login_required(login_url='login')
def userProfile(request,pk):
    user = User.objects.get(id=pk)

    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    try:
        profile = Profile.objects.get(id=pk)
    except:
        profile = Profile.objects.create(user=user)
        profile.save()
    context ={'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics,'profile':profile}
    return render(request, 'base/profile.html',context)
@login_required(login_url='login')
def updateProfile(request,pk):
    profile = Profile.objects.get(id=pk)
    form = ProfileForm(instance=profile)
    if request.user != profile.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST,instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('user-profile',pk=request.user.id)
    context = {'form':form}
    return render(request, 'base/profile_form.html',context)
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('/')
    context = {'form':form}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form':form}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        room.delete()
        return redirect('/')
    return render(request, 'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        message.delete()
        return redirect('/')
    return render(request, 'base/delete.html',{'obj':message})
