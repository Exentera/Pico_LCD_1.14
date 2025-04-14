from machine import Pin, SPI, PWM
import framebuf
import time
import random
from set_lcd import LCD_1inch14
LCD = LCD_1inch14()

# Unsichtbare Wände aktivieren (Kollisionsprüfung an allen Rändern)
wall_collision_enabled = True

# Startgeschwindigkeit: Level 1 (max. 10)
speed_level = 1

# Joystick und Buttons
up = Pin(2, Pin.IN, Pin.PULL_UP)
down = Pin(18, Pin.IN, Pin.PULL_UP)
right = Pin(20, Pin.IN, Pin.PULL_UP)   # Wird für Rotation genutzt
left = Pin(16, Pin.IN, Pin.PULL_UP)    # Beschleunigt den Fall (Bewegung nach links)
btn_a = Pin(15, Pin.IN, Pin.PULL_UP)    # Öffnet das Optionsmenü / Select
btn_b = Pin(17, Pin.IN, Pin.PULL_UP)    # Dient als Continue im Optionsmenü

block_size = 10
grid_cols = LCD.width // block_size
grid_rows = LCD.height // block_size

def get_game_delay():
    # Startwert 0.5 s, abnehmend mit steigendem Level (aber nicht unter 0.1 s)
    delay = 0.5 - (speed_level - 1) * 0.05
    return delay if delay >= 0.1 else 0.1

# Definition der Tetromino-Formen (4-Blöcke, relativ zum Pivot)
tetrominoes = {
    'I': { 'shape': [(-1, 0), (0, 0), (1, 0), (2, 0)] },
    'J': { 'shape': [(-1, -1), (-1, 0), (0, 0), (1, 0)] },
    'L': { 'shape': [(1, -1), (-1, 0), (0, 0), (1, 0)] },
    'O': { 'shape': [(0, 0), (1, 0), (0, 1), (1, 1)] },
    'S': { 'shape': [(0, 0), (1, 0), (-1, 1), (0, 1)] },
    'T': { 'shape': [(-1, 0), (0, 0), (1, 0), (0, 1)] },
    'Z': { 'shape': [(-1, 0), (0, 0), (0, 1), (1, 1)] }
}

# Farbzuteilung – verwendet die in LCD_1inch14 definierten Farben
tetromino_colors = {
    'I': LCD.blue,
    'J': LCD.white,
    'L': LCD.red,
    'O': LCD.green,
    'S': LCD.white,
    'T': LCD.blue,
    'Z': LCD.red
}

def rotate(shape):
    # Drehung im Uhrzeigersinn: (x,y) -> (y, -x)
    return [(y, -x) for (x, y) in shape]

def create_new_piece():
    tetromino_type = random.choice(list(tetrominoes.keys()))
    shape = tetrominoes[tetromino_type]['shape']
    # Starte nahe der rechten Kante, mittig in y-Richtung
    pos = [grid_cols - 2, grid_rows // 2]
    return {'type': tetromino_type, 'shape': shape, 'pos': pos}

def get_piece_cells(piece):
    cells = []
    px, py = piece['pos']
    for dx, dy in piece['shape']:
        cells.append((px + dx, py + dy))
    return cells

def valid_position(piece, grid, offset):
    new_x = piece['pos'][0] + offset[0]
    new_y = piece['pos'][1] + offset[1]
    for dx, dy in piece['shape']:
        x = new_x + dx
        y = new_y + dy
        if wall_collision_enabled:
            if x < 0 or x >= grid_cols or y < 0 or y >= grid_rows:
                return False
        else:
            x = x % grid_cols
            y = y % grid_rows
        if grid[y][x] != 0:
            return False
    return True

def valid_rotation(piece, grid, new_shape):
    for dx, dy in new_shape:
        x = piece['pos'][0] + dx
        y = piece['pos'][1] + dy
        if wall_collision_enabled:
            if x < 0 or x >= grid_cols or y < 0 or y >= grid_rows:
                return False
        else:
            x = x % grid_cols
            y = y % grid_rows
        if grid[y][x] != 0:
            return False
    return True

def lock_piece(piece, grid):
    color = tetromino_colors[piece['type']]
    for x, y in get_piece_cells(piece):
        grid[y][x] = color

def clear_full_columns(grid):
    """
    Prüft jede Spalte (entsprechend der Fallrichtung, da Steine von rechts kommen).
    Ist eine Spalte vollständig gefüllt, wird sie entfernt und
    in jeder Zeile wird am rechten Ende ein leeres Feld (0) angehängt.
    """
    cleared = 0
    col = 0
    while col < grid_cols:
        full = True
        for row in range(grid_rows):
            if grid[row][col] == 0:
                full = False
                break
        if full:
            for row in range(grid_rows):
                grid[row].pop(col)
                grid[row].append(0)
            cleared += 1
            # Nach dem Löschen derselben Spalte wird nicht col erhöht,
            # da die nachfolgenden Spalten nach links rutschen.
        else:
            col += 1
    return cleared

def draw_grid(grid):
    for y in range(grid_rows):
        for x in range(grid_cols):
            if grid[y][x] != 0:
                LCD.fill_rect(x * block_size, y * block_size, block_size, block_size, grid[y][x])

def draw_piece(piece):
    color = tetromino_colors[piece['type']]
    for x, y in get_piece_cells(piece):
        LCD.fill_rect(x * block_size, y * block_size, block_size, block_size, color)

def draw_rotated_text(text, x, y, color):
    # Zeichnet den Text um 90° counterclockwise, sodass der Score korrekt ausgerichtet ist.
    font_width = 8
    font_height = 8
    text_width = len(text) * font_width
    text_height = font_height
    buf = bytearray(text_width * text_height * 2)
    temp_fb = framebuf.FrameBuffer(buf, text_width, text_height, framebuf.RGB565)
    temp_fb.fill(LCD.black)
    temp_fb.text(text, 0, 0, color)
    for i in range(text_width):
        for j in range(text_height):
            c = temp_fb.pixel(i, j)
            if c != LCD.black:
                # 90° counterclockwise: (i,j) -> ((font_height - 1 - j), i)
                LCD.pixel(x + (font_height - 1 - j), y + i, c)

def options_menu():
    global speed_level
    menu_options = [
        "Speed: {}".format(speed_level),
        "Back to Main Menu"
    ]
    selected = 0
    while True:
        LCD.fill(LCD.black)
        LCD.text("Options", 10, 10, LCD.white)
        for i, option in enumerate(menu_options):
            y = 30 + i * 20
            if i == selected:
                LCD.text(">" + option, 10, y, LCD.green)
            else:
                LCD.text(" " + option, 10, y, LCD.white)
        LCD.text("B: Select | A: Continue", 10, LCD.height - 20, LCD.white)
        LCD.show()
        time.sleep(0.1)
        if not up.value():
            selected = (selected - 1) % len(menu_options)
            time.sleep(0.2)
        elif not down.value():
            selected = (selected + 1) % len(menu_options)
            time.sleep(0.2)
        if not btn_b.value():
            while not btn_b.value():
                time.sleep(0.05)
            time.sleep(0.3)
            return True if selected == 1 else False
        if not btn_a.value():
            while not btn_a.value():
                time.sleep(0.05)
            time.sleep(0.3)
            return False

def game_main():
    global speed_level
    # Erzeuge ein leeres Spielfeld (Grid)
    grid = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]
    score = 0
    piece = create_new_piece()
    fall_timer = 0
    last_time = time.ticks_ms()
    lines_cleared_counter = 0  # Zählt die insgesamt entfernten Linien

    while True:
        current_time = time.ticks_ms()
        dt = time.ticks_diff(current_time, last_time) / 1000.0
        last_time = current_time
        fall_timer += dt

        # Optionen öffnen mit btn_A
        if not btn_a.value():
            while not btn_a.value():
                time.sleep(0.05)
            time.sleep(0.2)
            if options_menu():
                return

        # Steuerung:
        # Vertikale Bewegung
        if not up.value():
            if valid_position(piece, grid, (0, -1)):
                piece['pos'][1] -= 1
            time.sleep(0.2)
        if not down.value():
            if valid_position(piece, grid, (0, 1)):
                piece['pos'][1] += 1
            time.sleep(0.2)
        # Rotation per rechtem Stick
        if not right.value():
            new_shape = rotate(piece['shape'])
            if valid_rotation(piece, grid, new_shape):
                piece['shape'] = new_shape
            time.sleep(0.2)
        # Beschleunigung in Fallrichtung (links)
        if not left.value():
            if valid_position(piece, grid, (-1, 0)):
                piece['pos'][0] -= 1
            time.sleep(0.1)

        # Automatischer Fall (Bewegung nach links)
        if fall_timer >= get_game_delay():
            fall_timer = 0
            if valid_position(piece, grid, (-1, 0)):
                piece['pos'][0] -= 1
            else:
                lock_piece(piece, grid)
                # Prüfe, ob Spalten komplett gefüllt sind und lasse Blöcke "fallen"
                cleared = clear_full_columns(grid)
                if cleared > 0:
                    score += 100 * cleared
                    lines_cleared_counter += cleared
                    # Geschwindigkeit nur erhöhen, wenn insgesamt 5 Linien entfernt wurden
                    if lines_cleared_counter >= 5:
                        speed_level = speed_level + 1 if speed_level < 10 else 10
                        lines_cleared_counter -= 5
                # Game Over, wenn in der rechten Spalte (Spawnbereich) ein Block liegt
                game_over_flag = any(grid[y][grid_cols - 1] != 0 for y in range(grid_rows))
                if game_over_flag:
                    break
                piece = create_new_piece()

        LCD.fill(LCD.black)
        draw_grid(grid)
        draw_piece(piece)
        score_text = "Score: {}".format(score)
        rotated_text_width = 8
        rotated_text_height = len(score_text) * 8
        score_x = LCD.width - rotated_text_width
        score_y = (LCD.height - rotated_text_height) // 2
        draw_rotated_text(score_text, score_x, score_y, LCD.blue)
        LCD.show()

    # Game-Over-Bildschirm
    LCD.fill(LCD.black)
    LCD.text("Game Over", 80, 60, LCD.blue)
    LCD.text("Press B to restart", 40, 80, LCD.blue)
    LCD.show()
    while not btn_b.value():
        time.sleep(0.1)
    while btn_b.value():
        time.sleep(0.1)
    time.sleep(0.3)
    game_main()

if __name__ == '__main__':
    game_main()

