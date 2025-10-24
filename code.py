"""
bit of this and a bit of that
"""

# pylint: disable = import-error, no-member
import time
import board
import neopixel

strip = neopixel.NeoPixel(board.GP16, 30, brightness=0.02)

print("rgb-pico is running")

strip.fill((0, 0, 0))


import time


def smooth_color_cycle(strip: object, sleep_time=0.01):
    """
    Perform a smooth RGB color cycle with gradual transitions.

    :param strip: LED strip object with a fill method
    :param sleep_time: Time between color updates
    """

    def interpolate_colors(start_color, end_color, steps):
        """
        Generate a smooth color transition between two colors.

        :param start_color: Starting RGB values
        :param end_color: Ending RGB values
        :param steps: Number of steps in the transition
        :return: Generator of interpolated color values
        """
        for step in range(steps + 1):
            r = int(start_color[0] + (end_color[0] - start_color[0]) * step / steps)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * step / steps)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * step / steps)
            yield [r, g, b]

    # Define color transition sequence
    color_sequence = [
        [255, 0, 0],  # Red
        [255, 255, 0],  # Yellow
        [0, 255, 0],  # Green
        [0, 255, 255],  # Cyan
        [0, 0, 255],  # Blue
        [255, 0, 255],  # Magenta
    ]

    while True:
        # Cycle through colors with smooth transitions
        for i in range(len(color_sequence)):
            start_color = color_sequence[i]
            end_color = color_sequence[(i + 1) % len(color_sequence)]

            # Perform smooth transition between colors
            for rgb in interpolate_colors(start_color, end_color, 100):
                strip.fill(tuple(rgb))
                time.sleep(sleep_time)


smooth_color_cycle(strip)
