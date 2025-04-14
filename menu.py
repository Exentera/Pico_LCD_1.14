from machine import Pin, SPI, PWM
import framebuf
import time
import gc
import set_lcd
import start_app

# Pin-Konfiguration LCD
BL   = 13
DC   = 8
RST  = 12
MOSI = 11
SCK  = 10
CS   = 9

# Joystick and Buttons
up      = Pin(2,  Pin.IN, Pin.PULL_UP)
down    = Pin(18, Pin.IN, Pin.PULL_UP)
left    = Pin(16, Pin.IN, Pin.PULL_UP)
right   = Pin(20, Pin.IN, Pin.PULL_UP)
center  = Pin(3,  Pin.IN, Pin.PULL_UP)
btn_a   = Pin(15, Pin.IN, Pin.PULL_UP)
btn_b   = Pin(17, Pin.IN, Pin.PULL_UP)  




# LCD initialisieren
pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)
LCD = set_lcd.LCD_1inch14()

# Menü

def main_menu():
    menu_options = ["Games", "Tools"]
    selected = 0

    while True:
        LCD.fill(LCD.black)
        LCD.text("Main Menue", 10, 10, LCD.white)
        for i, option in enumerate(menu_options):
            y = 30 + i * 20
            LCD.text(">" + option if i == selected else " " + option,
                     10, y, LCD.green if i == selected else LCD.white)
        LCD.text("B: Select", 10, LCD.height - 20, LCD.white)
        LCD.show()
        time.sleep(0.1)

        if not up.value():
            selected = (selected - 1) % len(menu_options)
            time.sleep(0.2)
        elif not down.value():
            selected = (selected + 1) % len(menu_options)
            time.sleep(0.2)
        elif not btn_b.value():
            if menu_options[selected] == "Games":
                game_menu()
            elif menu_options[selected] == "Tools":
                tools_menu()
            time.sleep(0.3)

def game_menu():
    game_options = ["Snake", "Pong","Tetris"]
    selected = 0

    while True:
        LCD.fill(LCD.black)
        LCD.text("Game Menu", 10, 10, LCD.white)
        for i, option in enumerate(game_options):
            y = 30 + i * 20
            if i == selected:
                LCD.text(">" + option, 10, y, LCD.green)
            else:
                LCD.text(" " + option, 10, y, LCD.white)
        LCD.text("B: Select  A: Back", 10, LCD.height - 20, LCD.white)
        LCD.show()
        time.sleep(0.1)

        if not btn_a.value():
            while not btn_a.value():
                time.sleep(0.05)
            time.sleep(0.2)
            return

        if not btn_b.value():
            if game_options[selected] == "Snake":
                start_app.start_snake_game(LCD, time)
            elif game_options[selected] == "Pong":
                start_app.start_pong_game(LCD, time)
            elif game_options[selected] == "Tetris":
                start_app.start_tetris_game(LCD, time)
            time.sleep(0.3)
            break

        if not up.value():
            selected = (selected - 1) % len(game_options)
            time.sleep(0.2)
        elif not down.value():
            selected = (selected + 1) % len(game_options)
            time.sleep(0.2)

def tools_menu():
    tool_options = ["PixelPaint", "Tool 2"]
    selected = 0

    while True:
        LCD.fill(LCD.black)
        LCD.text("Tools Menu", 10, 10, LCD.white)
        for i, option in enumerate(tool_options):
            y = 30 + i * 20
            LCD.text(">" + option if i == selected else " " + option,
                     10, y, LCD.green if i == selected else LCD.white)
        LCD.text("B: Select  A: Back", 10, LCD.height - 20, LCD.white)
        LCD.show()
        time.sleep(0.1)

        if not btn_a.value():
            while not btn_a.value():
                time.sleep(0.05)
            time.sleep(0.2)
            return

        if not btn_b.value():
            if tool_options[selected] == "PixelPaint":
                start_app.start_pixelpaint(LCD, time)
            else:
                LCD.fill(LCD.black)
                LCD.text("Selected: " + tool_options[selected],
                         10, LCD.height // 2, LCD.white)
                lcd.show()
                time.sleep(1)
            time.sleep(0.3)

        if not up.value():
            selected = (selected - 1) % len(tool_options)
            time.sleep(0.2)
        elif not down.value():
            selected = (selected + 1) % len(tool_options)
            time.sleep(0.2)



if __name__ == '__main__':
    main_menu()

