from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

from manager.models import Message, ManagerProfile, MonthlyPayment
from .forms import WorkerEditForm, CustomPasswordChangeForm
from .models import Worker, ChatMessage
from django.contrib import messages


def log(worker):
    return worker.is_login


def worker_profile_view(request, worker_id):
    worker = get_object_or_404(Worker, worker_id=worker_id)
    if not log(worker):  # log funksiyasi sizning logikangizga bog'liq
        return redirect('profil:sorov')
    unread = ChatMessage.objects.filter(
        receiver=(worker.ism+' '+worker.familiya+str(worker.worker_id))
    ).exclude(is_read=True).count()

    # O'qilmagan xabarlar sonini hisoblash
    unread_count = Message.objects.filter(
        manager=worker.manager
    ).exclude(views=worker).count()

    # Agar o'qilmagan xabarlar bo'lsa, bildirishnoma yuborish
    if unread_count > 0:
        messages.info(request, f"Sizda {unread_count} ta o'qilmagan xabar bor!")

    # Ishchining kundalik ishlari
    daily_works = worker.daily_works.order_by('-sana')

    # Paginator qo'shish
    paginator = Paginator(daily_works, 8)  # Har sahifada 10 ta yozuv
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'worker_profile.html', {
        'unread': unread,
        'unread_count': unread_count,
        'worker': worker,
        'page_obj': page_obj,  # daily_works o'rniga page_obj
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
    worker = Worker.objects.filter(worker_id=id).first()
    man = worker.manager
    if not log(worker):  # log funksiyasi sizning logikangizga bog'liq
        return redirect('profil:sorov')

    # Manager ga tegishli xabarlar
    messages = Message.objects.filter(manager=worker.manager).order_by('-created_at')

    # O'qilmagan xabarlar sonini hisoblash
    unread_count = Message.objects.filter(manager=worker.manager).exclude(views=worker).count()

    # Har bir xabar uchun ko'rilgan/ko'rilmagan holatni aniqlash
    ms = {}
    for message in messages:
        ms[message] = worker in message.views.all()
        if worker not in message.views.all():
            message.add_view(worker)

    ctx = {
        'ms': ms,
        'man': man,
        'messages': messages,
        'worker': worker,
        'unread_count': unread_count,
    }

    return render(request, 'messages.html', ctx)


def chat_view(request, receiver_id, w_id):
    receiver = get_object_or_404(User, id=receiver_id)
    worker = Worker.objects.filter(worker_id=w_id).first()
    messages = ChatMessage.objects.filter(
        Q(sender=receiver, receiver=worker.ism + ' ' + worker.familiya + str(worker.worker_id)) |
        Q(sender=worker.ism + ' ' + worker.familiya + str(worker.worker_id), receiver=receiver)
    ).order_by('created_at')
    for i in messages:
        if i.sender == receiver.username:
            i.is_read = True
            i.save()
    if request.method == 'POST':
        text = request.POST.get('message')
        if text:
            ChatMessage.objects.create(
                sender=worker.ism + ' ' + worker.familiya + str(worker.worker_id),
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
    ab = worker.ism + ' ' + worker.familiya + str(worker.worker_id)
    messages = ChatMessage.objects.filter(Q(sender=ab) | Q(receiver=ab)).distinct()
    al = [i.ism+' '+i.familiya+str(i.worker_id) for i in Worker.objects.all()]
    users = set()
    for msg in messages:
        if msg.sender != ab and msg.sender in al:
            # if msg.sender in al:
            #     ii = User.objects.filter(username=msg.sender).first()
            #     users.add((msg.sender, ii))
            a = str(msg.sender).split()

            users.add((f"{a[0]} {a[1][:-5]}", a[1][-5:]))

        if msg.receiver != ab and msg.receiver in al:
            # if msg.receiver in al:
            #     ii = User.objects.filter(username=msg.receiver).first()
            #     users.add((msg.receiver, ii))
            a = str(msg.receiver).split()
            users.add((f"{a[0]} {a[1][:-5]}", a[1][-5:]))
    uss = {}
    for i in users:
        i = list(i)
        uss[i[0]] = int(i[1])

    for i, u in uss.items():
        wr = Worker.objects.filter(worker_id=u).first()
        ad = wr.ism+' '+wr.familiya+str(wr.worker_id)
        mes = ChatMessage.objects.filter(sender=ad, is_read=False).count()
        uss.update({i: {u: mes}})
    ctx = {
        'uss': uss,
        'users': users,
        'worker': worker
    }
    return render(request, 'chat_users.html', ctx)


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


def edit_message(request, message_id):
    try:
        message = ChatMessage.objects.get(id=message_id, sender=request.user.username)
        r = message.receiver

        if request.method == "POST":
            new_text = request.POST.get('message')
            if not new_text:
                return render(request, 'e_mes.html', {
                    'message_id': message_id,
                    'message_text': message.message,
                    'error': "Xabar bo'sh bo'lishi mumkin emas"
                })
            message.message = new_text
            message.save()
            return redirect('manager:m_chat', id=int(r[-5:]))

        return render(request, 'e_mes.html', {
            'message_id': message_id,
            'message_text': message.message
        })
    except ChatMessage.DoesNotExist:
        return redirect('worker:chat_users')  # Xabar topilmasa chatga qaytarish


def delete_message(request, message_id):
    try:
        users = User.objects.all()
        message = ChatMessage.objects.get(id=message_id)
        if message.sender in users:
            raise "Xatolik"

        r = message.receiver
        s = message.sender
        if request.method == "POST":
            message.delete()
            return redirect('worker:chat', receiver_id=r.id, w_id=s.worker_id)
        rec = int(r[-5:])
        return render(request, 'd_mes.html', {
            'r_id': rec,
            'message_id': message_id,
            'message_text': message.message
        })
    except ChatMessage.DoesNotExist:
        return redirect('worker:chat_users', worker_id=s.worker_id)


def w_chat(request, w_id, id):
    # Joriy ishchi (me) va suhbatdosh (you)
    me = get_object_or_404(Worker, worker_id=id)
    you = get_object_or_404(Worker, worker_id=w_id)
    m_m = me.ism + ' ' + me.familiya + str(me.worker_id)
    y_m = you.ism + ' ' + you.familiya + str(you.worker_id)

    # Autentifikatsiya tekshiruvi
    if not log(me):  # log funksiyasi sizning logikangizga bog'liq
        return redirect('profil:sorov')

    # Ikki worker o'rtasidagi xabarlar
    sms = ChatMessage.objects.filter(
        Q(sender=m_m, receiver=y_m) | Q(sender=y_m, receiver=m_m)
    ).order_by('created_at')

    # O'qilmagan xabarlar sonini hisoblash
    unread_count = sms.filter(receiver=m_m, is_read=False).count()

    # Agar o'qilmagan xabarlar bo'lsa, bildirishnoma
    if unread_count > 0:
        messages.info(request, f"Sizda {unread_count} ta o'qilmagan xabar bor!")

    # Yangi xabar yuborish
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(
                sender=m_m,
                receiver=y_m,
                message=message_text
            )
            return redirect('worker:ww_chat', w_id=you.worker_id, id=me.worker_id)

    # Xabarlarni o'qilgan deb belgilash
    sms.filter(receiver=m_m, is_read=False).update(is_read=True)

    return render(request, 'ww_chat.html', {
        'me': me,
        'you': you,
        'mm': m_m,
        'ym': y_m,
        'sms': sms,
        'unread_count': unread_count,
    })


def w_search(request, worker_id):
    # Joriy ishchi
    worker = get_object_or_404(Worker, worker_id=worker_id)

    # Autentifikatsiya tekshiruvi
    if not log(worker):  # log funksiyasi sizning logikangizga bog'liq
        return redirect('profil:sorov')

    # Qidiruv so'rovi
    query = request.GET.get('q', '')
    workers = Worker.objects.filter(manager=worker.manager).exclude(worker_id=worker_id)
    if query:
        workers = workers.filter(
            Q(ism__icontains=query) | Q(familiya__icontains=query) | Q(worker_id__icontains=query)
        )

    # O'qilmagan xabarlar sonini hisoblash (barcha chat xabarlari uchun)
    unread_count = ChatMessage.objects.filter(
        receiver=worker, is_read=False
    ).count()

    # Agar o'qilmagan xabarlar bo'lsa, bildirishnoma
    if unread_count > 0:
        messages.info(request, f"Sizda {unread_count} ta o'qilmagan xabar bor!")

    return render(request, 'w_search.html', {
        'worker': worker,
        'workers': workers,
        'unread_count': unread_count,
        'query': query,
    })


def message_detail(request, id, d):
    msg = Message.objects.filter(id=id).first()
    return render(request, 'message_detail.html', {'msg': msg, 'd': d})


def tolov_tarixi(request, id):
    worker = Worker.objects.filter(worker_id=id).first()
    tolovlar = MonthlyPayment.objects.filter(worker=worker).order_by('-sana')

    return render(request, 'tolov_tarixi.html', {'tolovlar': tolovlar, 'worker': worker})

