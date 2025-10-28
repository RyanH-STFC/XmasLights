"""
Script for raspberry pi pico to change neopixel lights on pin GP16
"""

# pylint: disable = import-error, no-member, no-else-return
import time
import board
import neopixel

PIXEL_PIN = board.GP16
NUM_PIXELS = 30
PIXEL_BRIGHTNESS = 0.05

strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=PIXEL_BRIGHTNESS)
rgb = [255, 0, 0]
DEBUG_PRINT = True

def debug_print(msg: str, new_line: bool = True) -> None:
    """
    A function that prints messages to stdout. for debugging purposes.

    :param msg: The message to print
    :param new_line: Bool value, True to create a space underneath the message, default is True
    :return: None
    """
    if DEBUG_PRINT & new_line:
        print(msg, "\n")
    elif DEBUG_PRINT:
            print(msg)


def rainbow_cycle(delay: float = 0.002) -> bool:
    """
    Main function for rainbow cycle.
    checks to see if any of the values in rgb are outside the range of 0 - 255
    if not then it runs running_function

    :param delay: delay between changing the values of rgb (speed at which the colours change)
    :return: True if it worked, False otherwise
    """

    def running_function(
        increment_index: int = None,
        decrement_index: int = None,
    ) -> None:
        """
        The function that actually changes the colours of the LEDs

        :param increment_index: the index of rgb to be incremented by 1 each loop
        :param decrement_index: the index of rgb to be decremented by 1 each loop
        :return: None
        """
        for _ in range(255):
            if increment_index is not None:
                rgb[increment_index] += 1
            if decrement_index is not None:
                rgb[decrement_index] -= 1

            debug_print(f"Red:{rgb[0]} Green:{rgb[1]} Blue:{rgb[2]}", False)

            strip.fill(tuple(rgb))
            time.sleep(delay)

    if all(0 <= element < 255 for element in rgb):
        debug_print(f"ONE OF THE RGB VALUES WENT OUT OF BOUNDS {rgb}", True)
        return False

    else:
        debug_print("BEGINNING OF RAINBOW CYCLE: (1/2)")
        running_function(1, 0)
        running_function(2, 1)
        running_function(0, 2)
        debug_print("END OF RAINBOW CYCLE: (2/2)")
        return True

def update_multiple_pixels(
    pixels,
    updates,
    delay: float = 0
) -> None:
    """
    Takes in the strip of LED's and updates each LED's colour value
    based on the value of the key given
    The key also is the index of which the LED is to be updated

    :param pixels: List[Tuple[int, int, int]]    The list of the strip of LED's
    :param updates:  Dict[int, Tuple[int, int, int]]    The dictionary of updated for the LED's
    :param delay: the delay between each update
    :return: None
    """
    for index, colour in updates.items():
        pixels[index] = colour

        debug_print(f"UPDATED {index}: {colour}", False)

        if delay > 0:
            time.sleep(delay)


def rainbow_wave(delay: float = 0.002) -> None:
    """
    Call this function to create a wave of rainbow gradient colours.

    :param delay: The speed at which the rainbow gradient colours change down the strip
    :return: None
    """
    debug_print("Creating Colour sequence")
    colour_sequence = [
        (255, 0, 0),  # Red
        (255, 255, 0),  # Yellow
        (0, 255, 0),  # Green
        (0, 255, 255),  # Cyan
        (0, 0, 255),  # Blue
        (255, 0, 255),  # Magenta
    ]

    def running_function(
        start_colour,
        end_colour,
        num_pixels: int,
    ) -> None:
        """
        Function that creates the dictionary with the updates needed for the wave

        :param start_colour: TYPE-Tuple. The Start colour of the rainbow gradient
        :param end_colour: TYPE-Tuple. The End colour of the rainbow gradient
        :param num_pixels: The number of pixels in strip (elements in the list)
        :return: None
        """

        debug_print("Creating update dictionary", False)

        update_dict = {
            pixel: (
                int(
                    start_colour[0]
                    + (end_colour[0] - start_colour[0]) * pixel / (num_pixels - 1)
                ),
                int(
                    start_colour[1]
                    + (end_colour[1] - start_colour[1]) * pixel / (num_pixels - 1)
                ),
                int(
                    start_colour[2]
                    + (end_colour[2] - start_colour[2]) * pixel / (num_pixels - 1)
                ),
            )
            for pixel in range(num_pixels)
        }

        debug_print(f"{update_dict}")

        update_multiple_pixels(strip, update_dict, delay)

    debug_print("WAVE STARTED (1/2)")
    for i in range(len(colour_sequence) - 1):
        running_function(colour_sequence[i], colour_sequence[i+1], NUM_PIXELS)
    debug_print("WAVE FINISHED (2/2)")

while True:
    # debug_print("Turning pixels black")
    # strip.fill((0, 0, 0))
    # time.sleep(1)

    debug_print("BEGINNING OF PIXEL SEQUENCE")

    rainbow_wave(0.03)
    # rainbow_cycle()
