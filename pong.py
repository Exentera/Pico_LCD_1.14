from machine import Pin, SPI, PWM
import framebuf
import time
import random
from menu import LCD

speed_level = 5

# Joystick und Buttons     
up = Pin(2, Pin.IN, Pin.PULL_UP)
down = Pin(18, Pin.IN, Pin.PULL_UP)
left = Pin(16, Pin.IN, Pin.PULL_UP)
right = Pin(20, Pin.IN, Pin.PULL_UP)
btn_a = Pin(15, Pin.IN, Pin.PULL_UP)
btn_b = Pin(17, Pin.IN, Pin.PULL_UP)


def get_game_delay():
    return 0.03 + (5 - speed_level) * 0.005

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
        
        # Menüoptionen zeichnen
        for i, option in enumerate(menu_options):
            y = 30 + i * 20
            if i == selected:
                LCD.text(">" + option, 10, y, LCD.green)
            else:
                LCD.text(" " + option, 10, y, LCD.white)
        
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
            
        # Anpassung der Geschwindigkeit
        if not left.value() or not right.value():
            if selected == 0:
                if not left.value():
                    speed_level = max(1, speed_level - 1)
                else:
                    speed_level = min(10, speed_level + 1)
                menu_options[0] = "Speed: {}".format(speed_level)
                time.sleep(0.2)
        
        # Auswahl bestätigen
        if not btn_b.value():
            while not btn_b.value():
                time.sleep(0.05)
            time.sleep(0.3)
            if selected == 1:
                return True
            else:
                return False

def game_main():
    block_size = 10  
    paddle_height = 3 * block_size
    paddle_width = block_size
    
    # Spieler
    player_x = 2
    player_y = (LCD.height - paddle_height) // 2
    
    # KI
    ai_x = LCD.width - paddle_width - 2
    ai_y = (LCD.height - paddle_height) // 2
    
    # Ball initialisieren 
    ball_x = LCD.width // 2
    ball_y = LCD.height // 2
    # Ballgeschwindigkeit
    ball_vx = (speed_level * 2) if random.choice([True, False]) else -(speed_level * 2)
    ball_vy = random.choice([-speed_level * 2, speed_level * 2])
    
    # Punktestand
    player_score = 0
    ai_score = 0
    
    while True:
        # Optionsmenü öffnen
        if not btn_a.value():
            while not btn_a.value():
                time.sleep(0.05)
            time.sleep(0.2)
            if options_menu():
                return  # Zurück zum Hauptmenü
        if not up.value():
            player_y -= block_size
        elif not down.value():
            player_y += block_size
        
        if player_y < 0:
            player_y = 0
        if player_y > LCD.height - paddle_height:
            player_y = LCD.height - paddle_height
        
        if (ai_y + paddle_height // 2) < ball_y:
            ai_y += block_size
        elif (ai_y + paddle_height // 2) > ball_y:
            ai_y -= block_size
        if ai_y < 0:
            ai_y = 0
        if ai_y > LCD.height - paddle_height:
            ai_y = LCD.height - paddle_height
        
        # Ballposition aktualisieren
        ball_x += ball_vx
        ball_y += ball_vy
        
        if ball_y < 0:
            ball_y = 0
            ball_vy = -ball_vy
        if ball_y > LCD.height - block_size:
            ball_y = LCD.height - block_size
            ball_vy = -ball_vy
        
        # Kollision mit dem Spieler-Schläger (links)
        if ball_vx < 0:
            if ball_x <= player_x + paddle_width and ball_x >= player_x:
                if ball_y + block_size >= player_y and ball_y <= player_y + paddle_height:
                    ball_x = player_x + paddle_width  # Verhindert, dass der Ball im Schläger stecken bleibt
                    ball_vx = -ball_vx
        # Kollision mit dem KI-Schläger (rechts)
        if ball_vx > 0:
            if ball_x + block_size >= ai_x and ball_x + block_size <= ai_x + paddle_width:
                if ball_y + block_size >= ai_y and ball_y <= ai_y + paddle_height:
                    ball_x = ai_x - block_size
                    ball_vx = -ball_vx
        
        # Prüfe, ob der Ball den Bildschirm links oder rechts verlässt (Punkt für den Gegner)
        if ball_x < 0:
            ai_score += 1
            # Ball zurücksetzen und in Richtung Spieler starten
            ball_x = LCD.width // 2
            ball_y = LCD.height // 2
            ball_vx = speed_level * 2
            ball_vy = random.choice([-speed_level * 2, speed_level * 2])
            time.sleep(1)
        elif ball_x > LCD.width - block_size:
            player_score += 1
            ball_x = LCD.width // 2
            ball_y = LCD.height // 2
            ball_vx = -speed_level * 2
            ball_vy = random.choice([-speed_level * 2, speed_level * 2])
            time.sleep(1)
        
        # Spielgrafik zeichnen
        LCD.fill(LCD.black)
        LCD.fill_rect(int(ball_x), int(ball_y), block_size, block_size, LCD.white)
        LCD.fill_rect(player_x, player_y, paddle_width, paddle_height, LCD.white)
        LCD.fill_rect(ai_x, ai_y, paddle_width, paddle_height, LCD.white)
        LCD.text("P:{}".format(player_score), 5, 5, LCD.blue)
        LCD.text("AI:{}".format(ai_score), LCD.width - 50, 5, LCD.blue)
        LCD.show()
        time.sleep(get_game_delay())

if __name__ == '__main__':
    game_main()
