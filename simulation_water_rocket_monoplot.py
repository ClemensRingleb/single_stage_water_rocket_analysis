import time
import math
import numpy as np

import pygame as pg
from pygame.locals import *

import matplotlib.pyplot as plt

# ----- Alle Größen sind immer in SI-Basiseinheiten angegeben, damit nur bei der Ausgabe umgerechnet werden muss -----

# Rakete - Dimensionen / Spezifikationen

m_rocket = 0.2
V_rocket = 0.00125

d_rocket = 0.08
h_rocket = 0.43

A_rocket = (d_rocket / 2) ** 2 * np.pi

d_nozzle = 0.0095
A_nozzle = (d_nozzle / 2) ** 2 * np.pi

# C_D-Wert (Luftwiderstand für langen Zylinder)
C_D = 0.82

# ------------- Variable Parameter  -----------------

V_water_0 = 0.6 * V_rocket
p_gauge = 3 * 10 ** 5

# ---------------------------------------------------

# Physikalische Konstanten

g = 9.81  # Erdbeschleunigung
rho_water = 1000  # Dichte von Wasser
rho_air = 1.225  #
p_atm = 101325  # Normaldruck (Standardbedingungen)
gamma = 1.4  # Adiabatenindex

# initial values

m_water_0 = rho_water * V_water_0
V_air_0 = V_rocket - V_water_0
V_air = V_air_0
p_abs_0 = p_atm + p_gauge
p_abs = p_abs_0

# Initialisierung

m_water = m_water_0
t = 0
y = 0
v = 0
a = 0
y_max = 0
t_max = 0
t_0 = 0

# Simulation

dt = 10 ** (-5)

scale_list = [0.08, 0.12, 0.2, 0.3, 0.5, 0.8, 1.0, 2.0, 3.0, 4.0]
scale_index = 6
scale = scale_list[scale_index]

timestep_list = [0, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1]
timestep_index = 0
timestep = timestep_list[timestep_index]

# Pygame-Setup

pg.display.init()
pg.font.init()

displayfont = pg.font.SysFont('Mono Space', 30)

monitor_size = [pg.display.Info().current_w, pg.display.Info().current_h]
width, height = monitor_size

ground_h_p = 0.6
screen = pg.display.set_mode(monitor_size, pg.RESIZABLE)

origin_d_ = np.array([width // 2, height // 2])
ground_width = 8
ground_color = (255, 255, 255)
line_width = 9
line_color_1 = (120, 120, 120)
line_color_2 = (80, 80, 80)
line_color_3 = (40, 40, 40)

display_offset = (0, 0)

y_scale = 123 / h_rocket
x_scale = y_scale

scales = np.array([x_scale, y_scale])

running = True
has_reached_max = False
has_landed = False

pausing = False

stage = 0

i = 0

t_list = []
v_list = []
a_list = []
y_list = []
p_abs_list = []

change_p = False
change_V = False

p_entry = ""
V_entry = ""


# KI-generierter Code (für einen "bottle converter", um später Wasserfüllmenge
# in Wasserstand umzurechnen, basierend auf der animierten Geometrie der Flasche, in 3D
# denn aufgrund der Verjüngung des Flaschenhalses ist der Zusammenhang nicht proportional):
def create_bottle_converter(points):
    """
    Analyzes the 3D geometry of a bottle and returns a conversion function.

    The returned function converts a "water volume percentage" to the
    corresponding "water height percentage", accounting for the bottle's shape.

    Args:
        points (dict): A dictionary mapping point names to Vector2 objects
                       describing the bottle's 2D profile.

    Returns:
        function: A function that takes a volume percentage (0-100) and
                  returns the corresponding height percentage (0-100).
    """
    # 1. Define the bottle's profile from the points.
    # CORRECTION: Sort by y-coordinate in REVERSE order for an upside-down bottle.
    profile = sorted([
        (points["fl_r2"].y, points["fl_r2"].x),
        (points["fl_r1"].y, points["fl_r1"].x),
        (points["t_r"].y, points["t_r"].x),
        (points["b_r"].y, points["b_r"].x),
        (points["op_r1"].y, points["op_r1"].x),
        (points["op_r4"].y, points["op_r4"].x),
    ], key=lambda p: p[0], reverse=True)  # The key change is here

    y_max = profile[0][0]  # This is the new "bottom" (e.g., y=85)
    y_min = profile[-1][0]
    total_height = y_max - y_min

    if total_height <= 0:
        raise ValueError("Bottle has zero or negative height.")

    # 2. Calculate the volume of each segment (frustum).
    segments = []
    for i in range(len(profile) - 1):
        y1, r1 = profile[i]
        y2, r2 = profile[i + 1]
        h = y1 - y2  # y1 > y2, so h is positive
        volume = (math.pi * h / 3.0) * (r1 ** 2 + r1 * r2 + r2 ** 2)
        segments.append({'y_level': y2, 'volume': volume})

    # 3. Create a lookup table (LUT) mapping height percentage to volume percentage.
    lut_percent = [(0.0, 0.0)]
    cumulative_volume = 0.0
    total_volume = sum(s['volume'] for s in segments)

    if total_volume <= 0:
        def zero_volume_converter(water_volume_percent):
            return 100.0 if water_volume_percent > 0 else 0.0

        return zero_volume_converter

    for seg in segments:
        cumulative_volume += seg['volume']
        # Height is measured from the new bottom (y_max) downwards
        height_from_bottom = y_max - seg['y_level']
        height_percent = (height_from_bottom / total_height) * 100.0
        volume_percent = (cumulative_volume / total_volume) * 100.0
        lut_percent.append((height_percent, volume_percent))

    # 4. Return the final converter function that interpolates using the LUT.
    def convert_volume_to_height_percent(water_volume_percent):
        if water_volume_percent <= 0:
            return 0.0
        if water_volume_percent >= 100:
            return 100.0

        for i in range(len(lut_percent) - 1):
            hp1, vp1 = lut_percent[i]
            hp2, vp2 = lut_percent[i + 1]
            if vp1 <= water_volume_percent <= vp2:
                if vp2 == vp1: return hp1
                fraction = (water_volume_percent - vp1) / (vp2 - vp1)
                return hp1 + fraction * (hp2 - hp1)

        return 100.0

    return convert_volume_to_height_percent


def draw_rocket(screen, rocket_color, water_color, back_color, position, scale, thickness, water_percentage, exhaust_velocity, t_elapsed):
    origin = position

    # Definition der Flaschenkoordinaten relativ zum Ursprung
    # (noch in fester Skalierung, wird später danach entsprechend skaliert)

    points = {

        # großer "Hauptkörper" der Flasche
        "t_r": pg.Vector2(20, -30),  # top-right
        "b_r": pg.Vector2(20, 30),  # bottom-right
        "t_l": pg.Vector2(-20, -30),  # top-left
        "b_l": pg.Vector2(-20, 30),  # bottom-left

        # Boden (floor) der Flasche
        "fl_r1": pg.Vector2(18, -35),
        "fl_r2": pg.Vector2(12, -37),
        "fl_l1": pg.Vector2(-18, -35),
        "fl_l2": pg.Vector2(-12, -37),

        # Öffnung (opening) der Flasche
        "op_r1": pg.Vector2(8, 75),
        "op_r2": pg.Vector2(8, 80),
        "op_r3": pg.Vector2(12, 80),
        "op_r4": pg.Vector2(8, 85),
        "op_l1": pg.Vector2(-8, 75),
        "op_l2": pg.Vector2(-8, 80),
        "op_l3": pg.Vector2(-12, 80),
        "op_l4": pg.Vector2(-8, 85),

        # Finnen
        "f_r1": pg.Vector2(8,78),
        "f_r2": pg.Vector2(14,78),
        "f_r3": pg.Vector2(14,95),
        "f_r4": pg.Vector2(37,104),
        "f_r5": pg.Vector2(37,94),
        "f_r6": pg.Vector2(35,82),
        "f_r7": pg.Vector2(28,65),
        "f_r8": pg.Vector2(16,45),

        "f_l1": pg.Vector2(-8, 78),
        "f_l2": pg.Vector2(-14, 78),
        "f_l3": pg.Vector2(-14, 95),
        "f_l4": pg.Vector2(-37, 104),
        "f_l5": pg.Vector2(-37, 94),
        "f_l6": pg.Vector2(-35, 82),
        "f_l7": pg.Vector2(-28, 65),
        "f_l8": pg.Vector2(-16, 45)

        # Spitze

    }

    bottle_converter = create_bottle_converter(points)

    # Scale all points
    scaled_points = {name: p * scale for name, p in points.items()}

    # List of lines to draw, defined by the names of their start and end points
    lines_to_draw = [
        ("t_r", "b_r"), ("t_l", "b_l"),
        ("t_r", "fl_r1"), ("t_l", "fl_l1"),  # Boden-Abrundung 1
        ("fl_r1", "fl_r2"), ("fl_l1", "fl_l2"),  # Boden-Abrundung 2
        ("fl_l2", "fl_r2"),  # Boden
        ("op_r1", "b_r"), ("op_l1", "b_l"),  # Hauptkörper zur Öffnung
        ("op_r1", "op_r2"), ("op_l1", "op_l2"),
        ("op_r2", "op_r4"), ("op_l2", "op_l4"),
        ("op_r2", "op_r3"), ("op_l2", "op_l3"),
    ]

    poly_water_keys = [
        "op_r4", "op_r2", "op_r1", "b_r", "t_r", "fl_r1", "fl_r2",
        "fl_l2", "fl_l1", "t_l", "b_l", "op_l1", "op_l2", "op_l4"
    ]

    fin_right_keys = [
        "f_r1", "f_r2", "f_r3", "f_r4", "f_r5", "f_r6", "f_r7", "f_r8", "op_r1"
    ]

    fin_left_keys = [
        "f_l1", "f_l2", "f_l3", "f_l4", "f_l5", "f_l6", "f_l7", "f_l8", "op_l1"
    ]

    poly_water = []
    for key in poly_water_keys:
        poly_water.append(origin + points[key] * scale)

    poly_fin_right = []
    for key in fin_right_keys:
        poly_fin_right.append(origin + points[key] * scale)

    poly_fin_left = []
    for key in fin_left_keys:
        poly_fin_left.append(origin + points[key] * scale)

    if water_percentage > 0.01:
        pg.draw.polygon(screen, water_color, poly_water, 0)

    water_height_percentage = bottle_converter(water_percentage)

    air_height_percentage = 100 - water_height_percentage

    pg.draw.rect(screen, back_color, (
        origin[0] - scale * 30, origin[1] - scale * 37, scale * 60, air_height_percentage / 100 * scale * 123))

    # Draw all the lines
    for start_key, end_key in lines_to_draw:
        start_pos = origin + scaled_points[start_key]
        end_pos = origin + scaled_points[end_key]
        pg.draw.line(screen, rocket_color, start_pos, end_pos, thickness)

    fin_color = (200, 190, 150)
    pg.draw.polygon(screen, fin_color, poly_fin_right, 0)
    pg.draw.polygon(screen, fin_color, poly_fin_left, 0)

    # Erneutes Zeichnen der Linien der Rakete, die sonst von Finnen überdeckt werden
    pg.draw.line(screen, rocket_color, origin + scaled_points["b_r"], origin + scaled_points["op_r1"], thickness)
    pg.draw.line(screen, rocket_color, origin + scaled_points["op_r1"], origin + scaled_points["op_r2"], thickness)
    pg.draw.line(screen, rocket_color, origin + scaled_points["b_l"], origin + scaled_points["op_l1"], thickness)
    pg.draw.line(screen, rocket_color, origin + scaled_points["op_l1"], origin + scaled_points["op_l2"], thickness)

    draw_exhaust(screen, water_color, back_color, origin + scaled_points["op_l4"] + [scale * 16 / 2, 0], scale,
                 exhaust_velocity, t_elapsed)


def draw_exhaust(screen, water_color, back_color, position, scale, velocity, t_elapsed):
    time_factor = min(t_elapsed * 50, 1)  # Korrekturfaktor, um bei Animation nicht direkt mit vollem Strahl zu starten
    area = velocity * time_factor * 200  # Faktor beliebig, für gutes Verhältnis von (Ausstoß-)Geschwindigkeit und Fläche

    b1 = 16
    b2 = 20
    h = 250

    # Flächeninhalt "area", geometrische überlegung: A = b1 * z + 1/2 * (b2 - b1) * z / h * z
    exhaust_height_d = h * (-b1 + (b1 ** 2 + 2 * (b2 - b1) / h * area) ** 0.5) / (b2 - b1) * scale

    b1_d = scale * b1
    b2_d = scale * b2

    for j in range(int(exhaust_height_d)):
        p = j / int(exhaust_height_d)
        p_color = min(p, 1)
        k = 0.7
        # um einen "Fade" der Wasserfarbe zu erhalten
        color_r = int(water_color[0] + p_color ** k * (back_color[0] - water_color[0]))
        color_g = int(water_color[1] + p_color ** k * (back_color[1] - water_color[1]))
        color_b = int(water_color[2] + p_color ** k * (back_color[2] - water_color[2]))
        color = (color_r, color_g, color_b)
        delta_x1_d = -int(b1_d / 2 + (b2_d - b1_d) / 2 * p)
        delta_x2_d = int(b1_d / 2 + (b2_d - b1_d) / 2 * p)
        delta_y_d = int(p * exhaust_height_d)
        pg.draw.line(screen, color, position + (delta_x1_d, delta_y_d), position + (delta_x2_d, delta_y_d), 2)


decimal_separator = "."
def to_n_decimal_places(x, n):
    if x != 0:
        sign = x / abs(x)
    else:
        sign = 1
    z = abs(x)
    z_floor = int(z)
    z_str = str(z_floor)
    z_str += decimal_separator
    for j in range(n):
        z = (z - int(z)) * 10
        d = int(z)
        z_str += str(d)
    if sign == -1:
        z_str = "-" + z_str
    return z_str

v_exit = 0

t_prev = 0

while running:

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == VIDEORESIZE:
            screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                if stage == 0 and not (change_p or change_V):
                    stage = 1
                elif stage >= 1:
                    pausing = not pausing

            scale_change_keypress = False
            if event.key == K_UP:
                if not scale_change_keypress:
                    scale_index = min(scale_index + 1, len(scale_list) - 1)
                    scale = scale_list[scale_index]
                    scale_change_keypress = True
                    print("Scale:", scale)
            else:
                scale_change_keypress = False

            if event.key == K_DOWN:
                if not scale_change_keypress:
                    scale_index = max(scale_index - 1, 0)
                    scale = scale_list[scale_index]
                    scale_change_keypress = True
                    print("Scale:", scale)
            else:
                scale_change_keypress = False

            timestep_change_keypress = False
            if event.key == K_RIGHT:
                if not timestep_change_keypress:
                    timestep_index = min(timestep_index + 1, len(timestep_list) - 1)
                    timestep = timestep_list[timestep_index]
                    timestep_change_keypress = True
                    print("Timestep:", timestep)
            else:
                timestep_change_keypress = False

            if event.key == K_LEFT:
                if not timestep_change_keypress:
                    timestep_index = max(timestep_index - 1, 0)
                    timestep = timestep_list[timestep_index]
                    timestep_change_keypress = True
                    print("Timestep:", timestep)
            else:
                timestep_change_keypress = False

            if event.key == K_r:
                print("Reset key, stage:", stage)
                if stage == 3:
                    print("Reset")
                    stage = 0

                    has_landed = False
                    has_reached_max = False

                    # reset:

                    m_water_0 = rho_water * V_water_0
                    V_air_0 = V_rocket - V_water_0
                    V_air = V_air_0
                    p_abs_0 = p_atm + p_gauge
                    p_abs = p_abs_0
                    m_water = m_water_0

                    t = 0
                    y = 0
                    v = 0
                    a = 0

                    t_list = []
                    y_list = []
                    v_list = []
                    a_list = []
                    p_abs_list = []

                    t_prev = 0

            if stage == 0:
                if event.key == K_p:
                    if not change_p and not change_V:
                        change_p = True
                        p_entry = ""
                    elif change_p:
                        change_p = False
                    print("change_p:", change_p)

                if event.key == K_v:
                    if not change_p and not change_V:
                        change_V = True
                        V_entry = ""
                    elif change_V:
                        change_V = False
                    print("change_V:", change_V)

            num_entry_keys = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]

            if change_p:
                if event.key == K_ESCAPE:
                    change_p = False
                new_digit = ""
                for k_num, k in enumerate(num_entry_keys):
                    if event.key == k:
                        new_digit = str(k_num)
                if event.key == K_PERIOD or event.key == K_COMMA:
                    new_digit = "."
                elif event.key == K_BACKSPACE and len(p_entry) > 0:
                    p_entry = p_entry[:-1]
                elif event.key == K_RETURN:
                    change_p = False
                    try:
                        p_gauge = float(p_entry) * 10 ** 5
                        p_abs_0 = p_atm + p_gauge
                        p_abs = p_abs_0
                    except Exception as e:
                        print("Error:", e)
                p_entry = p_entry + new_digit

            elif change_V:
                if event.key == K_ESCAPE:
                    change_V = False
                new_digit = ""
                for k_num, k in enumerate(num_entry_keys):
                    if event.key == k:
                        new_digit = str(k_num)
                if event.key == K_PERIOD or event.key == K_COMMA:
                    new_digit = "."
                elif event.key == K_RETURN:
                    change_V = False
                    try:
                        V_water_percentage = float(V_entry)
                        if V_water_percentage >= 95:
                            V_water_percentage = 95
                        elif V_water_percentage <= 0:
                            V_water_percentage = 5
                        else:
                            V_water_0 = V_water_percentage / 100 * V_rocket
                            V_water = V_water_0
                            V_air = V_rocket - V_water
                            m_water_0 = rho_water * V_water
                            m_water = m_water_0
                            V_air_0 = V_air
                    except Exception as e:
                        print("Error:", e)
                V_entry = V_entry + new_digit

    if not pausing:
        if stage == 1:
            V_air = V_rocket - m_water / rho_water
            p_abs = p_abs_0 * (V_air_0 / V_air) ** gamma

            if p_abs < p_atm:
                v_exit = 0
            else:
                # velocity of water exiting the rocket
                v_exit = (2 * (p_abs - p_atm) / rho_water) ** 0.5

            # (water) mass flow rate
            m_water_dot = rho_water * A_nozzle * v_exit

            F_thrust = m_water_dot * v_exit

            m_total = m_rocket + m_water

            F_G = m_total * g
            F_D = 1 / 2 * rho_air * v ** 2 * C_D * A_rocket

            a = (F_thrust - F_G - F_D) / m_total

            v += a * dt
            y += v * dt

            t += dt

            m_water -= m_water_dot * dt

            if y <= 0:  # falls Höhe y während der ersten Stage kleiner als y wird (wegen zu geringem Rückstoß)
                y = 0
                stage = 3  # direkt zur Stage 3

            if m_water <= 0:  # Ende der ersten Stage (kein Wasser mehr in Rakete)
                stage = 2
                v_exit = 0
                p_abs = p_atm

        if stage == 2:

            F_G = m_rocket * g
            F_D = 1 / 2 * rho_air * v ** 2 * C_D * A_rocket

            a = (- F_G - np.sign(v) * F_D) / m_rocket
            v += a * dt
            y += v * dt

            t += dt

            if v <= 0 and not has_reached_max:
                print("Maximum height reached: z =", round(y, 2), "m at t =", round(t, 2), "s")
                has_reached_max = True
                y_max = y
                t_max = t

            if y <= 0 and not has_landed:
                y = 0
                v = 0
                a = 0
                print("Rocket has landed at t =", round(t, 2), "s")
                has_landed = True
                t_0 = t
                stage = 3

    if t - t_prev >= timestep or stage == 0 or stage == 3 or pausing:  # Animation des Raketen-Flugs (nicht für alle dt)

        t_prev = t

        # Fürs spätere Plotten: Aufnehmen der Werte t, y, v, a in Listen
        t_list.append(t)
        y_list.append(y)
        v_list.append(v)
        a_list.append(a)
        p_abs_list.append(p_abs / 10 ** 5)

        monitor_size = [pg.display.Info().current_w, pg.display.Info().current_h]
        width, height = monitor_size
        origin_d_ = np.array([width // 2, height // 2])

        screen_color = (235, 235, 235)
        screen.fill(screen_color)

        pg.draw.circle(screen, (255, 255, 0), origin_d_, 4)

        rocket_color = (50, 50, 50)
        water_color = (0, 200, 255)
        back_color = screen_color

        thickness = 1

        draw_rocket(screen, rocket_color, water_color, back_color, origin_d_ - (0, scale * 40), scale, thickness,
                    (m_water / rho_water) / V_rocket * 100, v_exit, t)

        ground_height_d = origin_d_[1] + y * y_scale * scale + scale * (104 - 40)

        pg.draw.line(screen, (0, 0, 0), (0, ground_height_d), (width, ground_height_d), 2)

        color_b = False
        color1 = (0, 0, 0)
        color2 = back_color

        for ky in range(int(y * y_scale * scale) * 2 + 50):

            tick_height_d = ground_height_d - ky * 0.5 * y_scale * scale

            if color_b:
                pg.draw.rect(screen, color1, (0, tick_height_d, 10, 0.5 * y_scale * scale))
            color_b = not color_b

            yT = ky * 0.5

            if scale_index == 0:
                if yT % 2 == 0:
                    pg.draw.line(screen, (0, 0, 0), (0, tick_height_d), (30, tick_height_d), 3)
                    textsurface = displayfont.render("{}.0".format(int(yT)), False,
                                                     (0, 0, 0))
                    screen.blit(textsurface, (40, tick_height_d - 17))
                else:
                    pg.draw.line(screen, (0, 0, 0), (0, tick_height_d), (18, tick_height_d), 3)

            elif scale_index == 1:
                if yT % 1 == 0:
                    pg.draw.line(screen, (0, 0, 0), (0, tick_height_d), (30, tick_height_d), 3)
                    textsurface = displayfont.render("{}.0".format(int(yT)), False,
                                                     (0, 0, 0))
                    screen.blit(textsurface, (40, tick_height_d - 17))
                else:
                    pg.draw.line(screen, (0, 0, 0), (0, tick_height_d), (18, tick_height_d), 3)

            else:
                if yT % 1 == 0:
                    pg.draw.line(screen, (0, 0, 0), (0, tick_height_d), (30, tick_height_d), 3)
                    textsurface = displayfont.render("{}.0".format(int(yT)), False,
                                                     (0, 0, 0))
                    screen.blit(textsurface, (40, tick_height_d - 17))
                else:
                    pg.draw.line(screen, (0, 0, 0), (0, tick_height_d), (18, tick_height_d), 3)
                    textsurface = displayfont.render("{}".format(round(yT, 1)), False,
                                                     (0, 0, 0))
                    screen.blit(textsurface, (40, tick_height_d - 17))

        y_max_text = "y_max = "
        t_max_text = "t_max = "
        if has_reached_max:
            y_max_text += str(to_n_decimal_places(y_max, 2)) + " m"
            t_max_text += str(to_n_decimal_places(t_max, 2)) + " s"
        else:
            y_max_text += "-"
            t_max_text += "-"

        if not change_p:
            p_gauge_text = "p_gauge = {} bar".format(to_n_decimal_places((p_abs - p_atm) / 10 ** 5, 2))
        else:
            if (i // 300) % 2 == 0:
                p_gauge_text = "p_gauge = {}| bar".format(p_entry)
            else:
                p_gauge_text = "p_gauge = {}  bar".format(p_entry)

        p_abs_text = "p_abs = {} bar".format(to_n_decimal_places(p_abs / 10 ** 5, 2))

        if not change_V:
            V_water_text = "V_water,% = {} %".format(round((V_rocket - V_air) / V_rocket * 100, 1))  # Wasserstand als Prozentzahl
        else:
            if (i // 300) % 2 == 0:
                V_water_text = "V_water,% = {}| %".format(V_entry)
            else:
                V_water_text = "V_water,% = {}  %".format(V_entry)

        V_air_text = "V_air,% = {} %".format(round((V_air) / V_rocket * 100, 1))

        v_exit_text = "v_exit = {} m/s".format(to_n_decimal_places(v_exit, 2))

        v_rocket_text = "v_rocket = {} m/s".format(to_n_decimal_places(v, 2))

        a_rocket_text = "a_rocket = {} m/s^2".format(to_n_decimal_places(a, 2))

        sim_speed_text = "Sim. Speed: {}".format(timestep_index + 1)

        x_text = width - 450
        y_text = 25

        y_text_spacing = 35
        y_text_spacing_gap = 45

        textsurface = displayfont.render(y_max_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text, y_text))
        y_text += y_text_spacing

        textsurface = displayfont.render(t_max_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text, y_text))
        y_text += y_text_spacing_gap

        textsurface = displayfont.render(p_gauge_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text - 18 * 2, y_text))
        y_text += y_text_spacing

        textsurface = displayfont.render(p_abs_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text, y_text))
        y_text += y_text_spacing_gap

        textsurface = displayfont.render(V_water_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text - 18 * 4, y_text))
        y_text += y_text_spacing

        # textsurface = displayfont.render(V_air_text, False, (0, 0, 0))
        # screen.blit(textsurface, (x_text - 18 * 2, y_text))
        # y_text += y_text_spacing_gap

        textsurface = displayfont.render(v_exit_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text - 18, y_text))
        y_text += y_text_spacing_gap

        textsurface = displayfont.render(v_rocket_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text - 18 * 3, y_text))
        y_text += y_text_spacing

        textsurface = displayfont.render(a_rocket_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text - 18 * 3, y_text))
        y_text += y_text_spacing_gap

        textsurface = displayfont.render(sim_speed_text, False, (0, 0, 0))
        screen.blit(textsurface, (x_text - 18 * 4, y_text))
        y_text += y_text_spacing

        pg.display.update()

    i += 1

pg.quit()

t_list = np.array(t_list)
v_list = np.array(v_list)
a_list = np.array(a_list)
y_list = np.array(y_list)
p_abs_list = np.array(p_abs_list)

plt.figure(figsize=(10, 6))
plt.plot(t_list, a_list, label = 'Beschleunigungsverlauf bei Wasservolumenanteil {} % '.format(V_water_0 / V_rocket * 100) )
plt.xlabel("Zeit $t$ [ s ]") 
plt.ylabel("Beschleunigung $a$ [ $\dfrac{m}{s^2}$ ]")
plt.axvline(0, color="black")
plt.axhline(0, color="black")
plt.legend(loc = "upper right")
plt.grid(linestyle='-', linewidth=2)
plt.savefig('{}_Zeit_Beschleunigung_Plot.png'.format(V_water_0 / V_rocket * 100))
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(t_list, v_list, label = 'Geschwindigkeitsverlauf bei Wasservolumenanteil {} % '.format(V_water_0 / V_rocket * 100))
plt.xlabel("Zeit $t$ [ s ]") 
plt.ylabel("Geschwindigkeit $v$ [ $\dfrac{m}{s}$ ]")
plt.axvline(0, color="black")
plt.axhline(0, color="black")
plt.legend(loc = "upper right")
plt.grid(linestyle='-', linewidth=2)
plt.savefig('{}_Zeit_Geschwindigkeit_Plot.png'.format(V_water_0 / V_rocket * 100))
plt.show()

plt.figure(figsize=(16, 9))
plt.plot(t_list, y_list, label = 'Höhenverlauf bei Wasservolumenanteil {} % '.format(V_water_0 / V_rocket * 100))
plt.xlabel("Zeit $t$ [ s ]") 
plt.ylabel("Höhe $h$ [ m ]")
plt.axvline(0, color="black")
plt.axhline(0, color="black")
plt.legend(loc = "upper right")
plt.grid(linestyle='-', linewidth=2)
plt.savefig('{}_Zeit_Höhe_Plot.png'.format(V_water_0 / V_rocket * 100))
plt.show()


plt.plot(t_list, p_abs_list, label = 'Druckverlauf bei einem Wasservolumenanteil von {} % '.format(V_water_0 / V_rocket * 100)  )
plt.xlabel("Zeit $t$ [ s ]") 
plt.ylabel("Druck $p$ [ bar ]")
plt.axvline(0, color="black")
plt.axhline(0, color="black")
plt.legend(loc = "upper right")
plt.grid(linestyle='-', linewidth=2)
plt.savefig('{}_Zeit_Druck_Plot.png'.format(V_water_0 / V_rocket * 100))
plt.show()

data = np.column_stack((t_list, a_list, v_list, y_list, p_abs_list))
np.savetxt("Daten_{}.csv".format(V_water_0 / V_rocket * 100), data, delimiter = ";", header = "Zeit; Beschleunigung; Geschwindigkeit; Höhe; Druck")
np.savetxt("Daten_{}.txt".format(V_water_0 / V_rocket * 100), data, header = "Zeit, Beschleunigung, Geschwindigkeit, Höhe; Druck")