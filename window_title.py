import platform
import subprocess
import time

PYGETWINDOW_AVAILABLE = False
XLIB_AVAILABLE = False

if platform.system() == "Windows":
    try:
        import pygetwindow as gw
        PYGETWINDOW_AVAILABLE = True
    except ImportError:
        print("pygetwindow is not available.")
    import win32gui

elif platform.system() == "Linux":
    try:
        from Xlib import X, display, Xatom, error
        import Xlib.protocol.event
        XLIB_AVAILABLE = True
    except ImportError:
        print("Xlib is not available.")


def get_active_window():
    system = platform.system()
    if system == "Windows":
        if PYGETWINDOW_AVAILABLE:
            return gw.getActiveWindow()
        else:
            print("pygetwindow is not available. Unable to get active window.")
            return None
    elif system == "Linux":
        if XLIB_AVAILABLE:
            d = display.Display()
            root = d.screen().root
            active_window = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
            if active_window:
                window = d.create_resource_object('window', active_window.value[0])
                return d, window
        return None
    else:
        print(f"Unsupported platform: {system}")
        return None


def set_window_name(display_window, new_name):
    system = platform.system()
    if system == "Windows":
        if PYGETWINDOW_AVAILABLE:
            try:
                hwnd = display_window._hWnd  # Get the window handle
                original_title = win32gui.GetWindowText(hwnd)
                print(f"Original window title: {original_title}")
                win32gui.SetWindowText(hwnd, new_name)
                time.sleep(1)  # Wait a bit to ensure the change takes effect
                updated_title = win32gui.GetWindowText(hwnd)
                print(f"Updated window title: {updated_title}")
                if updated_title == new_name:
                    print("Window title successfully updated.")
                else:
                    print("Window title did not update as expected.")
            except AttributeError:
                print("Error: Unable to set window title. The window object doesn't have a '_hWnd' attribute.")
            except Exception as e:
                print(f"Error setting window title: {str(e)}")
        else:
            print("pygetwindow is not available. Unable to set window name.")
    elif system == "Linux":
        print(f"display_window type: {type(display_window)}")
        print(f"display_window content: {display_window}")

        if isinstance(display_window, str):
            print("Warning: display_window is a string, which is not the expected format.")
            print("Attempting to set window name using xdotool...")
            try:
                # Use xdotool to set the window name
                subprocess.run(['xdotool', 'getactivewindow', 'set_window', '--name', new_name], check=True)
                print(f"Attempted to set window name to: {new_name}")
            except subprocess.CalledProcessError as e:
                print(f"Error using xdotool: {e}")
            except FileNotFoundError:
                print("xdotool is not installed. Please install it using 'sudo apt-get install xdotool'")
        elif XLIB_AVAILABLE:
            try:
                if isinstance(display_window, (list, tuple)) and len(display_window) == 2:
                    d, window = display_window
                elif hasattr(display_window, 'display') and hasattr(display_window, 'window'):
                    # Alternative structure where display_window is an object with display and window attributes
                    d, window = display_window.display, display_window.window
                else:
                    raise ValueError(f"Unsupported display_window structure: {display_window}")

                # Change the window property
                window.change_property(
                    d.intern_atom('_NET_WM_NAME'),
                    d.intern_atom('UTF8_STRING'),
                    8,
                    new_name.encode('utf-8')
                )
                d.flush()
                print(f"Attempted to set window name to: {new_name}")
            except Exception as e:
                print(f"Error setting window name: {str(e)}")
        else:
            print("Xlib is not available and display_window is not a string. Unable to set window name.")
    else:
        print(f"Unsupported platform: {system}")


def get_window_title(window):
    if window is None:
        return ""
    system = platform.system()
    if system == "Windows":
        return window.title
    elif system == "Linux":
        d, w = window
        return w.get_wm_name()
    return ""
