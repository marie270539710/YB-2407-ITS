from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .utils import find_shortest_path, plot_parking_lot
import matplotlib.pyplot as plt
import io
import base64

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, UserSettingsForm

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
    selected_slot = request.POST.get('slot') 
    available_slots = ['P1', 'P2', 'P3', 'P4', 'EV', 'D1']
    occupied_slots = ['P1']
    disabled_slots = ['D1']
    ev_slots = ['EV']
    
    if selected_slot:
        chosen_slot = slot_coordinates[selected_slot]
        start_point = (0, 0)  # Parking Entrance
        exit_point = (5, 5)  # Parking Exit
        mall_point = (3, 5)  # Mall Entrance
        
        path_to_parking = find_shortest_path(parking_lot_layout, start_point, chosen_slot)
        path_to_exit = find_shortest_path(parking_lot_layout, chosen_slot, exit_point)
        path_to_mall = find_shortest_path(parking_lot_layout, chosen_slot, mall_point)

        # Plotting the parking lot visualization
        plt.figure(figsize=(6, 10))
        plot_parking_lot(
                parking_lot_layout, path_to_parking, path_to_exit, path_to_mall,
                chosen_slot, exit_point, 
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
            'selected_slot': selected_slot
        }
        return render(request, 'navigation/parking_map.html', context)

    context = {
        'graphic': None,
        'available_slots': available_slots,
        'selected_slot': selected_slot
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