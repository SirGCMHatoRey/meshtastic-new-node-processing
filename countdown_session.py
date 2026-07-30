import threading
import time

from pynput import keyboard
from colorama import Fore, Style

from window_title import get_active_window, get_window_title


def _get_color_code(value, max_value):
    colors = [Fore.RED, Fore.YELLOW, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    index = min(int(value / max_value * (len(colors) - 1)), len(colors) - 1)
    return colors[index]


def _dispatch_key(key, window_title, key_actions):
    """Decide what a keypress should do. Returns True if the session should stop.

    Only reacts when the terminal window is titled 'K3ANO'. 'q' always stops
    the session and is not part of `key_actions`; any other char present in
    `key_actions` invokes its callback.
    """
    if not (hasattr(key, 'char') and key.char is not None):
        return False
    if 'K3ANO' not in window_title:
        return False

    char = key.char.lower()
    if char == 'q':
        return True
    if char in key_actions:
        key_actions[char]()
    return False


def _countdown_display(duration, stop_event):
    start_time = time.time()
    max_remaining = duration
    while not stop_event.is_set() and time.time() - start_time < duration:
        remaining = int(duration - (time.time() - start_time))

        print(f"\r{' ' * 80}", end='', flush=True)  # Clear the line
        color = _get_color_code(remaining, max_remaining)

        print(f"\r{Fore.YELLOW}{Style.BRIGHT}Press {Fore.GREEN}'L'{Fore.YELLOW} for TRACE log, {Fore.GREEN}'N'{Fore.YELLOW} for NODES, or {Fore.GREEN}'Q'{Fore.YELLOW} to quit.{Style.RESET_ALL} Continue in {color}{remaining:3d}{Style.RESET_ALL} seconds", end='', flush=True)

        time.sleep(0.1)


def run_countdown(duration, key_actions):
    """Wait up to `duration` seconds, showing a countdown, while watching for
    keypresses (only when the terminal window is titled 'K3ANO'). Keys present
    in `key_actions` invoke their callback; 'q' stops the session immediately.
    Returns when the duration elapses or 'q' is pressed.
    """
    stop_event = threading.Event()

    def on_press(key):
        try:
            window_title = get_window_title(get_active_window())
            if _dispatch_key(key, window_title, key_actions):
                stop_event.set()
                return False  # Stop listener
        except Exception as e:
            print(f"Error handling key press: {e}")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    display_thread = threading.Thread(target=_countdown_display, args=(duration, stop_event), daemon=True)
    display_thread.start()

    stop_event.wait(duration)
    stop_event.set()
    display_thread.join()
    listener.stop()
