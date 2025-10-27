# pylint: disable = import-error, no-member
import time
import board
import neopixel


strip = neopixel.NeoPixel(board.GP16, 30, brightness=0.05)
rgb = [255, 0, 0]
DEBUG_PRINT = True


def debug_print(msg: str, *args, new_line: bool = True) -> None:
    """
    Print debug message with optional formatting and line control

    :param msg: Message template to format
    :param args: Arguments to format into the message
    :param new_line: Whether to add a new line (default True)
    """
    formatted_msg = msg.format(*args)
    if DEBUG_PRINT:
        end_char = "\n" if new_line else ""
        print(formatted_msg, end=end_char)


def rainbow_cycle(delay: float = 0.002) -> bool:

    def running_function(
        increment_index: int = None,
        decrement_index: int = None,
    ) -> None:

        for _ in range(255):
            if increment_index is not None:
                rgb[increment_index] += 1
            if decrement_index is not None:
                rgb[decrement_index] -= 1

            debug_print("Red:{} Green:{} Blue:{}".format(*rgb), False)

            strip.fill(tuple(rgb))
            time.sleep(delay)

    if all(0 <= element < 255 for element in rgb):
        debug_print("ONE OF THE RGB VALUES WENT OUT OF BOUNDS", True, rgb)
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
