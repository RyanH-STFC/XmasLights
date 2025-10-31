"""
Script for raspberry pi pico to change neopixel lights on pin GP16
"""

# pylint: disable = import-error, no-member, no-else-return
import time
import board
import neopixel
import random

PIXEL_PIN = board.GP16
NUM_PIXELS = 30
PIXEL_BRIGHTNESS = 0.05

strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=PIXEL_BRIGHTNESS)
rgb = [255, 0, 0]
DEBUG_PRINT = False


def debug_print(msg, new_line=True):
    """
    A function that prints messages to stdout. for debugging purposes.

    :param msg: str,  The message to print
    :param new_line: bool,  To create a space underneath the message default is True
    :return: None
    """
    if DEBUG_PRINT and new_line:
        print(msg.upper(), "\n")
    elif DEBUG_PRINT:
        print(msg.upper())


def update_multiple_pixels(updates, delay=0.0):
    """
    Takes a list and goes through it and changes the pixels colour at the index of this #
    with the value at that element.

    :param updates: list[tuple[int, int, int]],  The list of updated for the LED's
    :param delay: float,  the delay between each update default is 0 seconds
    :return: None or List[tuple[int, int, int]]
    """
    debug_print(f"List to be updated:    {updates}")

    for index, colour in enumerate(updates):
        strip[index] = colour

        debug_print(f"UPDATED {index}: {colour}", False)

        time.sleep(delay)


def turn_black(delay=1.0):
    """
    Turns off all LED's, with debug print statement

    :param delay: float,  delay for after the pixels turn black, default is 1.0 seconds
    :return: None
    """
    debug_print("Turning pixels black")
    strip.fill((0, 0, 0))
    time.sleep(delay)


def rainbow_cycle(delay=0.002):
    """
    Main function for rainbow cycle.
    checks to see if any of the values in rgb are outside the range of 0 - 255
    if not then it runs running_function

    :param delay: float,  delay between changing the values of rgb
    (speed at which the colours change) default is 0.002 seconds
    :return: None
    """

    def running_function(
        increment_index,
        decrement_index,
    ):
        """
        The function that actually changes the colours of the LEDs

        :param increment_index: int,   the index of rgb to be incremented by 1 each loop
        :param decrement_index: int,   the index of rgb to be decremented by 1 each loop
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

    else:
        debug_print("BEGINNING OF RAINBOW CYCLE: (1/2)")
        running_function(1, 0)
        running_function(2, 1)
        running_function(0, 2)
        debug_print("END OF RAINBOW CYCLE: (2/2)")


def rainbow_wave(delay=0.03):
    """
    Call this function to create a wave of rainbow gradient colours.

    :param delay: float,  The speed at which the rainbow gradient colours
    change down the strip, default is 0.03
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
    ):
        """
        Function that creates the dictionary with the updates needed for the wave

        :param start_colour: tuple[int, int, int],   The Start colour of the rainbow gradient
        :param end_colour: tuple[int, int, int],   The End colour of the rainbow gradient
        :return: None
        """

        debug_print("Creating update dictionary", False)

        update_list = [
            (
                int(
                    start_colour[0]
                    + (end_colour[0] - start_colour[0]) * pixel / (NUM_PIXELS - 1)
                ),
                int(
                    start_colour[1]
                    + (end_colour[1] - start_colour[1]) * pixel / (NUM_PIXELS - 1)
                ),
                int(
                    start_colour[2]
                    + (end_colour[2] - start_colour[2]) * pixel / (NUM_PIXELS - 1)
                ),
            )
            for pixel in range(NUM_PIXELS)
        ]

        debug_print(f"{update_list}")

        update_multiple_pixels(update_list, delay)

    debug_print("WAVE STARTED (1/2)")
    for i in range(len(colour_sequence) - 1):
        running_function(colour_sequence[i], colour_sequence[i + 1])
    debug_print("WAVE FINISHED (2/2)")


def rainbow_wave_improved(delay=0.0, num_iterations=NUM_PIXELS):
    """
    Create a fixed rainbow gradient that moves across the LED strip.

    :param delay: float,   The speed of the wave movement, default is 0.0
    :param num_iterations: int,  Number of times to shift the gradient, default is number of pixels
    :return: None
    """
    debug_print("Creating Fixed Rainbow Gradient")

    def generate_fixed_rainbow_gradient():
        """
        Generate a complete rainbow gradient across the entire strip.

        :return: List of pixel colors
        """
        update_list = []
        for led in range(NUM_PIXELS):
            # Normalize pixel position to create a smooth rainbow gradient
            hue = led / NUM_PIXELS
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            update_list.append((int(r * 255), int(g * 255), int(b * 255)))

        return update_list

    def hsv_to_rgb(hue: float, saturation: float, value: float) -> tuple:
        """
        Convert HSV color space to RGB.

        :param hue: Hue (0-1)
        :param saturation: Saturation (0-1)
        :param value: Brightness (0-1)
        :return: RGB tuple (0-1 range)
        """
        # Determine which sector of the color wheel we're in
        hue_sector = int(hue * 6)

        # Fractional part within the sector
        hue_fraction = hue * 6 - hue_sector

        # Calculate intermediate values for color blending
        lowest_component = value * (1 - saturation)
        mid_low_component = value * (1 - hue_fraction * saturation)
        mid_high_component = value * (1 - (1 - hue_fraction) * saturation)

        # Map the sector to specific RGB combinations
        if hue_sector == 0:
            return value, mid_high_component, lowest_component
        elif hue_sector == 1:
            return mid_low_component, value, lowest_component
        elif hue_sector == 2:
            return lowest_component, value, mid_high_component
        elif hue_sector == 3:
            return lowest_component, mid_low_component, value
        elif hue_sector == 4:
            return mid_high_component, lowest_component, value
        else:  # hue_sector == 5
            return value, lowest_component, mid_low_component

    debug_print("Rainbow Wave Started")

    # Generate the initial rainbow gradient
    rainbow_gradient = generate_fixed_rainbow_gradient()

    # Shift the gradient multiple times
    for _ in range(num_iterations):
        # Update the strip with the current gradient
        update_multiple_pixels(rainbow_gradient)

        # Rotate the gradient by shifting color values
        rainbow_gradient = rainbow_gradient[1:] + rainbow_gradient[:1]
        time.sleep(delay)

    debug_print("Rainbow Wave Finished")


def sparkle_pixels(
    speed=0.33, colour=(255, 255, 255), intensity=0.33, cycles: int = 10
):
    """
    Create a random sparkling effect

    :param speed: float,   Time in seconds a set of sparkles last. default is 0.33
    :param colour: Tuple[int, int, int],     RGB colour. default is white (255,255,255)
    :param intensity: float,    Percentage of pixels to light up. default is 0.5
     (50% of amount of pixels at a max)
    :param cycles: int,    Number of sparkle cycles, default is 10
    :return: None
    """

    for c in range(cycles):
        debug_print(f"sparkling cycle {c} of {cycles}", True)

        pixel_list = [(0, 0, 0) for _ in range(NUM_PIXELS)]
        for _ in range(
            random.randint(
                round((NUM_PIXELS * intensity) / 2), round(NUM_PIXELS * intensity)
            )
        ):
            random_pixel = random.randint(0, NUM_PIXELS - 1)
            pixel_list[random_pixel] = colour

        update_multiple_pixels(pixel_list)
        time.sleep(speed)


while True:
    debug_print("BEGINNING OF WHILE LOOP (1/2)")

    turn_black()
    sparkle_pixels(cycles=15)
    rainbow_cycle()
    turn_black(0.5)
    rainbow_wave()
    turn_black(0.5)
    rainbow_wave_improved()
    turn_black(0.5)

    debug_print("END OF WHILE LOOP (2/2)")
