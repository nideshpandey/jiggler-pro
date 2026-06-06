import time
import sys
import argparse
import ctypes
import ctypes.util
import platform
import random
from datetime import datetime

# --- UI & Colors ---
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"

# --- Platform Detection ---
OS = platform.system()

# --- Cross-Platform Controller ---
class JigglerController:
    def __init__(self):
        self.lib = None
        self.setup_platform()

    def setup_platform(self):
        if OS == "Darwin":  # macOS
            self.setup_macos()
        elif OS == "Windows":
            self.setup_windows()
        elif OS == "Linux":
            self.setup_linux()
        else:
            print(f"{RED}Error: Unsupported OS: {OS}{RESET}")
            sys.exit(1)

    # --- macOS Implementation ---
    def setup_macos(self):
        # Robust library loading for newer macOS
        path = ctypes.util.find_library("CoreGraphics")
        if not path:
            path = "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
        
        try:
            self.lib = ctypes.cdll.LoadLibrary(path)
        except:
            self.lib = ctypes.cdll.LoadLibrary("CoreGraphics")

        class CGPoint(ctypes.Structure):
            _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]
        
        self.CGPoint = CGPoint
        
        # Explicit signatures to prevent 64-bit segmentation faults
        self.lib.CGEventCreate.restype = ctypes.c_void_p
        self.lib.CGEventCreate.argtypes = [ctypes.c_void_p]

        self.lib.CGEventGetLocation.restype = CGPoint
        self.lib.CGEventGetLocation.argtypes = [ctypes.c_void_p]

        self.lib.CGEventCreateMouseEvent.restype = ctypes.c_void_p
        self.lib.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, CGPoint, ctypes.c_int]

        self.lib.CGEventPost.restype = None
        self.lib.CGEventPost.argtypes = [ctypes.c_int, ctypes.c_void_p]

        self.lib.CFRelease.restype = None
        self.lib.CFRelease.argtypes = [ctypes.c_void_p]

        self.lib.CGEventSourceKeyState.restype = ctypes.c_bool
        self.lib.CGEventSourceKeyState.argtypes = [ctypes.c_int, ctypes.c_uint16]
        
        self.VK_SPACE = 0x31
        self.VK_ENTER = 0x24

    def get_mouse_pos_macos(self):
        event = self.lib.CGEventCreate(None)
        if not event: return 0, 0
        point = self.lib.CGEventGetLocation(event)
        self.lib.CFRelease(event)
        return point.x, point.y

    def move_mouse_macos(self, x, y):
        ev = self.lib.CGEventCreateMouseEvent(None, 5, self.CGPoint(x, y), 0)
        if ev:
            self.lib.CGEventPost(0, ev)
            self.lib.CFRelease(ev)

    def click_macos(self, x, y):
        p = self.CGPoint(x, y)
        down = self.lib.CGEventCreateMouseEvent(None, 1, p, 0)
        up = self.lib.CGEventCreateMouseEvent(None, 2, p, 0)
        if down and up:
            self.lib.CGEventPost(0, down)
            self.lib.CGEventPost(0, up)
            self.lib.CFRelease(down)
            self.lib.CFRelease(up)

    # --- Windows Implementation ---
    def setup_windows(self):
        self.lib = ctypes.windll.user32
        self.VK_SPACE = 0x20
        self.VK_ENTER = 0x0D

    def get_mouse_pos_win(self):
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        self.lib.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def move_mouse_win(self, x, y):
        self.lib.SetCursorPos(int(x), int(y))

    def click_win(self, x, y):
        # MOUSEEVENTF_LEFTDOWN = 2, LEFTUP = 4
        self.lib.mouse_event(2, 0, 0, 0, 0)
        self.lib.mouse_event(4, 0, 0, 0, 0)

    # --- Linux Implementation (X11) ---
    def setup_linux(self):
        try:
            self.x11 = ctypes.cdll.LoadLibrary("libX11.so.6")
            self.xtst = ctypes.cdll.LoadLibrary("libXtst.so.6")
            self.display = self.x11.XOpenDisplay(None)
            if not self.display: raise Exception("No display")
        except:
            print(f"{RED}Error: Linux version requires X11 (libX11 and libXtst).{RESET}")
            sys.exit(1)
        self.VK_SPACE = 65 
        self.VK_ENTER = 36

    def get_mouse_pos_linux(self):
        root = self.x11.XDefaultRootWindow(self.display)
        child = ctypes.c_ulong()
        rx, ry, wx, wy = ctypes.c_int(), ctypes.c_int(), ctypes.c_int(), ctypes.c_int()
        mask = ctypes.c_uint()
        self.x11.XQueryPointer(self.display, root, ctypes.byref(ctypes.c_ulong()), 
                               ctypes.byref(child), ctypes.byref(rx), ctypes.byref(ry), 
                               ctypes.byref(wx), ctypes.byref(wy), ctypes.byref(mask))
        return rx.value, ry.value

    def move_mouse_linux(self, x, y):
        self.xtst.XTestFakeMotionEvent(self.display, -1, int(x), int(y), 0)
        self.x11.XFlush(self.display)

    def click_linux(self, x, y):
        self.xtst.XTestFakeButtonEvent(self.display, 1, True, 0)
        self.xtst.XTestFakeButtonEvent(self.display, 1, False, 0)
        self.x11.XFlush(self.display)

    # --- Wrapper Methods ---
    def get_pos(self):
        if OS == "Darwin": return self.get_mouse_pos_macos()
        if OS == "Windows": return self.get_mouse_pos_win()
        return self.get_mouse_pos_linux()

    def move(self, x, y):
        if OS == "Darwin": self.move_mouse_macos(x, y)
        elif OS == "Windows": self.move_mouse_win(x, y)
        else: self.move_mouse_linux(x, y)

    def click(self, x, y):
        if OS == "Darwin": self.click_macos(x, y)
        elif OS == "Windows": self.click_win(x, y)
        else: self.click_linux(x, y)

    def is_key_pressed(self):
        if OS == "Darwin":
            return self.lib.CGEventSourceKeyState(0, self.VK_SPACE) or \
                   self.lib.CGEventSourceKeyState(0, self.VK_ENTER)
        if OS == "Windows":
            return (ctypes.windll.user32.GetAsyncKeyState(self.VK_SPACE) & 0x8000) or \
                   (ctypes.windll.user32.GetAsyncKeyState(self.VK_ENTER) & 0x8000)
        if OS == "Linux":
            keys = (ctypes.c_char * 32)()
            self.x11.XQueryKeymap(self.display, keys)
            space_byte = ord(keys[self.VK_SPACE >> 3])
            enter_byte = ord(keys[self.VK_ENTER >> 3])
            return (space_byte & (1 << (self.VK_SPACE & 7))) or \
                   (enter_byte & (1 << (self.VK_ENTER & 7)))
        return False

# --- Main Logic ---
def run_jiggler(interval, pixels, stealth=False, click=True):
    ctrl = JigglerController()
    start_time = datetime.now()
    jiggle_count = 0
    
    print(f"{GREEN}{BOLD}--- Jiggler Pro Activated ---{RESET}")
    print(f"{CYAN}OS:{RESET} {OS}")
    print(f"{CYAN}Interval:{RESET} {interval}s {'(Randomized)' if stealth else ''}")
    print(f"{CYAN}Distance:{RESET} {pixels}px {'(Randomized)' if stealth else ''}")
    print(f"{CYAN}Clicks:{RESET} {'Enabled' if click else 'Disabled'}")
    print(f"{YELLOW}STOP:{RESET} Press {BOLD}[SPACE]{RESET} or {BOLD}[ENTER]{RESET} anywhere.\n")
    
    try:
        while True:
            # 1. Randomized Action
            current_interval = random.randint(max(1, interval-5), interval+5) if stealth else interval
            current_pixels = random.randint(1, pixels) if stealth else pixels
            
            x, y = ctrl.get_pos()
            
            # Pattern Choice
            pattern = random.choice(["L", "Wiggle", "Box"]) if stealth else "L"
            
            if pattern == "L":
                ctrl.move(x + current_pixels, y)
                time.sleep(0.1)
                ctrl.move(x + current_pixels, y - current_pixels)
                time.sleep(0.1)
                ctrl.move(x, y)
            elif pattern == "Wiggle":
                for _ in range(3):
                    ctrl.move(x + 2, y + 2)
                    time.sleep(0.05)
                    ctrl.move(x - 2, y - 2)
                    time.sleep(0.05)
                ctrl.move(x, y)
            elif pattern == "Box":
                ctrl.move(x + current_pixels, y)
                time.sleep(0.05)
                ctrl.move(x + current_pixels, y + current_pixels)
                time.sleep(0.05)
                ctrl.move(x, y + current_pixels)
                time.sleep(0.05)
                ctrl.move(x, y)

            if click:
                ctrl.click(x, y)
            
            jiggle_count += 1
            
            # 2. Countdown
            for i in range(current_interval, 0, -1):
                for _ in range(10): # Poll 10x per second
                    if ctrl.is_key_pressed():
                        raise KeyboardInterrupt
                    time.sleep(0.1)
                
                color = GREEN if i > 5 else RED
                mode_str = f"[{pattern}]" if stealth else ""
                sys.stdout.write(f"\r{color}Next jiggle in {i:2d}s...{RESET} {CYAN}{mode_str}{RESET} [Total: {jiggle_count}]")
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n\n{YELLOW}{BOLD}--- Session Summary ---{RESET}")
        print(f"{CYAN}Total Uptime: {RESET} {duration.seconds // 3600}h {(duration.seconds // 60) % 60}m {duration.seconds % 60}s")
        print(f"{CYAN}Total Jiggles:{RESET} {jiggle_count}")
        print(f"{GREEN}Stay awake!{RESET}")
    finally:
        print(f"\n{CYAN}Jiggler deactivated.{RESET}")

def run_from_cli():
    parser = argparse.ArgumentParser(description="Jiggler Pro: Professional Cross-Platform Mouse Jiggler.")
    parser.add_argument("seconds", type=int, nargs="?", default=30, help="Interval in seconds")
    parser.add_argument("-p", "--pixels", type=int, default=7, help="Movement distance")
    parser.add_argument("-s", "--stealth", action="store_true", help="Enable randomized human-like movement")
    parser.add_argument("--no-click", action="store_false", dest="click", help="Disable mouse clicking")
    
    args = parser.parse_args()
    run_jiggler(args.seconds, args.pixels, args.stealth, args.click)

if __name__ == "__main__":
    run_from_cli()
