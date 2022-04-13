from cProfile import label
import tkinter
import random
import time
import numpy as np
from pygame import mixer

#
# Constants
#

WIN_WIDTH = 400
WIN_HEIGHT = 600

MARGIN_LEFT = 20
MARGIN_RIGHT = 20
MARGIN_TOP = 30
PAD = 5
WIDTH = 20
HEIGHT = 20

AREA_WIDTH = 10
AREA_HEIGHT = 20

LINE = [
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
]

SQUARE = [
    [1, 1],
    [1, 1],
]

CORNER_R = [
    [1, 1, 1],
    [1, 0, 0],
    [0, 0, 0],
]
CORNER_L = [
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 0],
]

ZIGZAG_R = [
    [0, 1, 1],
    [1, 1, 0],
    [0, 0, 0],
]

ZIGZAG_L = [
    [1, 1, 0],
    [0, 1, 1],
    [0, 0, 0],
]

TEE = [
    [1, 1, 1],
    [0, 1, 0],
    [0, 0, 0],
]


class Score:
    def __init__(self) -> None:
        global win
        self.value = 0
        self.label = tkinter.Label(win, text="Score", font=("Helvetica", 25))
        self.label.place(x=MARGIN_LEFT + (PAD + WIDTH) * AREA_WIDTH + MARGIN_RIGHT,
                         y=MARGIN_TOP)
        self.strval = tkinter.StringVar()
        self.strval.set(str(self.value))
        self.text = tkinter.Label(
            win, textvariable=self.strval, font=("Helvetica", 20))
        self.text.place(x=MARGIN_LEFT + (PAD + WIDTH) * AREA_WIDTH + MARGIN_RIGHT,
                        y=MARGIN_TOP + 40)

    def add(self):
        self.value += 1
        self.strval.set(str(self.value))


#
# Variables
#

cursor = {"x": 0, "y": 0}
shape = None
exit_game = False

#
# Init
#

data = [[False for x in range(0, AREA_WIDTH)] for z in range(0, AREA_HEIGHT)]
win = tkinter.Tk(screenName="Tetris", className="Tetris")
win.geometry("%sx%s" % (WIN_WIDTH, WIN_HEIGHT))

canvas = tkinter.Canvas(width=WIN_WIDTH, height=WIN_HEIGHT)
score = Score()


mixer.init()
sound = mixer.Sound("sounds/background.wav")
sound.set_volume(0.25)
sound.play(loops=-1)

game_over = mixer.Sound("sounds/game_over.wav")
game_over.set_volume(0.5)

click = mixer.Sound("sounds/click.wav")
click.set_volume(0.5)

cleared = mixer.Sound("sounds/clear.wav")
cleared.set_volume(0.5)


def new_shape():
    global shape
    val = random.randrange(0, 7)
    if val == 0:
        shape = LINE
    elif val == 1:
        shape = SQUARE
    elif val == 2:
        shape = CORNER_L
    elif val == 3:
        shape = CORNER_R
    elif val == 4:
        shape = ZIGZAG_R
    elif val == 5:
        shape = ZIGZAG_L
    else:
        shape = TEE

    cursor["x"] = int(AREA_WIDTH / 2)
    cursor["y"] = AREA_HEIGHT

    for i in range(4):
        if shape_is_inside(0, 0):
            break
        else:
            cursor["y"] -= 1

    if not shape_is_inside(0, 0):
        global exit_game
        exit_game = True


def freeze_shape():
    click.play()
    for y in range(0, len(shape)):
        for x in range(0, len(shape[y])):
            if shape[y][x] != 0:
                data[cursor["y"] + y][cursor["x"] + x] = True


def is_inside(obj, nx, ny):
    for y in range(0, len(obj)):
        for x in range(0, len(obj[y])):
            if obj[y][x] != 0:
                tx = cursor["x"] + x + nx
                ty = cursor["y"] + y + ny

                if tx < 0 or tx >= AREA_WIDTH or ty < 0 or ty >= AREA_HEIGHT:
                    return False
                elif data[ty][tx]:
                    return False
    return True


def shape_is_inside(nx, ny):
    return is_inside(shape, nx, ny)


def empty_row():
    return [False for x in range(0, AREA_WIDTH)]


def rotate(dir):
    global shape
    next_shape = np.rot90(shape, dir)
    if is_inside(next_shape, 0, 0):
        shape = next_shape


def input_handler(event):
    global shape

    if event.keysym == "Left" or event.keysym == "a":
        if shape_is_inside(-1, 0):
            cursor["x"] -= 1

    elif event.keysym == "Right" or event.keysym == "d":
        if shape_is_inside(1, 0):
            cursor["x"] += 1

    elif event.keysym == "Down" or event.keysym == "s":
        if not check_shape_collided(0, -1):
            cursor["y"] -= 1

    # elif event.keysym == "Up" or event.keysym == "w":
    #     if shape_is_inside(0, 1):
    #         cursor["y"] += 1

    elif event.keysym == "space":
        data[cursor["y"]][cursor["x"]] = not data[cursor["y"]][cursor["x"]]

    # elif event.keysym == "r":
    #     new_shape()

    elif event.keysym == "e":
        rotate(1)

    elif event.keysym == "q":
        rotate(3)

    draw_window()


def check_full_rows():
    for r in range(0, len(data)):
        if all(i for i in data[r]):
            del data[r]
            data.append(empty_row())
            check_full_rows()
            global score
            score.add()
            return True
    return False


def draw_shape():
    global shape
    assert(shape is not None)

    for y in range(0, len(shape)):
        for x in range(0, len(shape[y])):
            if shape[y][x] != 0:
                draw_block(cursor["x"] + x, cursor["y"] + y, "blue", "white")


def draw_block(x, y, fill, outline):
    x = MARGIN_LEFT + (PAD + WIDTH) * x
    y = MARGIN_TOP + (PAD + HEIGHT) * (AREA_HEIGHT - y)
    canvas.create_rectangle(
        (x, y), (x + WIDTH), (y + HEIGHT), fill=fill, outline=outline)


def check_shape_collided(nx, ny):
    if not shape_is_inside(nx, ny):
        freeze_shape()
        new_shape()
        return True
    return False


def advance_cursor():
    if not check_shape_collided(0, -1):
        cursor["y"] -= 1


def draw_window():
    canvas.delete("all")

    for y in range(0, AREA_HEIGHT):
        for x in range(0, AREA_WIDTH):
            fill = "red" if data[y][x] else "white"
            draw_block(x, y, fill, "white")

    draw_shape()

    canvas.pack()


def main_loop():
    #
    # Logic
    #
    global shape
    if shape is None:
        new_shape()

    if check_full_rows():
        cleared.play()

    advance_cursor()

    draw_window()

    win.after(1000, main_loop)

    if exit_game:
        sound.stop()
        game_over.play()
        time.sleep(game_over.get_length())
        win.destroy()


win.bind("<Key>", input_handler)
win.after(0, main_loop)
win.mainloop()
