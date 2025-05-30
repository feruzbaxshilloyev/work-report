from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from .forms import ManagerRegisterForm, ManagerLoginForm, MessageForm, MonthlyPaymentForm, TolowForm, \
    ChangeManagerProfileForm, CustomSetPasswordForm
from django.contrib import messages
from worker.models import Worker, DailyWork, ChatMessage
from .models import ManagerProfile, MonthlyPayment
from django.utils import timezone
from django.db.models import Sum
from django.utils.dateparse import parse_date


def manager_register(request):
    if request.method == 'POST':
        form = ManagerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('manager:profil')
    else:
        form = ManagerRegisterForm()
    return render(request, 'regis.html', {'form': form})


def manager_login(request):
    if request.method == 'POST':
        form = ManagerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('manager:profil')
    else:
        form = ManagerLoginForm()
    return render(request, 'm_login.html', {'form': form})


@login_required
def manager_profile(request):
    manager = ManagerProfile.objects.filter(user=request.user).first()
    ctx = {
        'manager': manager
    }
    return render(request, 'm_profil.html', ctx)


@login_required
def logout_view(request):
    logout(request)
    return redirect('profil:sorov')


def add_worker(request):
    if request.method == 'POST':
        ism = request.POST.get('ism')
        familiya = request.POST.get('familiya')
        try:
            worker = Worker.objects.create(
                ism=ism,
                familiya=familiya,
                manager=request.user
            )
            worker.save()

            messages.success(request, f"Ishchi {worker.ism} muvaffaqiyatli qo‘shildi! Parol: {worker.password}")
            print(f"Ishchi {worker.ism} muvaffaqiyatli qo‘shildi! Parol: {worker.password}")
            return redirect('manager:profil')
        except Exception as e:
            print(e)
            messages.error(request, f"Ishchi qo‘shishda xato: {e}")

    return render(request, 'add_worker.html')


def worker_list(request):
    workers = Worker.objects.filter(manager=request.user)

    return render(request, 'worker_list.html', {'workers': workers})


@login_required
def home(request):
    workers = Worker.objects.filter(manager=request.user)
    manager = request.user
    wk = [i.ism + ' ' + i.familiya + str(i.worker_id) for i in workers]
    msss = ChatMessage.objects.filter(sender__in=wk, is_read=False)
    st = set()
    for i in msss:
        st.add(i.sender)

    worker_stats = []
    wun = -1
    for _ in st:
        wun += 1
    print(wun)
    for worker in workers:
        kunliklar = DailyWork.objects.filter(worker=worker)
        jami_mahsulot = sum([float(d.umumiy_mahsulot) for d in kunliklar])
        jami_sifatsiz = sum([d.sifatsiz_mahsulot for d in kunliklar])
        jami_haqi = sum([d.hisoblangan_haqi for d in kunliklar])
        sof = float(jami_mahsulot) - float(jami_sifatsiz)
        vaznlar = len([float(d.umumiy_mahsulot) for d in kunliklar])
        worker_stats.append({
            'worker': worker,
            'mahsulot': jami_mahsulot,
            'sifatsiz': jami_sifatsiz,
            'kunlik_haqi': jami_haqi,
            'sof': str(sof),
            'vaznlar': vaznlar
        })

    ctx = {
        'wun': wun,
        'worker_stats': worker_stats,
        'manager': manager
    }
    return render(request, 'm_home.html', ctx)


@login_required
def add_daily_work(request):
    workers = Worker.objects.filter(manager=request.user)

    if request.method == 'POST':
        worker_id = request.POST['worker_id']
        product_weights = request.POST['product_weights']
        bad_weight = float(request.POST['bad_weight'])
        price_per_kg = float(request.POST['price_per_kg'])

        # Sana POSTdan olinadi, bo‘sh bo‘lsa hozirgi sanani oladi
        sana_str = request.POST.get('sana')
        if sana_str:
            sana = timezone.datetime.strptime(sana_str, '%Y-%m-%d').date()
        else:
            sana = timezone.now().date()

        try:
            weight_list = [float(w) for w in product_weights.strip().split()]
        except ValueError:
            return render(request, 'add_daily_work.html', {
                'workers': workers,
                'error': 'Faqat raqamli qiymatlar kiriting!'
            })

        total_weight = sum(weight_list)
        worker = Worker.objects.get(id=worker_id)
        sf = total_weight - bad_weight
        pul = sf * price_per_kg
        worker.ishlangan += pul
        qoldiq = worker.ishlangan - worker.tolangan
        worker.qoldiq = qoldiq
        worker.save()
        dail = DailyWork.objects.create(
            worker=worker,
            umumiy_mahsulot=total_weight,
            sifatsiz_mahsulot=bad_weight,
            narx_per_kg=price_per_kg,
            sana=sana  # Sana qo‘shildi
        )
        dail.alohida = weight_list
        dail.save()

        return redirect('manager:home')
    ctx = {
        'workers': workers,
    }
    return render(request, 'add_daily_work.html', ctx)


@login_required()
def worker_detail(request, worker_id):
    worker = get_object_or_404(Worker, id=worker_id, manager=request.user)
    ishlar = DailyWork.objects.filter(worker=worker).order_by('-sana')
    tolovlar = MonthlyPayment.objects.filter(worker=worker).order_by('-created')
    context = {
        'tolovlar': tolovlar,
        'worker': worker,
        'ishlar': ishlar,
    }
    return render(request, 'mw_detail.html', context)


@login_required
def edit_profile(request):
    profile, created = ManagerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile_form = ChangeManagerProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        password_form = CustomSetPasswordForm(user=request.user, data=request.POST)

        if profile_form.is_valid() and password_form.is_valid():
            profile_form.save()
            password_form.save()
            messages.success(request, "Profilingiz muvaffaqiyatli yangilandi!")
            return redirect('manager:edit_profile')
        else:
            messages.error(request, "Iltimos, xatolarni tuzating.")
    else:
        profile_form = ChangeManagerProfileForm(instance=profile, user=request.user)
        password_form = CustomSetPasswordForm(user=request.user)

    return render(request, 'edit_profil.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })


@login_required
def create_message_view(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.manager = request.user
            message.save()
            return redirect('manager:home')
    else:
        form = MessageForm()

    return render(request, 'create_message.html', {'form': form})


@login_required
def manager_chat_l(request):
    manager = request.user

    # Managerga tegishli chatlarda ishtirok etgan barcha foydalanuvchilarni olish
    messages = ChatMessage.objects.filter(
        Q(sender=manager) | Q(receiver=manager)
    ).order_by('-created_at')

    chat_users = set()
    a = [str(i) for i in range(10000, 100000)]
    for msg in messages:
        if msg.sender != manager.username and ' ' in msg.sender and msg.sender[-5:] in a:
            chat_users.add(msg.sender)
        if msg.receiver != manager.username and ' ' in msg.receiver and msg.receiver[-5:] in a:
            chat_users.add(msg.receiver)

    us = {}
    for i in chat_users:
        un = 0
        mss = messages.filter(sender=i, receiver=manager)
        for e in mss:
            if not e.is_read:
                un += 1
        wr = Worker.objects.filter(worker_id=int(i[-5:])).first()
        wr.unread = un
        wr.save()
        us[i[:-5]] = {int(i[-5:]): un}
    context = {
        'us': us,
        'chat_users': chat_users,
        'manager': manager
    }

    return render(request, 'm_chat_u.html', context)


def daily_reports(request):
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    ws = Worker.objects.filter(manager=request.user)
    queryset = DailyWork.objects.filter(worker__in=ws)
    if start_date:
        queryset = queryset.filter(sana__gte=start_date)
    if end_date:
        queryset = queryset.filter(sana__lte=end_date)

    reports = list(queryset.values('sana').annotate(
        jami_ishlangan=Sum('umumiy_mahsulot'),
        jami_sifatsiz=Sum('sifatsiz_mahsulot')
    ).order_by('-sana'))

    # sofi qiymatini qo'shish
    for r in reports:
        jami = r['jami_ishlangan'] or 0
        sifatsiz = r['jami_sifatsiz'] or 0
        r['sof'] = float(jami) - float(sifatsiz)

    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'daily_reports.html', context)


def manager_chat_detail(request, id):
    manager = request.user
    worker = get_object_or_404(Worker, worker_id=int(id))

    # Faqat manager yoki worker bo'lishi mumkinligini tekshirish (xohlasangiz qo'shing)

    # Chatdagi barcha xabarlar (ikki tomon o'rtasida)
    messages = ChatMessage.objects.filter(
        (Q(sender=manager) & Q(receiver=worker.ism + ' ' + worker.familiya + str(worker.worker_id))) |
        (Q(sender=worker.ism + ' ' + worker.familiya + str(worker.worker_id)) & Q(receiver=manager))
    ).order_by('created_at')  # eski xabarlardan yangi xabarlarga

    for i in messages:
        if i.sender != request.user.username:
            i.is_read = True
            i.save()

    if request.method == "POST":
        text = request.POST.get('message')
        if text:
            ChatMessage.objects.create(sender=manager.username,
                                       receiver=worker.ism + ' ' + worker.familiya + str(worker.worker_id),
                                       message=text)
            return redirect('manager:m_chat', id=worker.worker_id)

    context = {
        'worker': worker,
        'messages': messages,
    }
    return render(request, 'm_chat.html', context)


@login_required
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
        return redirect('chat:m_chat_u')  # Xabar topilmasa chatga qaytarish


@login_required
def delete_message(request, message_id):
    try:
        message = ChatMessage.objects.get(id=message_id, sender=request.user.username)
        r = message.receiver

        if request.method == "POST":
            message.delete()
            return redirect('manager:m_chat', id=int(r[-5:]))
        rec = int(r[-5:])
        return render(request, 'd_mes.html', {
            'r_id': rec,
            'message_id': message_id,
            'message_text': message.message
        })
    except ChatMessage.DoesNotExist:
        return redirect('manager:m_chat_u')


@login_required
def mark_as_read(request, message_id):
    try:
        message = ChatMessage.objects.get(id=message_id)
        # Faqat qabul qilingan xabarlar ko'rilgan deb belgilanishi mumkin
        if message.receiver == request.user.username and not message.is_read:
            message.is_read = True
            message.save()
            return JsonResponse({"message": "Xabar ko'rilgan deb belgilandi"}, status=200)
        return JsonResponse({"message": "Xabar allaqachon ko'rilgan yoki boshqa foydalanuvchiga tegishli"}, status=400)
    except ChatMessage.DoesNotExist:
        return JsonResponse({"error": "Xabar topilmadi"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def add_payment(request):
    workers = Worker.objects.filter(manager=request.user)
    workers_exist = workers.exists()

    if request.method == 'POST':
        form = MonthlyPaymentForm(request.POST)
        form.fields['worker'].queryset = workers  # <-- BU HAR DOIM KERAK
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.worker.manager != request.user:
                messages.error(request, "Siz bu ishchiga to‘lov kiritolmaysiz.")
                return redirect('manager:tolov')
            if instance.summa <= 0:
                messages.error(request, "Bunday summa to'lab bo'lmaydi")
                return redirect('manager:tolov')
            if instance.summa > instance.worker.qoldiq:
                messages.error(request, "Ishchi buncha summa ishlamagan")
                return redirect('manager:tolov')
            instance.manager = request.user
            instance.save()
            messages.success(request, "To‘lov muvaffaqiyatli qo‘shildi.")
            return redirect('manager:tolov')
    else:
        form = MonthlyPaymentForm()
        form.fields['worker'].queryset = workers  # <-- BU YERDA HAM KERAK

    return render(request, 'monthly_payment.html', {
        'form': form,
        'workers_exist': workers_exist,
        'back_url': 'manager:home',
    })


@login_required
def tolow(request, w_id):
    worker = get_object_or_404(Worker, worker_id=w_id)  # .first() o‘rniga xavfsizroq
    qoldiq = worker.qoldiq

    if request.method == 'POST':
        print("POST so‘rov")
        form = TolowForm(data=request.POST, worker_id=w_id)
        if form.is_valid():
            print("Forma valid")
            instance = form.save(commit=False)
            if worker.manager != request.user:
                messages.error(request, "Siz bu ishchiga to‘lov kiritolmaysiz.")
                return redirect('manager:tolow', w_id=worker.worker_id)
            instance.manager = request.user
            instance.save()
            messages.success(request, "To‘lov muvaffaqiyatli qo‘shildi.")
            return redirect('manager:worker_detail', worker_id=worker.id)
        else:
            print("Forma xatolari:", form.errors)
    else:
        form = TolowForm(worker_id=w_id)
        print("GET so‘rov")

    return render(request, 'tolow.html', {
        'form': form,
        'qoldiq': qoldiq,
        'back_url': 'manager:home',
        'worker': worker,  # Shablon uchun qo‘shimcha
    })
