from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .utils import find_shortest_path, plot_parking_lot
from .models import ParkingLog
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, UserSettingsForm

from datetime import datetime, timedelta

# parking_lot_layout = [
#     ['ENTER', 'E', 'O', 'E', 'P1'],
#     ['E', 'E', 'O', 'E', 'P2'],
#     ['O', 'E', 'E', 'E', 'P3'],
#     ['E', 'O', 'E', 'E', 'P4'],
#     ['E', 'E', 'E', 'O', 'P5'],
#     ['EXIT', 'E', 'E', 'D1', 'E']
# ]

parking_lot_layout = [
    ['ENTER', 'O', 'O', 'O', 'O', 'O'],
    ['E', 'E', 'E', 'E', 'E', 'O'],
    ['E', 'P1', 'P2', 'D1', 'E', 'O'],
    ['E', 'O', 'O', 'O', 'E', 'O'],
    ['E', 'EV', 'P3', 'P4', 'E', 'O'],
    ['E', 'E', 'E', 'E', 'E', 'EXIT']
]

slot_coordinates = {
    'P1': (2, 1),
    'P2': (2, 2),
    'P3': (4, 2),
    'P4': (4, 3),
    'EV': (4, 1),
    'D1': (2, 3),
}

@login_required(login_url='/accounts/login/')
@csrf_exempt
def parking_map(request):
    user_profile = request.user.profile

    available_slots = ['P1', 'P2', 'P3', 'P4', 'EV', 'D1']
    near_entrance_slots = ['P1', 'P2']
    near_exit_slots = ['P3', 'P4']
    occupied_slots = ['P1']
    disabled_slots = ['D1']
    ev_slots = ['EV']

    # Remove occupied slots dynamically from near entrance/exit lists
    available_slots_near_entrance = [slot for slot in near_entrance_slots if slot not in occupied_slots]
    available_slots_near_exit = [slot for slot in near_exit_slots if slot not in occupied_slots]
    available_disabled_slots = [slot for slot in disabled_slots if slot not in occupied_slots]
    available_ev_slots = [slot for slot in ev_slots if slot not in occupied_slots]

    available_slots = [slot for slot in available_slots if slot not in occupied_slots]
    available_slots = [slot for slot in available_slots if slot not in disabled_slots]
    available_slots = [slot for slot in available_slots if slot not in ev_slots]

    path_to_parking = None
    path_to_exit = None
    path_to_mall = None
    chosen_slot = None
    exit_point = None

    match request.method:
        case 'POST':
            extend_minutes = request.POST.get('extend_minutes')
            selected_slot = request.POST.get('slot')

            if extend_minutes:
                if user_profile.exit_time:
                    # Add extend_minutes to existing datetime
                    updated_exit = user_profile.exit_time + timedelta(minutes=int(extend_minutes))
                    user_profile.exit_time = updated_exit
                    user_profile.save()
                return redirect('parking_map')

            elif selected_slot:
                match selected_slot:
                    case 'toexit': None
                    case 'tomall': None
                    case 'endparking':
                        # Try to find existing log for current session
                        existing_log = ParkingLog.objects.filter(
                            user=request.user,
                            slot=user_profile.selected_slot,
                            arrival_time=user_profile.arrival_time
                        ).first()

                        if existing_log:
                            # Update the existing log
                            existing_log.exit_time = user_profile.exit_time
                            existing_log.autoexit = False  # Manual end
                            existing_log.save()
                        else:
                            # Create new log if none found
                            ParkingLog.objects.create(
                                user=request.user,
                                slot=user_profile.selected_slot,
                                arrival_time=user_profile.arrival_time,
                                exit_time=user_profile.exit_time,
                                autoexit=False
                            )

                        selected_slot = None
                        user_profile.selected_slot = ""
                        user_profile.arrival_time = None
                        user_profile.exit_time = None
                        user_profile.save()
                    case _:
                        match selected_slot:
                            case 'exit':
                                selected_slot = np.random.choice(available_slots_near_exit)
                            case 'entrance':
                                selected_slot = np.random.choice(available_slots_near_entrance)
                            case 'ev':
                                selected_slot = np.random.choice(available_ev_slots)
                            case 'disabled':
                                selected_slot = np.random.choice(available_disabled_slots)

                        user_profile.selected_slot = selected_slot
                        user_profile.arrival_time = timezone.localtime()
                        user_profile.exit_time = user_profile.arrival_time + timedelta(hours=1)
                        user_profile.save()

                        ParkingLog.objects.create(
                            user=request.user,
                            slot=user_profile.selected_slot,
                            arrival_time=user_profile.arrival_time,
                        )

        case 'GET':
            selected_slot = user_profile.selected_slot if user_profile.selected_slot else None

    # Calculate Progress
    progress_percentage = 0
    if user_profile.arrival_time and user_profile.exit_time:
        arrival_dt = user_profile.arrival_time
        exit_dt = user_profile.exit_time
        current_dt = timezone.now()

        total_seconds = (exit_dt - arrival_dt).total_seconds()
        elapsed_seconds = (current_dt - arrival_dt).total_seconds()
        progress_percentage = min(max((elapsed_seconds / total_seconds) * 100, 0), 100)


    if selected_slot:
        # chosen_slot = slot_coordinates[selected_slot]
        start_point = (0, 0)  # Parking Entrance
        exit_point = (5, 5)  # Parking Exit
        mall_point = (3, 5)  # Mall Entrance

        match selected_slot:
            case 'toexit':
                selected_slot = user_profile.selected_slot
                chosen_slot = slot_coordinates[user_profile.selected_slot]
                path_to_exit = find_shortest_path(parking_lot_layout, chosen_slot, exit_point)
                path_to_parking = find_shortest_path(parking_lot_layout, start_point, chosen_slot)
            case 'tomall':
                selected_slot = user_profile.selected_slot
                chosen_slot = slot_coordinates[user_profile.selected_slot]
                path_to_mall = find_shortest_path(parking_lot_layout, chosen_slot, mall_point)
                path_to_parking = find_shortest_path(parking_lot_layout, start_point, chosen_slot)
            case _:
                chosen_slot = slot_coordinates[selected_slot]
                path_to_parking = find_shortest_path(parking_lot_layout, start_point, chosen_slot)
        
        # path_to_parking = find_shortest_path(parking_lot_layout, start_point, chosen_slot)
        # path_to_exit = find_shortest_path(parking_lot_layout, chosen_slot, exit_point)
        # path_to_mall = find_shortest_path(parking_lot_layout, chosen_slot, mall_point)

    if path_to_parking == None:
        path_to_parking = find_shortest_path(parking_lot_layout, (0,0), (0,0))

    # Plotting the parking lot visualization
    plt.figure(figsize=(6, 10))
    plot_parking_lot(
            parking_lot_layout, path_to_parking, path_to_exit, path_to_mall,
            chosen_slot, selected_slot, exit_point, 
            occupied_slots=occupied_slots,
            disabled_slots=disabled_slots,
            ev_slots=ev_slots
        )
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    context = {
        'graphic': graphic,
        'available_slots': available_slots,
        'selected_slot': selected_slot,
        'near_entrance_slots': available_slots_near_entrance,
        'near_exit_slots': available_slots_near_exit,
        'disabled_slots': available_disabled_slots,
        'ev_slots': available_ev_slots,
        'user_profile': user_profile,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'navigation/parking_map.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('parking_map')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def user_settings(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            if request.POST.get('new_password'):
                request.user.set_password(request.POST['new_password'])
                request.user.save()
            return redirect('parking_map')
    else:
        form = UserSettingsForm(user=request.user, instance=request.user.profile)

    return render(request, 'navigation/user_settings.html', {
        'form': form,
    })

@login_required
def parking_status(request):
    user_profile = request.user.profile
    alert_needed = False
    expired = False
    time_remaining_minutes = None

    if user_profile.arrival_time and user_profile.exit_time:
        now_dt = timezone.now()  # Timezone-aware current datetime
        exit_dt = user_profile.exit_time  # Already a DateTimeField, timezone-aware

        remaining_seconds = (exit_dt - now_dt).total_seconds()

        if remaining_seconds <= 0:
            expired = True
        elif remaining_seconds <= 600:  # 10 mins or less
            alert_needed = True
            time_remaining_minutes = max(int(remaining_seconds // 60), 0)
        else:
            time_remaining_minutes = int(remaining_seconds // 60)

    data = {
        'current_time': timezone.localtime().strftime('%I:%M %p'),  # Local time for user
        'arrival_time': timezone.localtime(user_profile.arrival_time).strftime('%I:%M %p') if user_profile.arrival_time else '',
        'exit_time': timezone.localtime(user_profile.exit_time).strftime('%I:%M %p') if user_profile.exit_time else '',
        'alert': alert_needed,
        'expired': expired,
        'remaining_minutes': time_remaining_minutes,
    }

    return JsonResponse(data)
