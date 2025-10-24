# pylint: disable = import-error, no-member
import time
import board
import neopixel

strip = neopixel.NeoPixel(board.GP16, 30, brightness=0.05)

print("rgb-pico is running")

rgb = [0, 0, 0]


def rainbow_cycle(
    strip,
    delay: float = 0.002,
) -> bool:

    def running_function(
        increment_index: int = None,
        decrement_index: int = None,
    ) -> None:

        for i in range(255):
            if increment_index is not None:
                rgb[increment_index] += 1
            if decrement_index is not None:
                rgb[decrement_index] -= 1

            print(rgb)
            strip.fill(tuple(rgb))
            time.sleep(delay)

    if all(0 <= element <= 254 for element in rgb):
        print("Return false")
        return False
    else:
        running_function()
        return True


while True:
    if not rainbow_cycle(strip):
        break
    print("LOOPING MAIN LOOP")
    print(rainbow_cycle(strip))
    rainbow_cycle(strip, 1)


r = False
g = False
b = False
loop = False
eepy = 0.002

while True:
    while not r:
        if rgb[0] < 255:
            rgb[0] = rgb[0] + 1
        elif rgb[0] == 255:
            r = True
        strip.fill(tuple(rgb))
        time.sleep(eepy)
    while not g:
        if rgb[1] < 255:
            rgb[1] = rgb[1] + 1
            rgb[0] = rgb[0] - 1
        elif rgb[1] == 255:
            g = True
        strip.fill(tuple(rgb))
        time.sleep(eepy)
    while not b:
        if rgb[2] < 255:
            rgb[2] = rgb[2] + 1
            rgb[1] = rgb[1] - 1
        elif rgb[2] == 255:
            b = True
        strip.fill(tuple(rgb))
        time.sleep(eepy)
    while not loop:
        if rgb[0] < 255:
            rgb[2] = rgb[2] - 1
            rgb[0] = rgb[0] + 1
        elif rgb[0] == 255:
            loop = True
        strip.fill(tuple(rgb))
        time.sleep(eepy)
    r = False
    g = False
    b = False
    loop = False
