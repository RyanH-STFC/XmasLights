"""
Script for raspberry pi pico to change neopixel lights on pin GP16
"""

# pylint: disable = import-error, no-member, no-else-return, too-many-locals
import random
import time
import asyncio
import board
import neopixel
import digitalio

PIXEL_PIN = board.GP16
PIXEL_BRIGHTNESS = 0.05
NUM_PIXELS = 30
strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=PIXEL_BRIGHTNESS)

BUTTON_PIN = board.GP14
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

pattern_frame_amounts = {}
DEBUG_PRINT = True


def debug_print(msg, new_line=True):
    """
    Prints messages to stdout. for debugging purposes.

    :param msg: str,  The message to print
    :param new_line: bool,  To create a space underneath the message default is True
    :return: None
    """
    if DEBUG_PRINT and new_line:
        print(msg.upper(), "\n")
    elif DEBUG_PRINT:
        print(msg.upper())


async def red():
    """
    Turns lights red
    :return: None
    """
    return strip.fill((250, 0, 0))


async def green():
    """
    Turns lights green
    :return: None
    """
    return strip.fill((0, 250, 0))


# pylint: disable = consider-iterating-dictionary
async def _update_pattern_frame_amount(key, cycles, returning=True):
    if key in pattern_frame_amounts.keys():
        if pattern_frame_amounts[key] != cycles:
            debug_print(f'creating a new key "{key}" with {cycles}')
            pattern_frame_amounts[key] = cycles
        else:
            debug_print(f'found existing key "{key}" with {cycles}')
    else:
        pattern_frame_amounts[key] = cycles
        debug_print(f"created new key {key} with {cycles}")

    print(pattern_frame_amounts)
    if not returning:
        return None
    return pattern_frame_amounts


async def update_multiple_pixels(updates, pace=0.0):
    """
    Takes a list and goes through it and changes the pixels colour at the index of this #
    with the value at that element.

    :param updates: list[tuple[int, int, int]],  The list of updated for the LED's
    :param pace: float,  the delay between each update default is 0 seconds
    :return: None or List[tuple[int, int, int]]
    """
    debug_print(f"List to be updated:    {updates}")
    for index, colour in enumerate(updates):
        strip[index] = colour

        await asyncio.sleep(pace)


def turn_black(delay=1.0):
    """
    Turns off all LED's, with debug print statement

    :param delay: float,  delay for after the pixels turn black, default is 1.0 seconds
    :return: None
    """
    debug_print("Turning pixels black")
    strip.fill((0, 0, 0))
    time.sleep(delay)


# pylint: disable = too-many-arguments, too-many-positional-arguments
def merge_patterns(
    pattern_a_funct,
    pattern_b_funct,
    mode="default",
    sway=0.5,
    delay=0.0,
    pace=0.0,
):
    """
    Creates a new list by merging two patterns most efficiently.

    :param pattern_a_funct: tuple[List[tuple[int, int, int]], int]
    :param pattern_b_funct: tuple[List[tuple[int, int, int]], int]
     changes the colour of the other lists pixels
    :param mode: the mode/mask that the two patterns will be merged against.
    :param sway: float, how much one pattern is effected by the other
     (1 makes pattern A more favoured by 100% and 0 makes pattern B more favoured by 100%)
    :param delay: float,  delay for how long between each iteration
    :param pace: float, how fast the lights update along the strip
    :return: List[tuple[int, int, int]]
    """

    debug_print(f"Pattern A {pattern_a_funct}, " f"Pattern B {pattern_b_funct}")

    def _default_funct(pattern_1, pattern_2):
        out = []
        for i in range(NUM_PIXELS - 1):
            value_1 = pattern_1[i]
            value_2 = pattern_2[i]
            if value_1 == (0, 0, 0):
                out.append(value_1)
            else:
                out.append(value_2)
        return out

    def _combine_funct(pattern_1, pattern_2, sway):
        out = []

        # Ensure sway is between 0 and 1
        sway = max(0.01, min(sway, 0.99))

        for i in range(NUM_PIXELS - 1):

            value_1 = tuple(int(num * sway) for num in pattern_1[i])
            value_2 = tuple(int(num * (1 - sway)) for num in pattern_2[i])

            # Combine the two values by adding them
            blended_color = tuple(value_1[j] + value_2[j] for j in range(3))

            out.append(blended_color)

        return out  # Make sure to return the blended pattern

    index = 0

    while True:
        # create and cache previous patterns

        pattern_a_frame = pattern_a_funct(
            delay=0,
            specific_frame=index % pattern_frame_amounts[pattern_a_funct.__name__],
            returning=True,
        )
        pattern_b_frame = pattern_b_funct(
            delay=0,
            specific_frame=index % pattern_frame_amounts[pattern_b_funct.__name__],
            returning=True,
        )

        if mode == "default":
            update_multiple_pixels(
                _default_funct(pattern_a_frame, pattern_b_frame), pace
            )
        if mode == "combine":
            update_multiple_pixels(
                _combine_funct(pattern_a_frame, pattern_b_frame, sway), pace
            )

        time.sleep(delay)
        index += 1

        if pattern_a_frame == pattern_a_funct(
            delay=0,
            specific_frame=pattern_frame_amounts[pattern_a_funct.__name__],
            returning=True,
        ) and pattern_b_frame == pattern_b_funct(
            delay=0,
            specific_frame=pattern_frame_amounts[pattern_b_funct.__name__],
            returning=True,
        ):
            break


async def rainbow_cycle(delay=0.002, returning=False, specific_frame=None):
    """
    Rainbow cycle with option to generate a specific frame.

    :param delay: float, delay for how long between each iteration
    :param returning: bool, to return the update sequence and not update lights
    :param specific_frame: int, generate only a specific frame number
    :return: None or Sequence[tuple[int, int, int]]
    """
    step = 8
    rgb_state = [255, 0, 0]

    async def running_function(increment_channel, decrement_channel):
        for _ in range(step):
            rgb_state[increment_channel] += 255 // step
            rgb_state[decrement_channel] -= 255 // step
            yield tuple(rgb_state)

    transitions = (
        await running_function(increment_channel=1, decrement_channel=0),
        await running_function(increment_channel=2, decrement_channel=1),
        await running_function(increment_channel=0, decrement_channel=2),
    )

    cycles = len(transitions) * step
    await _update_pattern_frame_amount("rainbow_cycle", cycles, returning)

    if specific_frame is not None:
        # Calculate which transition and which step within that transition
        frame = None
        total_step = step
        transition_index = specific_frame // total_step
        frame_in_transition = specific_frame % total_step

        # Reset initial state
        rgb_state = [255, 0, 0]

        # Advance to the correct transition
        for _ in range(transition_index):
            list(transitions[_ % len(transitions)])

        # Generate the specific frame in the current transition
        current_transition = transitions[transition_index % len(transitions)]
        for _ in range(frame_in_transition + 1):
            frame = next(current_transition)

        if returning:
            return [frame] * NUM_PIXELS

        await update_multiple_pixels([frame] * NUM_PIXELS)
        return None

    for transition in transitions:
        for rgb_tuple in transition:
            await update_multiple_pixels([rgb_tuple] * NUM_PIXELS)
            await asyncio.sleep(delay)
    return None


async def rainbow_wave(delay=0.03, returning=False, specific_frame=None):
    """
    Creates a wave of rainbow gradient colours.

    :param delay: float, speed at which the rainbow gradient moves down the strip
    :param returning: bool, Whether to return the list
    :param specific_frame: int, generate only a specific frame number
    :return: None or List[tuple] or tuple
    """
    debug_print("rainbow_wave BEGUN")

    colour_sequence = [
        (255, 0, 0),  # Red
        (255, 255, 0),  # Yellow
        (0, 255, 0),  # Green
        (0, 255, 255),  # Cyan
        (0, 0, 255),  # Blue
        (255, 0, 255),  # Magenta
    ]

    num_pixels_take_one = NUM_PIXELS - 1 if NUM_PIXELS > 1 else 1

    cycles = len(colour_sequence) - 1
    await _update_pattern_frame_amount("rainbow_wave", cycles, returning)

    async def build_gradient(start_colour, end_colour):
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

    if specific_frame is not None:
        # Calculate which gradient transition we're in
        total_gradients = len(colour_sequence) - 1
        gradient_index = specific_frame % total_gradients

        # Build the specific gradient
        current_gradient = build_gradient(
            colour_sequence[gradient_index], colour_sequence[gradient_index + 1]
        )

        # Rotate the gradient based on the specific frame
        rotation = specific_frame // total_gradients
        return current_gradient[rotation:] + current_gradient[:rotation]

    # Original implementation remains the same
    if not returning:
        debug_print("WAVE STARTED (1/2)")
        for i in range(len(colour_sequence) - 1):
            await update_multiple_pixels(
                await build_gradient(colour_sequence[i], colour_sequence[i + 1]), delay
            )
        debug_print("WAVE FINISHED (2/2)")
    return None


async def rainbow_wave_improved(
    delay=0.0, returning=False, num_iterations=NUM_PIXELS, specific_frame=None
):
    """
    Create a fixed rainbow gradient that moves across the LED strip.

    :param delay: float,   The speed of the wave movement, default is 0.0
    :param num_iterations: int,  Number of times to shift the gradient, default is number of pixels
    :param returning: bool,    Whether to return the list
    :param specific_frame: int, generate only a specific frame number
    :return: None
    """

    cycles = num_iterations
    await _update_pattern_frame_amount("rainbow_wave_improved", cycles, returning)

    async def generate_fixed_rainbow_gradient():
        """
        Generate a complete rainbow gradient across the entire strip.

        :return: List of pixel colors
        """
        update_list = []
        for led in range(NUM_PIXELS):
            # Normalize pixel position to create a smooth rainbow gradient
            hue = led / NUM_PIXELS
            r, g, b = await hsv_to_rgb(hue, 1.0, 1.0)
            update_list.append((int(r * 255), int(g * 255), int(b * 255)))

        return update_list

    async def hsv_to_rgb(hue: float, saturation: float, value: float) -> tuple:
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

    # Generate the initial rainbow gradient
    rainbow_gradient = await generate_fixed_rainbow_gradient()

    # If specific frame is requested
    if specific_frame is not None:
        # Rotate the gradient based on the specific frame
        rotation = specific_frame % NUM_PIXELS
        return rainbow_gradient[rotation:] + rainbow_gradient[:rotation]

    if not returning:
        for _ in range(num_iterations):
            await update_multiple_pixels(rainbow_gradient)
            rainbow_gradient = rainbow_gradient[1:] + rainbow_gradient[:1]
            await asyncio.sleep(delay)

    return None


# pylint: disable = too-many-arguments, too-many-positional-arguments
async def sparkle_pixels(
    speed=0.33,
    colour=(255, 255, 255),
    intensity=0.33,
    cycles: int = 4,
    returning=False,
    specific_frame=None,
):
    """
    Create a random sparkling effect

    :param speed: float,   Time in seconds a set of sparkles last. default is 0.33
    :param colour: Tuple[int, int, int],     RGB colour. default is white (255,255,255)
    :param intensity: float,    Percentage of pixels to light up. default is 0.5
     (50% of amount of pixels at a max)
    :param cycles: int,    Number of sparkle cycles, default is 3.0
    :param returning: bool,    Whether to return the list of cycles
    :param specific_frame: int, generate only a specific frame number
    :return: None or Sequence[tuple[int, int, int]]
    """

    await _update_pattern_frame_amount(
        "sparkle_pixels", (cycles * 3) / cycles, returning
    )

    # If specific_frame is not None or returning is True, generate the pixel list without updating
    # Create a pixel list for this cycle
    pixel_list = [(0, 0, 0) for _ in range(NUM_PIXELS)]
    for _ in range(
        random.randint(
            round((NUM_PIXELS * intensity) / 2), round(NUM_PIXELS * intensity)
        )
    ):
        random_pixel = random.randint(0, NUM_PIXELS - 1)
        pixel_list[random_pixel] = colour

    if specific_frame is not None or returning:
        return pixel_list

    await update_multiple_pixels(pixel_list)
    await asyncio.sleep(speed)
    return None


# All functions that work
# sparkle_pixels()
# rainbow_wave()
# rainbow_wave_improved()
# rainbow_cycle()

PATTERNS = [
    red,
    green,
    sparkle_pixels,
    rainbow_wave,
    rainbow_wave_improved,
    rainbow_cycle,
]
CURRENT_PATTERN_INDEX = 0


async def pattern_runner(pattern_func):
    """
    Runs pattern_func until button pressed
    :param pattern_func: function to run
    :return:
    """
    while True:
        await pattern_func()

        if not button.value:
            break


async def main():
    """
    Main running function
    :return: None
    """
    # pylint: disable = global-statement
    global CURRENT_PATTERN_INDEX

    while True:
        debug_print("BEGINNING OF WHILE LOOP (1/2)")
        current_pattern = PATTERNS[CURRENT_PATTERN_INDEX]

        debug_print(f"Switched to pattern: {current_pattern.__name__}")

        await pattern_runner(current_pattern)
        await asyncio.sleep(0.2)
        CURRENT_PATTERN_INDEX = (CURRENT_PATTERN_INDEX + 1) % (len(PATTERNS) - 1)

        debug_print("END OF WHILE LOOP (2/2)")


asyncio.run(main())
