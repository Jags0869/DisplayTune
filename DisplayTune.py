import ctypes
import os
import tkinter as tk
from ctypes import wintypes

import customtkinter as ctk


class GammaRamp(ctypes.Structure):
    _fields_ = [
        ("red", ctypes.c_ushort * 256),
        ("green", ctypes.c_ushort * 256),
        ("blue", ctypes.c_ushort * 256),
    ]


if os.name == "nt":
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    gdi32.CreateDCW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPVOID]
    gdi32.CreateDCW.restype = wintypes.HDC
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteDC.restype = wintypes.BOOL
    gdi32.SetDeviceGammaRamp.argtypes = [wintypes.HDC, ctypes.POINTER(GammaRamp)]
    gdi32.SetDeviceGammaRamp.restype = wintypes.BOOL


def clamp(value, low, high):
    return max(low, min(high, value))


def build_ramp(brightness=0, contrast=1, gamma=1, warmth=0, tint=0):
    ramp = GammaRamp()
    brightness = clamp(float(brightness), -100, 100) / 100
    contrast = clamp(float(contrast), 0.2, 2.5)
    gamma = clamp(float(gamma), 0.4, 3.2)
    warmth = clamp(float(warmth), -100, 100) / 100
    tint = clamp(float(tint), -100, 100) / 100

    for i in range(256):
        value = pow(i / 255.0, 1.0 / gamma)
        value = clamp((value - 0.5) * contrast + 0.5 + brightness * 0.25, 0, 1)
        red = clamp(value + warmth * 0.22, 0, 1)
        green = clamp(value + tint * 0.18 - warmth * 0.08, 0, 1)
        blue = clamp(value - warmth * 0.22 - tint * 0.04, 0, 1)
        ramp.red[i] = round(red * 65535)
        ramp.green[i] = round(green * 65535)
        ramp.blue[i] = round(blue * 65535)
    return ramp


def apply_ramp(profile):
    if os.name != "nt":
        raise RuntimeError("DisplayTune runs on Windows only.")
    dc = gdi32.CreateDCW("DISPLAY", None, None, None)
    if not dc:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        ramp = build_ramp(**profile)
        if not gdi32.SetDeviceGammaRamp(dc, ctypes.byref(ramp)):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        gdi32.DeleteDC(dc)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DisplayTune(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DisplayTune")
        self.geometry("760x650")
        self.minsize(620, 560)
        self.configure(fg_color="#0f1117")
        self.profile = {"brightness": 0, "contrast": 1, "gamma": 1, "warmth": 0, "tint": 0}
        self.controls = {}
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(self, fg_color="#121925", corner_radius=18)
        header.grid(row=0, column=0, padx=18, pady=18, sticky="ew")
        ctk.CTkLabel(header, text="DisplayTune", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=20, pady=(18, 3))
        ctk.CTkLabel(header, text="Simple display controls for Windows", text_color="#9aa7bf").pack(anchor="w", padx=20, pady=(0, 18))

        body = ctk.CTkFrame(self, fg_color="#121925", corner_radius=18)
        body.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        body.grid_columnconfigure((0, 1), weight=1)
        left = ctk.CTkFrame(body, fg_color="#171d2e", corner_radius=14)
        left.grid(row=0, column=0, padx=(18, 9), pady=18, sticky="nsew")
        right = ctk.CTkFrame(body, fg_color="#171d2e", corner_radius=14)
        right.grid(row=0, column=1, padx=(9, 18), pady=18, sticky="nsew")

        specs = [
            ("Brightness", "brightness", -100, 100, 0, 1, "%.0f"),
            ("Contrast", "contrast", .2, 2.5, 1, .05, "%.2f"),
            ("Gamma", "gamma", .4, 3.2, 1, .05, "%.2f"),
            ("Warmth", "warmth", -100, 100, 0, 1, "%.0f"),
            ("Tint", "tint", -100, 100, 0, 1, "%.0f"),
        ]
        for row, spec in enumerate(specs):
            self._add_control(left, row, *spec)

        ctk.CTkLabel(right, text="Quick Presets", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=18, pady=(18, 10))
        presets = {
            "Neutral": {"brightness": 0, "contrast": 1, "gamma": 1, "warmth": 0, "tint": 0},
            "Night": {"brightness": -14, "contrast": 1.15, "gamma": 1.45, "warmth": 35, "tint": -8},
            "Warm": {"brightness": 0, "contrast": 1.1, "gamma": 1.1, "warmth": 45, "tint": 0},
            "Cool": {"brightness": -5, "contrast": 1.05, "gamma": 1, "warmth": -25, "tint": 15},
        }
        for name, values in presets.items():
            ctk.CTkButton(right, text=name, command=lambda p=values: self.set_profile(p), fg_color="#2a3148", hover_color="#3d7afe").pack(fill="x", padx=18, pady=5)
        ctk.CTkLabel(right, text="Actions", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=18, pady=(25, 10))
        ctk.CTkButton(right, text="Apply", command=self.apply, height=40).pack(fill="x", padx=18, pady=5)
        ctk.CTkButton(right, text="Reset", command=lambda: self.set_profile(presets["Neutral"]), fg_color="#364154", hover_color="#4c5a73").pack(fill="x", padx=18, pady=5)
        ctk.CTkButton(right, text="Close", command=self.destroy, fg_color="#a83e4d", hover_color="#c54b5b").pack(fill="x", padx=18, pady=5)
        self.status = ctk.CTkLabel(self, text="Ready", text_color="#9aa7bf")
        self.status.grid(row=2, column=0, pady=(0, 12))

    def _add_control(self, parent, row, label, key, low, high, default, step, fmt):
        box = ctk.CTkFrame(parent, fg_color="#1c2233", corner_radius=10)
        box.grid(row=row, column=0, padx=14, pady=6, sticky="ew")
        box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(box, text=label, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=12, pady=(9, 2), sticky="w")
        entry = ctk.CTkEntry(box, width=65, justify="center", fg_color="#232b3e", border_width=0)
        entry.grid(row=0, column=1, padx=12, pady=(9, 2))
        slider = ctk.CTkSlider(box, from_=low, to=high, number_of_steps=round((high-low)/step), command=lambda value, k=key: self._slider(k, value))
        slider.set(default)
        slider.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")
        entry.insert(0, fmt % default)
        entry.bind("<Return>", lambda event, k=key: self._entry(k))
        entry.bind("<FocusOut>", lambda event, k=key: self._entry(k))
        self.controls[key] = {"slider": slider, "entry": entry, "low": low, "high": high, "fmt": fmt}

    def _slider(self, key, value):
        self.profile[key] = float(value)
        control = self.controls[key]
        control["entry"].delete(0, "end")
        control["entry"].insert(0, control["fmt"] % value)
        self.apply(False)

    def _entry(self, key):
        control = self.controls[key]
        try:
            value = float(control["entry"].get())
        except ValueError:
            value = self.profile[key]
        value = clamp(value, control["low"], control["high"])
        control["slider"].set(value)
        self._slider(key, value)

    def set_profile(self, profile):
        for key, value in profile.items():
            self.controls[key]["slider"].set(value)
            self._slider(key, value)
        self.apply()

    def apply(self, notify=True):
        try:
            apply_ramp(self.profile)
            self.status.configure(text="Applied")
        except Exception as error:
            self.status.configure(text=str(error)[:90])
        if not notify:
            self.status.configure(text="Preview")


if __name__ == "__main__":
    DisplayTune().mainloop()
