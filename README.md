![holy_sight](https://github.com/user-attachments/assets/81e9d5cd-0008-4f13-a1c6-035cc81504be)

# HolySight
HolySight is a lightweight crosshair overlay made with PySide6.

## Features
- Adjust crosshair size, opacity, color, and border
- Load custom images (PNG, JPG etc.)
- Move crosshair with drag mode
- Minimalist app design

## Installation  
- A pre-built `.exe` is available for Windows — no Python or setup needed.  
- 👉 [Download the latest release here](../../releases) and run `HolySight.exe`.  
- Compiled with [Nuitka](https://github.com/Nuitka/Nuitka) for performance and minimal memory usage.


## Usage
![holy_sight_tray](https://github.com/user-attachments/assets/dd3e5857-3ea3-44b8-864e-b96772fcd642)

HolySight doesn't use a traditional window — everything is configured directly from the system tray menu.
When you launch the app, a new icon will appear in your system tray (bottom-right of your screen).

- Right-click the system tray icon to open the menu.
- Use sliders to adjust size, opacity, and border thickness.
- Click the buttons to change:
  - Crosshair color
  - Border color
  - Enable/disable move mode
- Select **"Set image"** to load a custom PNG/JPG.
- Click **"Reset"** to restore the default red dot.
- Use **"Hide"/"Show"** to toggle visibility.
- Choose **"Exit"** to close the app.

To disable or exit Move Mode, press **Enter**, **Escape**, or click the button again (tooltip changes to **"Exit move mode"**).
While in Move Mode, you can also **double-click the crosshair** to instantly center it on the screen.

https://github.com/user-attachments/assets/21e75356-5e9b-4338-8a57-b96606413cde

## Contributing
Fork, make changes, and submit a pull request. Use type hints and follow PEP 8 🔥

## License
MIT License. See [LICENSE](LICENSE).
