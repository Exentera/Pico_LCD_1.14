from machine import Pin, SPI, PWM
import framebuf
import time
import gc
from menu import LCD  

up      = Pin(2,  Pin.IN, Pin.PULL_UP)
down    = Pin(18, Pin.IN, Pin.PULL_UP)
left    = Pin(16, Pin.IN, Pin.PULL_UP)
right   = Pin(20, Pin.IN, Pin.PULL_UP)
btn_a   = Pin(15, Pin.IN, Pin.PULL_UP)  
btn_b   = Pin(17, Pin.IN, Pin.PULL_UP)  


available_colors = [
    ("Black", LCD.black),
    ("Red", 0x07E0),
    ("Green", 0x001F),
    ("Blue", 0xF800),
    ("White", LCD.white),
    ("Yellow", 0x07FF),
    ("Cyan", 0xF81F),
    ("Purple", 0xFFE0)
]

# Raster initialisieren
def reset_grid(cell_size):
    grid_w = LCD.width // cell_size
    grid_h = LCD.height // cell_size

    grid = [[available_colors[0][1] for _ in range(grid_w)] for _ in range(grid_h)]
    return grid, grid_w, grid_h

# Optionsmenü
# Optionen: Zellengröße, Zeichenfarbe, BG Fill-Farbe und Main Menu.
# Durch Links-/Rechts-Tasten werden die Werte angepasst.
# Wird "BG Fill" bestätigt (Option 2), wird das Raster gefüllt.
# Rückgabewerte: cell_size, current_color_index, current_bg_index, exit_to_main, fill_bg
def options_menu(cell_size, current_color_index, current_bg_index):
    options = [
        "Cell Size: {}".format(cell_size),
        "Color: {}".format(available_colors[current_color_index][0]),
        "BG Fill: {}".format(available_colors[current_bg_index][0]),
        "Main Menu"
    ]
    selected = 0

    while True:
        LCD.fill(LCD.black)
        LCD.text("Options", 10, 10, LCD.white)
        for i, opt in enumerate(options):
            y = 30 + i * 20
            if i == selected:
                LCD.text(">" + opt, 10, y, LCD.green)
            else:
                LCD.text(" " + opt, 10, y, LCD.white)
        LCD.text("B: Select", 10, LCD.height - 20, LCD.white)
        LCD.show()
        time.sleep(0.1)

        if not up.value():
            selected = (selected - 1) % len(options)
            time.sleep(0.2)
        elif not down.value():
            selected = (selected + 1) % len(options)
            time.sleep(0.2)

        # Links/Rechts zum Anpassen der Werte
        if not left.value() or not right.value():
            if selected == 0:  # Zellengröße anpassen (min. 5, max. 20)
                if not left.value():
                    cell_size = max(5, cell_size - 1)
                else:
                    cell_size = min(20, cell_size + 1)
                options[0] = "Cell Size: {}".format(cell_size)
                time.sleep(0.2)
            elif selected == 1:  # Zeichenfarbe anpassen
                if not left.value():
                    current_color_index = (current_color_index - 1) % len(available_colors)
                else:
                    current_color_index = (current_color_index + 1) % len(available_colors)
                options[1] = "Color: {}".format(available_colors[current_color_index][0])
                time.sleep(0.2)
            elif selected == 2:  # BG Fill-Farbe anpassen
                if not left.value():
                    current_bg_index = (current_bg_index - 1) % len(available_colors)
                else:
                    current_bg_index = (current_bg_index + 1) % len(available_colors)
                options[2] = "BG Fill: {}".format(available_colors[current_bg_index][0])
                time.sleep(0.2)

        if not btn_b.value():
            while not btn_b.value():
                time.sleep(0.05)
            time.sleep(0.3)
            if selected == 3:  # Main Menu
                return cell_size, current_color_index, current_bg_index, True, False
            elif selected == 2:  # BG Fill soll das Raster füllen
                return cell_size, current_color_index, current_bg_index, False, True
            else:
                return cell_size, current_color_index, current_bg_index, False, False

# Hauptfunktion des PixelPaint-Programms
def game_main():
    cell_size = 10                    # Anfangs-Zellengröße
    current_color_index = 1           # Standard-Zeichenfarbe (z.B. "Red")
    current_bg_index = 0              # Standard-Hintergrundfarbe ("Black")
    grid, grid_w, grid_h = reset_grid(cell_size)
    # Cursor-Position (Start in der Rastermitte)
    cursor_x = grid_w // 2
    cursor_y = grid_h // 2

    while True:
        # Mit A ins Optionsmenü
        if not btn_a.value():
            while not btn_a.value():
                time.sleep(0.05)
            time.sleep(0.2)
            old_cell_size = cell_size
            cell_size, current_color_index, current_bg_index, exit_to_main, fill_bg = options_menu(cell_size, current_color_index, current_bg_index)
            if exit_to_main:
                return  # Rückkehr ins Hauptmenü
            # Nur neu initialisieren, wenn sich die Zellengröße geändert hat.
            if cell_size != old_cell_size:
                grid, grid_w, grid_h = reset_grid(cell_size)
                cursor_x = grid_w // 2
                cursor_y = grid_h // 2
            else:
                if fill_bg:
                    fill_color = available_colors[current_bg_index][1]
                    for y in range(grid_h):
                        for x in range(grid_w):
                            grid[y][x] = fill_color

        # Steuerung des Cursors über den Joystick
        if not up.value():
            cursor_y = max(0, cursor_y - 1)
            time.sleep(0.2)
        elif not down.value():
            cursor_y = min(grid_h - 1, cursor_y + 1)
            time.sleep(0.2)
        elif not left.value():
            cursor_x = max(0, cursor_x - 1)
            time.sleep(0.2)
        elif not right.value():
            cursor_x = min(grid_w - 1, cursor_x + 1)
            time.sleep(0.2)

        # Mit B wird der aktuelle Zelle in der aktuell gewählten Zeichenfarbe gesetzt
        if not btn_b.value():
            grid[cursor_y][cursor_x] = available_colors[current_color_index][1]
            time.sleep(0.2)

        # Zeichne das Raster
        LCD.fill(available_colors[current_bg_index][1])
        for y in range(grid_h):
            for x in range(grid_w):
                color = grid[y][x]
                LCD.fill_rect(x * cell_size, y * cell_size, cell_size, cell_size, color)
        # Cursor weißen Rahmen
        LCD.rect(cursor_x * cell_size, cursor_y * cell_size, cell_size, cell_size, LCD.white)
        LCD.show()
        time.sleep(0.05)

if __name__ == '__main__':
    game_main()
