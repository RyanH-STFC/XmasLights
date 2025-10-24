# pylint: disable = import-error, no-member
import time
import board
import neopixel

strip = neopixel.NeoPixel(board.GP16, 30, brightness=0.02)

print("rgb-pico is running")

strip.fill((0, 0, 0))


rgb = [0, 0, 0]
r = False
g = False
b = False
loop = False
eepy = 0.005

while True:
    while not r:
        if rgb[0] < 255:
            rgb[0] = rgb[0] + 1
        elif rgb[0] == 255:
            r = True
        print(tuple(rgb))
        time.sleep(eepy)
    while not g:
        if rgb[1] < 255:
            rgb[1] = rgb[1] + 1
            rgb[0] = rgb[0] - 1
        elif rgb[1] == 255:
            g = True
        print(tuple(rgb))
        time.sleep(eepy)
    while not b:
        if rgb[2] < 255:
            rgb[2] = rgb[2] + 1
            rgb[1] = rgb[1] - 1
        elif rgb[2] == 255:
            b = True
        print(tuple(rgb))
        time.sleep(eepy)
    while not loop:
        if rgb[0] < 255:
            rgb[2] = rgb[2] - 1
            rgb[0] = rgb[0] + 1
        elif rgb[0] == 255:
            loop = True
        print(tuple(rgb))
        time.sleep(eepy)
    r = False
    g = False
    b = False
    loop = False
