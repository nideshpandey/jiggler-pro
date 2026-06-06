# Jiggler Pro

A professional, zero-dependency mouse jiggler that keeps your computer awake by simulating human-like activity.

## Why Jiggler Pro

Jiggler Pro is designed for users who need a reliable, lightweight, and undetectable way to keep their systems active. Unlike other tools that require heavy dependencies or move the mouse in obvious, repetitive patterns, Jiggler Pro offers:

- **Indistinguishable Activity:** Stealth Mode uses randomized movement and timing to mimic a real user, making it much harder for monitoring software to flag.
- **Zero Installation Footprint:** It uses native system APIs (ctypes) rather than installing large libraries like `pyautogui`, keeping your environment clean.
- **System Integrity:** It always returns your cursor to its original position, ensuring it doesn't interfere with your work when you return to your desk.
- **Universal Compatibility:** A single codebase that runs natively on macOS, Windows, and Linux.

---

## Quick Start

### 1. Installation
Install directly from the project folder:
```bash
pip install .
```

### 2. Basic Usage
Once installed, simply run:
```bash
jiggler-pro
```
*By default, it jiggles every 30 seconds.*

---

## Examples

| Goal | Command |
| :--- | :--- |
| **Fast Jiggle** (every 5s) | `jiggler-pro 5` |
| **Low Frequency** (every 2m) | `jiggler-pro 120` |
| **Human-like Stealth** | `jiggler-pro --stealth` |
| **Movement Only** (no clicks) | `jiggler-pro --no-click` |
| **Subtle Nudge** (1 pixel) | `jiggler-pro -p 1` |
| **Long Distance** (50 pixels) | `jiggler-pro -p 50` |
| **Balanced Stealth** | `jiggler-pro 10 -s --no-click` |
| **Invisible Mode** | `jiggler-pro 15 -s --no-click` |

---

## Arguments and Options

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `seconds` | Positional | `30` | The interval between jiggles in seconds. |
| `-p`, `--pixels` | Integer | `7` | The distance in pixels the mouse will move. |
| `-s`, `--stealth` | Flag | `False` | Enables randomized timing, distances, and movement patterns. |
| `--no-click` | Flag | `True` | Disables the automatic mouse click that follows a movement. |

---

## Interactive Controls

| Key | Action |
| :--- | :--- |
| **SPACE** / **ENTER** | **Stop** and exit safely. |
| **Ctrl + C** | Force quit. |

---

## Features
- **Zero Dependencies:** No extra libraries needed—runs on pure Python.
- **Stealth Mode:** Randomizes movement patterns and timing to stay undetected.
- **Cross-Platform:** Works natively on macOS, Windows, and Linux.
- **Safe:** Always returns the mouse to the exact spot it started.

## License
MIT
