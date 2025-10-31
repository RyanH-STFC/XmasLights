"""
Script for raspberry pi pico to change neopixel lights on pin GP16
"""

# pylint: disable = import-error, no-member, no-else-return, too-many-locals
import time
import random
import board
import neopixel


PIXEL_PIN = board.GP16
NUM_PIXELS = 30
PIXEL_BRIGHTNESS = 0.05

strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=PIXEL_BRIGHTNESS)
DEBUG_PRINT = True


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
    Main function for rainbow cycle using update_multiple_pixels.
    :param delay: float, delay between colour steps
    """
    debug_print("BEGINNING OF RAINBOW CYCLE (1/2)")

    rgb_local = [255, 0, 0]

    def running_function(increment_index, decrement_index):
        """
        Increment one channel and decrement another over 255 steps,
        updating all pixels to the current rgb_local value each step.
        """

        for _ in range(255):
            if increment_index is not None:
                rgb_local[increment_index] = min(255, rgb_local[increment_index] + 1)
            if decrement_index is not None:
                rgb_local[decrement_index] = max(0, rgb_local[decrement_index] - 1)

            # colour_list = [tuple(rgb_local) for _ in range(NUM_PIXELS)]

            strip.fill(rgb_local)
            time.sleep(delay)

    if not all(0 <= element <= 255 for element in rgb_local):
        debug_print(f"ONE OF THE RGB VALUES WENT OUT OF BOUNDS {rgb_local}", True)
        return

    running_function(1, 0)
    running_function(2, 1)
    running_function(0, 2)

    debug_print("END OF RAINBOW CYCLE (2/2)")


def rainbow_wave(delay=0.03):
    """
    Create a wave of rainbow gradient colours across the strip.

    :param delay: float, speed at which the rainbow gradient moves down the strip
    :return: None
    """
    debug_print("Creating Colour sequence (optimized)")

    colour_sequence = [
        (255, 0, 0),  # Red
        (255, 255, 0),  # Yellow
        (0, 255, 0),  # Green
        (0, 255, 255),  # Cyan
        (0, 0, 255),  # Blue
        (255, 0, 255),  # Magenta
    ]

    num_pixels_take_one = NUM_PIXELS - 1 if NUM_PIXELS > 1 else 1

    def build_gradient(start_colour, end_colour):
        """Return list of NUM_PIXELS tuples forming a linear gradient between two colours."""
        sr, sg, sb = start_colour
        er, eg, eb = end_colour

        step_r = (er - sr) / num_pixels_take_one
        step_g = (eg - sg) / num_pixels_take_one
        step_b = (eb - sb) / num_pixels_take_one

        gradient = []
        for pixel in range(NUM_PIXELS):
            r = int(sr + step_r * pixel)
            g = int(sg + step_g * pixel)
            b = int(sb + step_b * pixel)
            gradient.append((r, g, b))
        return gradient

    debug_print("WAVE STARTED (1/2)")
    gradients = []
    for i in range(len(colour_sequence) - 1):
        gradients.append(build_gradient(colour_sequence[i], colour_sequence[i + 1]))

    for grad in gradients:
        update_multiple_pixels(grad, delay)

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
    speed=0.33, colour=(255, 255, 255), intensity=0.33, cycles: int = 10.0
):
    """
    Create a random sparkling effect

    :param speed: float,   Time in seconds a set of sparkles last. default is 0.33
    :param colour: Tuple[int, int, int],     RGB colour. default is white (255,255,255)
    :param intensity: float,    Percentage of pixels to light up. default is 0.5
     (50% of amount of pixels at a max)
    :param cycles: int,    Number of sparkle cycles, default is 10.0
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

    turn_black(0.5)
    sparkle_pixels()
    turn_black(0.25)
    rainbow_cycle()
    turn_black(0.25)
    rainbow_wave()
    turn_black(0.25)
    rainbow_wave_improved()
    turn_black(0.25)

    debug_print("END OF WHILE LOOP (2/2)")
