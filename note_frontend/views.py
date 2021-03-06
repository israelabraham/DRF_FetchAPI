from django.shortcuts import render, redirect
from .models import Note
from .forms import NoteCreateForm, NoteUpdateForm, \
    CreateUserForm, LogUserForm, UpdateProfileForm, \
        UpdateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    notes = Note.objects.filter(
        author__username=request.user
    )[:3]
    context = {
        'notes': notes
    }
    return render(request, "note_frontend/home.html", context)


@login_required
def create_thought(request):
    form = NoteCreateForm()
    print(request.user)

    if request.method == "POST":
        
        form = NoteCreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            thought = form.cleaned_data.get("thought")
            print(title, thought)
            note = Note(
                title=title,
                thought=thought,
                author=request.user,
            )
            note.save()
            messages.success(request, f"Yes, {request.user.username}, you finally published your thought.")
            return redirect("note:home")
        return redirect("note:new-thought")

    context = {
        'form': form
    }
    return render(request, "note_frontend/write-thought.html", context)


@login_required
def update_thought(request, pk):
    try:
        note = Note.objects.get(id=pk)
    except Note.DoesNotExist:
        return redirect("note:home")

    form = NoteUpdateForm(instance=note)

    if request.method == "POST":
        form = NoteUpdateForm(data=request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect("note:home")
        return redirect("note:home")

    context = {
        'form': form
    }
    return render(request, "note_frontend/edit-thought.html", context)


@login_required
def delete_thought(request, pk):
    """
    This view delete a single note
    """
    try:
        note = Note.objects.get(id=pk)
        note.delete()
        messages.success(request, f"{note} has successfully been deleted.")
        return redirect("note:home")
    except Note.DoesNotExist:
        return redirect("note:home")


@login_required
def confirm_delete(request, pk):
    note = Note.objects.get(id=pk)

    """
    Calls the delete_thought logic
    """
    delete_thought(request, pk)

    context = {
        'note': note
    }
    return render(request, "note_frontend/confirm-delete.html", context)


def logout_page(request):
    logout(request)
    return redirect("note:login")


def login_page(request):
    form = LogUserForm()

    if request.method == "POST":
        form = LogUserForm(request.POST)
        if form.is_valid():
            print(form)
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(
                request, username=username, password=password
            )

            if user is not None:
                login(request, user)
                messages.success(request, f"{username}, you are logged in.")
                return redirect("note:profile")
            messages.error(request, f"Oops, the username {username} does not exist in our database. Please try again.")
        return redirect("note:login")

    context = {
        'form': form
    }

    return render(request, "note_frontend/login.html", context)


def register_page(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has successfully been created.")
            return redirect("note:login")
        return redirect("note:register")

    context = {
        'form': form
    }

    return render(request, "note_frontend/register.html", context)


@login_required
def profile_page(request):
    u_form = UpdateUserForm(instance=request.user)
    p_form = UpdateProfileForm(instance=request.user.profile)

    if request.method == "POST":
        p_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        u_form = UpdateUserForm(instance=request.user, data=request.POST)

        if p_form.is_valid() and u_form.is_valid():
            username = u_form.cleaned_data.get("username")
            p_form.user = username
            p_form.save()
            messages.success(request, f"{username}, you profile has successfully been updated.")
            return redirect("note:profile")
        return redirect("note:profile")

    context = {
        'p_form': p_form,
        'u_form': u_form
    }

    return render(request, "note_frontend/profile.html", context)
