import gc

def start_snake_game(LCD, time):
    LCD.fill(LCD.black)
    LCD.text("Starting Snake...", 10, LCD.height // 2, LCD.white)
    LCD.show()
    time.sleep(1)
    try:
        gc.collect()
        import snake_0041
        snake_0041.game_main()
    except Exception as e:
        LCD.fill(LCD.black)
        LCD.text("Fehler:", 10, 30, LCD.red)
        LCD.text(str(e), 10, 50, LCD.red)
        LCD.show()
        time.sleep(3)

def start_pong_game(LCD, time):
    LCD.fill(LCD.black)
    LCD.text("Starting Pong...", 10, LCD.height // 2, LCD.white)
    LCD.show()
    time.sleep(1)
    try:
        gc.collect()
        import pong
        pong.game_main()
    except Exception as e:
        LCD.fill(LCD.black)
        LCD.text("Fehler:", 10, 30, LCD.red)
        LCD.text(str(e), 10, 50, LCD.red)
        LCD.show()
        time.sleep(3)
        
def start_tetris_game(LCD, time):
    LCD.fill(LCD.black)
    LCD.text("Starting Tetris...", 10, LCD.height // 2, LCD.white)
    LCD.show()
    time.sleep(1)
    try:
        gc.collect()
        import tetris
        tetris.game_main()
    except Exception as e:
        LCD.fill(LCD.black)
        LCD.text("Fehler:", 10, 30, LCD.red)
        LCD.text(str(e), 10, 50, LCD.red)
        LCD.show()
        time.sleep(3)

def start_pixelpaint(LCD, time):
    LCD.fill(LCD.black)
    LCD.text("Starting PixelPaint...", 10, LCD.height // 2, LCD.white)
    LCD.show()
    time.sleep(1)
    try:
        gc.collect()
        import pixelpaint
        pixelpaint.game_main()
    except Exception as e:
        LCD.fill(LCD.black)
        LCD.text("Fehler:", 10, 30, LCD.red)
        LCD.text(str(e), 10, 50, LCD.red)
        LCD.show()
        time.sleep(3)

# Example imports for menu.py
# from start_app import start_snake_game, start_pong_game, start_pixelpaint
# Usage:
# start_snake_game(LCD, time)
# start_pong_game(LCD, time)
# start_pixelpaint(LCD, time)
