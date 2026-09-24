# DisplayTune

A small, modern Windows display-tuning utility. Download the executable from the **Releases** page and open it—Python is not required for the released `.exe`.

## Features

- Brightness, contrast, gamma, warmth, and tint controls
- Live preview while moving sliders
- Exact numeric entry fields
- Neutral, Night, Warm, and Cool presets
- Single-file Python implementation
- Uses the Windows GDI `SetDeviceGammaRamp` API rather than a screen overlay

## Download

Go to [Releases](../../releases) and download `DisplayTune.exe` from the newest release.

Windows Defender or SmartScreen may show a warning because the executable is an unsigned personal utility. Only download it from this repository, and inspect the source if desired.

## Run from source

Windows 10/11 and Python 3.10+ are recommended.

```powershell
py -m pip install -r requirements.txt
py DisplayTune.py
```

## Build the standalone executable

On Windows, run `build.bat`. The output will be `dist\DisplayTune.exe`.

Alternatively:

```powershell
py -m pip install -r requirements.txt
py -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name DisplayTune DisplayTune.py
```

## Notes and limitations

- This version targets the primary display through GDI. It does not yet include monitor selection or DDC/CI saturation control.
- Windows Night Light and HDR can prevent or limit gamma-ramp changes.
- Some graphics drivers reject aggressive ramps or restore them after display-mode changes.
- Changes are not persisted between launches yet. Use the Neutral preset to restore the default ramp.
- The project must be built on Windows to produce a Windows executable.

## License

MIT. See [LICENSE](LICENSE).
