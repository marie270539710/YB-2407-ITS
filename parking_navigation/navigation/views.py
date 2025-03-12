from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .utils import find_shortest_path, plot_parking_lot
import matplotlib.pyplot as plt
import io
import base64

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
    ['E', 'P3', 'P4', 'P5', 'E', 'O'],
    ['E', 'E', 'E', 'E', 'E', 'EXIT']
]

slot_coordinates = {
    'P1': (2, 1),
    'P2': (2, 2),
    'P3': (4, 1),
    'P4': (4, 2),
    'P5': (4, 3),
    'D1': (2, 3),
}

@csrf_exempt
def parking_map(request):
    selected_slot = request.POST.get('slot') 
    available_slots = ['P1', 'P2', 'P3', 'P4', 'P5', 'D1']
    disabled_slots = ['D1']
    occupied_slots = ['P1', 'P4']
    
    if selected_slot:
        start = (0, 0)  # Entrance
        chosen_slot = slot_coordinates[selected_slot]
        exit_point = (5, 5)  # Exit
        
        path_to_parking = find_shortest_path(parking_lot_layout, start, chosen_slot)
        path_to_exit = find_shortest_path(parking_lot_layout, chosen_slot, exit_point)

        # Plotting the parking lot visualization
        plt.figure()
        plot_parking_lot(
                parking_lot_layout, path_to_parking, path_to_exit, 
                chosen_slot, exit_point, 
                occupied_slots=occupied_slots,
                disabled_slots=disabled_slots 
            )
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
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
    
