from django.shortcuts import render, redirect, get_object_or_404


def sorov(request):
    # if 'worker_id' in request.session:
    #     return redirect('profil:sorov')
    # elif request.user.is_authenticated:
    #     return redirect('manager:home')
    return render(request, 'worker_or.html')
