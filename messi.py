#!/usr/bin/python
""" This script allows to measure distances on screen. """

from os import path
import tkinter as tk
import tkinter.simpledialog
import math

VERSION = '17.06.2021'

# TODO: Add feature calculation of paths (several segments)

# Create window
app = tk.Tk()

# List to hold mouse coordinates (pairs of x- and y-values)
coords = []

# Dict to hold the values for assigning screen units to real world ones
calibration_vals = {'length_screen' : 1,
                    'length_reality' : 1,
                    'unit' : 'px',
                    'factor' : 1}

# Edit window
app.title('Messi')
app.geometry('200x200')

# Set app icon
# The following commands ensure that the icon can be found whether the
# script is run directly with Python or also as EXE-file created with
# 'pyinstaller'
path_to_icon = path.abspath(path.join(path.dirname(__file__), 'ruler.png'))
icon = tk.PhotoImage(master=app, file=path_to_icon)
app.wm_iconphoto(True, icon)

# Without the next line transparency doesn't work on Linux
app.wait_visibility(app)

# Define grade of transparency: 0 = invisible, 1 = intransparent
app.wm_attributes('-alpha', 0.3)

canvas = tk.Canvas(app, bd=0, bg='yellow')
# Settings to expand the canvas in case the main window resizes
canvas.pack(fill='both', expand=True)

var_mouse = tk.StringVar()
var_mouse.set('tbd')
lbl_mouse = tk.Label(app, textvariable = var_mouse)
lbl_mouse.place(relx=0.0, rely=1.0, anchor='sw')

var_dimension = tk.StringVar()
var_dimension.set('tbd')
lbl_dimension = tk.Label(app, textvariable = var_dimension)
lbl_dimension.place(relx=1.0, rely=1.0, anchor='se')

def show_manual(version):
    """Displays short summary how to use this software."""

    print('+-----------------------------------------+')
    print('|                M E S S I                |')
    print('|                                         |')
    print(f'| This is messi version {version}.       |')
    print('|                                         |')
    print('| Usage (keyboard shortcuts)              |')
    print('|   ?     : Show this text                |')              
    print('|   c     : Define relation of pixels to  |')
    print('|           real-world dimensions like mm |')
    print('|   g     : Switch grid on/off and define |')
    print('|           grid distance                 |')
    print('|   DELETE: Remove points and lines from  |')
    print('|           messi window                  |')
    print('+-----------------------------------------+')
    print('')

def motion(event):
    """
    Follow the mouse
    https://stackoverflow.com/questions/22925599/mouse-position-python-tkinter
    """
    # One option to track the mouse coordinates relative
    # to the root window
    # x, y = event.x, event.y
    # print('{}, {}'.format(x, y))

    # Track mouse coordinates relative to the screen
    # x = app.winfo_pointerx()
    # y = app.winfo_pointery()
    # print(f'window: {x}, {y}')

    # Another option to track the mouse coordinates relative
    # to the window.
    x = app.winfo_pointerx() - app.winfo_rootx()
    y = app.winfo_pointery() - app.winfo_rooty()

    # Update text of mouse position label
    var_mouse.set(f'{x}, {y}')

    # If we have already defined one point we draw a line from it to the
    # mouse cursor
    if len(coords) == 1:
        x1 = coords[0][0]
        y1 = coords[0][1]
        # With each mouse move a new line is drawn.
        # To not end up with hundreds of line we have to delete the old one
        # before drawing a new one
        canvas.delete('my_line')
        canvas.create_line(x1, y1, x, y, fill='blue', tags='my_line')

def set_coords(event):
    """Fills a list with mouse coordinates for later calculation."""

    x = app.winfo_pointerx() - app.winfo_rootx()
    y = app.winfo_pointery() - app.winfo_rooty()
    coords.append([x, y])

    # Get the index of the new mouse click in the coordinates list
    # and print it. To not start with index 0 we add 1.
    coord_index = coords.index([x, y]) + 1
    print(f'coordinate {coord_index}: {x}, {y}')

    draw_point(x, y)

    # To calculate the distance between 2 points we just wait until
    # the list of coordinates holds 2 coordinates
    if len(coords) == 2:
        calc_distance(coords)
        coords.clear()


def draw_point(x, y):
    """Draws a crosshair at the provided x,y position."""
    oval = canvas.create_oval(x-3, y-3, x+3, y+3, fill='red', tags='dots')

def clear_canvas(event):
    """Delete all objects on the canvas."""
    canvas.delete('all')

def calc_distance(coords):
    """Calculates the distance between two points."""
    x1 = coords[0][0]
    y1 = coords[0][1]
    x2 = coords[1][0]
    y2 = coords[1][1]

    distance_chord = ((y2 - y1)**2 + (x2 - x1)**2)**0.5

    # Store last distance in global var
    calibration_vals['length_screen'] = distance_chord

    # Do geometrical calculations
    real_dist_x = abs(x2 - x1) * calibration_vals['factor']
    real_dist_y = abs(y2 - y1) * calibration_vals['factor']
    real_dist_chord = distance_chord * calibration_vals['factor']

    dist_x = x2 - x1
    dist_y = y2 - y1
    angle_x = math.degrees(math.atan2(dist_y, dist_x))

    # Set the chord length for display in GUI
    var_dimension.set(f'{real_dist_chord:.2f} {calibration_vals["unit"]}')

    # Print all vars of calculation to console
    print(f'X distance  : {real_dist_x:.2f} {calibration_vals["unit"]}')
    print(f'Y distance  : {real_dist_y:.2f} {calibration_vals["unit"]}')
    print(f'chord length: {real_dist_chord:.2f} {calibration_vals["unit"]}')
    # TODO: Presently the angle is given to the X-axis. The origin of
    #       the X-axis is the first point. All angles are positive inde-
    #       pendent from the location of the second point that can be
    #       above or below the first point.
    print(f'angle from X: {abs(angle_x):.2f}\n')

def calibrate_distance(event):
    """Calibrate the distance to real world units."""

    title = 'Calibrate'
    prompt = 'Provide distance and unit:'
    user_input = tk.simpledialog.askstring(title, prompt)

    if not user_input:
        return

    real_distance, unit = user_input.split()
    real_distance = float(real_distance)
    calibration_vals['unit'] = unit
    calibration_vals['length_reality'] = real_distance
    calibration_vals['factor'] = real_distance / calibration_vals['length_screen']
    print(f'Calibration from px to {calibration_vals["unit"]}')
    print(f'{calibration_vals["length_screen"]:.2f} px correspond to {calibration_vals["length_reality"]} {calibration_vals["unit"]}')
    # ~ print(f'{calibration_vals["length_screen"]:.2f} px')
    # ~ print(f'{calibration_vals["length_reality"]} {calibration_vals["unit"]}')
    print(f'{calibration_vals["factor"]} {calibration_vals["unit"]}/px\n')

    var_dimension.set(f'{calibration_vals["length_reality"]:.2f} {calibration_vals["unit"]}')

def toggle_grid(event):
    """Switch grid on and off"""

    title = 'Grid'
    prompt = 'Provide grid resolution (0 = grid off):'
    user_input = tk.simpledialog.askfloat(title, prompt)
    
    if user_input:
        grid_dist = user_input
    else:
        # Delete grid lines
        canvas.delete('grid_line')
        return        

    # The canvas has to be updated to receive the latest dimensions
    canvas.update()
    x = canvas.winfo_width()
    y = canvas.winfo_height()

    nr_lines_x = int(x // (grid_dist / calibration_vals['factor']))
    nr_lines_y = int(y // (grid_dist / calibration_vals['factor']))

    print('- Grid -')
    print(f'nr. of lines  : {user_input}')
    print(f'window size  X: {x} px')
    print(f'window size  Y: {y} px')
    print(f'nr. of lines X: {nr_lines_x}')
    print(f'nr. of lines Y: {nr_lines_y}')
    print('')
        
    # Draw vertical grid lines
    for i in range(nr_lines_x + 1):
        x1 = x2 = i * grid_dist / calibration_vals['factor'] 
        y1 = 0 
        y2 = y
        canvas.create_line(x1, y1, x2, y2, tags='grid_line')

    # Draw horizontal grid lines
    for i in range(nr_lines_y + 1):
        x1 = 0 
        y1 = y2 = i * grid_dist / calibration_vals['factor']
        x2 = x
        canvas.create_line(x1, y1, x2, y2, tags='grid_line')

# Activate handler for mouse motion events
app.bind('<Motion>', motion)
app.bind('<Button-1>', set_coords)
app.bind('<Delete>', clear_canvas)
app.bind('c', calibrate_distance )
app.bind('g', toggle_grid)
app.bind('?', show_manual)

show_manual(VERSION)

# Activate command
app.mainloop()
