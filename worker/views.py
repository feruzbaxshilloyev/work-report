from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

from manager.models import Message, ManagerProfile
from .forms import WorkerEditForm, CustomPasswordChangeForm
from .models import Worker, ChatMessage
from django.contrib import messages


def log(worker):
    return worker.is_login


def worker_profile_view(request, worker_id):
    worker = get_object_or_404(Worker, worker_id=worker_id)
    if not log(worker):
        return redirect('profil:sorov')
    daily_works = worker.daily_works.order_by('-sana')
    return render(request, 'worker_profile.html', {
        'worker': worker,
        'daily_works': daily_works
    })


def worker_login_view(request):
    if request.method == 'POST':
        worker_id = request.POST.get('worker_id')
        password = request.POST.get('password')

        try:
            worker = Worker.objects.get(worker_id=worker_id)
            if worker.password == password:
                request.session['worker_id'] = worker.worker_id
                worker.is_login = True
                worker.save()
                return redirect('worker:worker_profile', worker_id=worker.worker_id)
            else:
                messages.error(request, 'Parol noto‘g‘ri.')
        except Worker.DoesNotExist:
            messages.error(request, 'Bunday IDdagi ishchi topilmadi.')

    return render(request, 'w_login.html')


def worker_home(request, id):
    worker = get_object_or_404(Worker, worker_id=id)
    if not log(worker):
        return redirect('profil:sorov')
    ctx = {
        'worker': worker
    }
    return render(request, 'home.html', ctx)


def worker_logout(request, worker_id):
    worker = Worker.objects.filter(worker_id=worker_id).first()
    if not log(worker):
        return redirect('profil:sorov')
    worker.is_login = False
    worker.save()
    return redirect('profil:sorov')


def edit_profile(request):
    worker = request.user
    if not log(worker):
        return redirect('profil:sorov')
    if request.method == 'POST':
        image_form = WorkerEditForm(request.POST, request.FILES, instance=worker)
        password_form = CustomPasswordChangeForm(worker, request.POST)
        if image_form.is_valid() and password_form.is_valid():
            image_form.save()
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('worker:profile')
    else:
        image_form = WorkerEditForm(instance=worker)
        password_form = CustomPasswordChangeForm(worker)
    return render(request, 'edit_w_profile.html', {
        'image_form': image_form,
        'password_form': password_form
    })


def worker_messages_view(request, id):
    worker = Worker.objects.get(worker_id=id)
    if not log(worker):
        return redirect('profil:sorov')
    mess = Message.objects.filter(manager=worker.manager).order_by('-created_at')
    return render(request, 'messages.html', {'messages': mess, 'worker': worker})


def chat_view(request, receiver_id, w_id):
    receiver = get_object_or_404(User, id=receiver_id)
    worker = Worker.objects.filter(worker_id=w_id).first()
    messages = ChatMessage.objects.filter(
        Q(sender=receiver, receiver=worker.ism+' '+worker.familiya+str(worker.worker_id)) |
        Q(sender=worker.ism+' '+worker.familiya+str(worker.worker_id), receiver=receiver)
    ).order_by('created_at')
    if request.method == 'POST':
        text = request.POST.get('message')
        if text:
            ChatMessage.objects.create(
                sender=worker.ism+' '+worker.familiya+str(worker.worker_id),
                receiver=receiver,
                message=text
            )
            return redirect('worker:chat', receiver_id=receiver.id, w_id=worker.worker_id)

    return render(request, 'chat.html', {
        'messages': messages,
        'receiver': receiver,
        'worker': worker,
    })


def chat_user_list(request, worker_id):
    worker = get_object_or_404(Worker, worker_id=worker_id)
    messages = ChatMessage.objects.filter(Q(sender=worker) | Q(receiver=worker)).distinct()

    users = set()

    for msg in messages:
        if msg.sender != worker:
            if isinstance(msg.sender, Worker):
                users.add((msg.sender.worker_id, f"{msg.sender.ism} {msg.sender.familiya}"))
            elif isinstance(msg.sender, User):
                users.add((msg.sender.id, msg.sender.username))

        if msg.receiver != worker:
            if isinstance(msg.receiver, Worker):
                users.add((msg.receiver.worker_id, f"{msg.receiver.ism} {msg.receiver.familiya}"))
            elif isinstance(msg.receiver, User):
                users.add((msg.receiver.id, msg.receiver.username))

    return render(request, 'chat_users.html', {
        'users': users,
        'worker': worker
    })


def update_password(request, worker_id):
    worker = get_object_or_404(Worker, worker_id=worker_id)

    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Parollar mos emas!")
        elif len(new_password) < 6:
            messages.error(request, "Parol kamida 6 ta belgidan iborat bo‘lishi kerak.")
        else:
            worker.password = new_password
            worker.save()
            messages.success(request, "Parol muvaffaqiyatli yangilandi!")
            return redirect('worker:home', id=worker.worker_id)  # yoki kerakli sahifaga

    return render(request, 'update_password.html', {'worker': worker})
# def message_detail(request, id):
#     msg = get_object_or_404(Message, id=id)
#
#     if not msg.is_view:
#         msg.is_view = True
#         msg.save()
#
#     return render(request, 'message_detail.html', {'msg': msg})
