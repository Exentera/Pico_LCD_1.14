from machine import Pin, SPI, PWM
import framebuf
import time
import random
from menu import LCD  # Verwende die LCD-Instanz aus dem Hauptmenü

# Globale Variablen für Wandmodus und Geschwindigkeit
wall_collision_enabled = True
speed_level = 5

# Joystick und Buttons     
up = Pin(2, Pin.IN, Pin.PULL_UP)
down = Pin(18, Pin.IN, Pin.PULL_UP)
left = Pin(16, Pin.IN, Pin.PULL_UP)
right = Pin(20, Pin.IN, Pin.PULL_UP)
btn_a = Pin(15, Pin.IN, Pin.PULL_UP)
btn_b = Pin(17, Pin.IN, Pin.PULL_UP)

def get_game_delay():
    return 0.1 + (5 - speed_level) * 0.1

def random_position(grid_w, grid_h, block_size):
    return (random.randint(0, grid_w - 1) * block_size,
            random.randint(0, grid_h - 1) * block_size)

def reset_game(grid_w, grid_h, block_size):
    start_x = (grid_w // 2) * block_size
    start_y = (grid_h // 2) * block_size
    snake = [(start_x, start_y)]
    direction = (block_size, 0)
    fruit = random_position(grid_w, grid_h, block_size)
    while fruit in snake:
        fruit = random_position(grid_w, grid_h, block_size)
    return snake, direction, fruit

def options_menu():
    global speed_level, wall_collision_enabled
    menu_options = [
        "Speed: {}".format(speed_level),
        "Walls: {}".format("On" if wall_collision_enabled else "Off"),
        "Back to Main Menu"
    ]
    selected = 0
    
    while True:
        LCD.fill(LCD.black)
        LCD.text("Options", 10, 10, LCD.white)
        
        # Menüoptionen zeichnen
        for i, option in enumerate(menu_options):
            y = 30 + i * 20
            if i == selected:
                LCD.text(">" + option, 10, y, LCD.green)
            else:
                LCD.text(" " + option, 10, y, LCD.white)
        
        # Hinweistext anpassen – nun: A zum Auswählen
        LCD.text("A: Continue | B: Select", 10, LCD.height - 20, LCD.white)
        LCD.show()
        time.sleep(0.1)
        
        # Navigation
        if not up.value():
            selected = (selected - 1) % len(menu_options)
            time.sleep(0.2)
        elif not down.value():
            selected = (selected + 1) % len(menu_options)
            time.sleep(0.2)
            
        # Änderungen mit Links/Rechts
        if not left.value() or not right.value():
            if selected == 0:  # Geschwindigkeit anpassen
                if not left.value():
                    speed_level = max(1, speed_level - 1)
                else:
                    speed_level = min(10, speed_level + 1)
                menu_options[0] = "Speed: {}".format(speed_level)
                time.sleep(0.2)
            elif selected == 1:  # Wandmodus umschalten
                wall_collision_enabled = not wall_collision_enabled
                menu_options[1] = "Walls: {}".format("On" if wall_collision_enabled else "Off")
                time.sleep(0.2)
        
        # Auswahl mit Button A (statt bisher B)
        if not btn_b.value():
            # Warten, bis Button B losgelassen wurde
            while not btn_b.value():
                time.sleep(0.05)
            time.sleep(0.3)  # kurze Entprellzeit
            if selected == 2:  # Zurück zum Hauptmenü
                return True
            else:
                return False

def game_main():
    block_size = 10  
    grid_w = LCD.width // block_size   
    grid_h = LCD.height // block_size    

    while True:
        snake, direction, fruit = reset_game(grid_w, grid_h, block_size)
        score = 0  
        game_over = False

        while not game_over:
            # Öffne das Optionsmenü, wenn Button B gedrückt wird
            if not btn_a.value():
                # Warten, bis Button B losgelassen wird
                while not btn_a.value():
                    time.sleep(0.05)
                time.sleep(0.2)  # Entprellung
                # Falls im Optionsmenü "Back to Main Menu" gewählt wurde, kehre zurück
                if options_menu():
                    return
                continue  # ansonsten Spiel fortsetzen

            # Steuerung der Schlange
            dx, dy = direction
            if not up.value() and dy == 0:
                direction = (0, -block_size)
            elif not down.value() and dy == 0:
                direction = (0, block_size)
            elif not left.value() and dx == 0:
                direction = (-block_size, 0)
            elif not right.value() and dx == 0:
                direction = (block_size, 0)

            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            if wall_collision_enabled:
                if (new_head[0] < 0 or new_head[0] >= grid_w * block_size or
                    new_head[1] < 0 or new_head[1] >= grid_h * block_size):
                    game_over = True
                    break
            else:
                new_head = (new_head[0] % (grid_w * block_size),
                            new_head[1] % (grid_h * block_size))

            if new_head in snake:
                game_over = True
                break

            snake.insert(0, new_head)
            if new_head == fruit:
                score += speed_level
                fruit = random_position(grid_w, grid_h, block_size)
                while fruit in snake:
                    fruit = random_position(grid_w, grid_h, block_size)
            else:
                snake.pop()

            LCD.fill(LCD.black)
            LCD.fill_rect(fruit[0], fruit[1], block_size, block_size, LCD.green)
            for seg in snake:
                LCD.fill_rect(seg[0], seg[1], block_size, block_size, LCD.red)

            if wall_collision_enabled:
                LCD.rect(1, 1, LCD.width - 2, LCD.height - 2, LCD.white)

            LCD.text("Score: {}".format(score), 5, LCD.height - 13, LCD.blue)
            LCD.show()
            time.sleep(get_game_delay())

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

if __name__ == '__main__':
    game_main()
