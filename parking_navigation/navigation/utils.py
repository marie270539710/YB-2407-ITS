import matplotlib
matplotlib.use('Agg')  # Important: Use non-GUI backend
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import matplotlib.image as mpimg
import random
from random import choice
import os

def find_shortest_path(parking_lot, start, destination):
    rows, cols = len(parking_lot), len(parking_lot[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    queue = deque([(start, [])])
    visited = set()

    while queue:
        (current, path) = queue.popleft()
        x, y = current

        if current == destination:
            return path + [current]

        if current in visited:
            continue
        visited.add(current)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (parking_lot[nx][ny] == 'E' or parking_lot[nx][ny] == 'X' or (nx, ny) == destination) and (nx, ny) not in visited:
                queue.append(((nx, ny), path + [current]))

    return None

def plot_parking_lot(parking_lot, path_to_parking, path_to_exit, path_to_mall, chosen_slot, selected_slot, exit_point, occupied_slots, disabled_slots, ev_slots):
    rows, cols = len(parking_lot), len(parking_lot[0])
    grid = np.zeros((rows, cols, 3))

    colors = {
        'E': (1, 1, 1),
        'O': (0, 0, 0),
        'MALL': (0, 0, 0),
        'ENTER': (1, 1, 1),
        'P1': (0.5, 0.5, 0.5),
        'P2': (0.5, 0.5, 0.5),
        'P3': (0.5, 0.5, 0.5),
        'P4': (0.5, 0.5, 0.5),
        'EV': (0.5, 0.5, 0.5),
        'D1': (0.5, 0.5, 0.5),
        'EXIT': (1, 1, 1)
    }

    parking_top = ['P1', 'P2', 'D1']
    parking_bottom = ['EV', 'P3', 'P4']

    for i in range(rows):
        for j in range(cols):
            grid[i, j] = colors.get(parking_lot[i][j], (1, 1, 1))

    plt.figure(figsize=(6, 10))
    plt.imshow(grid, origin='upper')
    plt.xticks([])  # Removes x-axis ticks and labels
    plt.yticks([])  # Removes y-axis ticks and labels

    car_images = ['car1.png', 'car2.png', 'car3.png', 'car4.png']
    static_path = 'navigation/static/navigation'

    # Place random car images on occupied slots
    for i, row in enumerate(parking_lot):
        for j, slot in enumerate(row):
            if slot in parking_top:
                car_img = mpimg.imread(os.path.join(static_path, "parking_top.png"))
                plt.imshow(car_img, extent=(j-0.5, j+0.5, i-0.5, i+0.5))
            if slot in parking_bottom:
                car_img = mpimg.imread(os.path.join(static_path, "parking_bottom.png"))
                plt.imshow(car_img, extent=(j-0.5, j+0.5, i-0.5, i+0.5))
            if slot == "X":
                car_img = mpimg.imread(os.path.join(static_path, "crosswalk.png"))
                plt.imshow(car_img, extent=(j-0.4, j+0.4, i-0.3, i+0.3))
            if slot == "EXIT":
                car_img = mpimg.imread(os.path.join(static_path, "exit.png"))
                plt.imshow(car_img, extent=(j-0.4, j+0.4, i-0.2, i+0.2))
            if slot == "ENTER":
                car_img = mpimg.imread(os.path.join(static_path, "entrance.png"))
                plt.imshow(car_img, extent=(j-0.4, j+0.4, i-0.2, i+0.2))
            if slot == "MALL":
                car_img = mpimg.imread(os.path.join(static_path, "mall.png"))
                plt.imshow(car_img, extent=(j-0.5, j+0.5, i-0.4, i+0.4))
            if slot in disabled_slots:
                car_img = mpimg.imread(os.path.join(static_path, "disabled.png"))
                plt.imshow(car_img, extent=(j-0.2, j+0.2, i-0.2, i+0.2))
            if slot in ev_slots:
                car_img = mpimg.imread(os.path.join(static_path, "ev.png"))
                plt.imshow(car_img, extent=(j-0.2, j+0.2, i-0.2, i+0.2))
            if slot in occupied_slots:
                car_img_file = np.random.choice(car_images)
                car_img = mpimg.imread(os.path.join(static_path, car_img_file))
                plt.imshow(car_img, extent=(j-0.3, j+0.3, i-0.4, i+0.4), aspect='auto')
            if slot == selected_slot:
                car_img = mpimg.imread(os.path.join(static_path, "carslot.png"))
                plt.imshow(car_img, extent=(j-0.3, j+0.3, i-0.4, i+0.4), aspect='auto')

    if path_to_parking:
        x_coords, y_coords = zip(*path_to_parking)
        y_shifted = [y - 0.1 for y in y_coords]
        plt.plot(y_shifted, x_coords, color='green', linewidth=3, label="To Parking")

    if path_to_exit:
        x_coords, y_coords = zip(*path_to_exit)
        y_shifted = [y + 0.1 for y in y_coords]
        plt.plot(y_shifted, x_coords, color='red', linewidth=3, label="To Exit")

    if path_to_mall:
        x_coords, y_coords = zip(*path_to_mall)
        y_shifted = [y + 0.2 for y in y_coords]
        x_shifted = [x + 0.1 for x in x_coords]
        plt.plot(y_shifted, x_shifted, color='blue', linewidth=3, label="To Mall")

    # if chosen_slot:
    #     plt.scatter(chosen_slot[1], chosen_slot[0], c='yellow', s=100, edgecolors='black', alpha=0.0, label='Selected Slot')

    # if exit_point:
    #     plt.scatter(exit_point[1], exit_point[0], c='red', s=100, edgecolors='black', alpha=0.0, label='Parking Exit')

    plt.gca().invert_yaxis()
    plt.legend()
