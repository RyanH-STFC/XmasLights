"""
Script for raspberry pi pico to change neopixel lights on pin GP16
"""

# pylint: disable = import-error, no-member, no-else-return
import time
import board
import neopixel


strip = neopixel.NeoPixel(board.GP16, 30, brightness=0.05)
rgb = [255, 0, 0]
DEBUG_PRINT = True


def debug_print(msg: str, new_line: bool = True) -> None:
    """
    A function that prints messages to stdout. for debugging purposes.

    :param msg: The message to print
    :param new_line: Bool value, True to create a space underneath the message, default is True
    :return: None
    """
    if DEBUG_PRINT:
        if new_line:
            print(msg, "\n")
        else:
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

            debug_print("Red:{} Green:{} Blue:{}".format(*rgb), False)

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


while True:
    debug_print("BEGINNING OF MAIN WHILE LOOP")
    if not rainbow_cycle():
        break
