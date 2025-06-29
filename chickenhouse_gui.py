import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import light_detection
from light_detection import DEFAULT_IMAGE_PATH
import datetime
import cv2

class ChickenHouseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chicken House Door Control")
        self.status_var = tk.StringVar()
        self.status_var.set("Unknown")
        self.time_var = tk.StringVar()
        self.create_widgets()
        self.update_clock()
        # --- Live camera feed additions ---
        self.cap = cv2.VideoCapture(1)  # Try external camera first
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)  # Fallback to laptop camera
        self.current_frame = None
        self.last_detection_time = 0
        self.detection_delay = 10  # seconds
        self.update_video_frame()

    def create_widgets(self):
        status_frame = ttk.LabelFrame(self.root, text="Door Status")
        status_frame.pack(padx=10, pady=10, fill="x")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 16))
        self.status_label.pack(pady=5)
        self.clock_label = ttk.Label(status_frame, textvariable=self.time_var, font=("Arial", 12))
        self.clock_label.pack(pady=2)
        door_vis_frame = ttk.LabelFrame(self.root, text="Door Visualization")
        door_vis_frame.pack(padx=10, pady=5, fill="x")
        self.door_canvas = tk.Canvas(door_vis_frame, width=80, height=120, bg='lightgrey')
        self.door_canvas.pack(pady=5)
        self.door_rect = self.door_canvas.create_rectangle(20, 20, 60, 100, fill="brown")
        self.update_door_visual()
        # --- Video frame for live feed ---
        self.video_label = tk.Label(self.root)
        self.video_label.pack(pady=5)
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(padx=10, pady=5, fill="x")
        open_btn = ttk.Button(btn_frame, text="Open Door", command=self.open_door)
        open_btn.pack(side="left", expand=True, fill="x", padx=5)
        close_btn = ttk.Button(btn_frame, text="Close Door", command=self.close_door)
        close_btn.pack(side="left", expand=True, fill="x", padx=5)
        refresh_btn = ttk.Button(btn_frame, text="Refresh Status", command=self.manual_detection)
        refresh_btn.pack(side="left", expand=True, fill="x", padx=5)
        plot_frame = ttk.LabelFrame(self.root, text="Light Detection Visualization")
        plot_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.plot_frame = plot_frame
        self.show_plot()

    def update_clock(self):
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        self.time_var.set(now.strftime('%Y-%m-%d %H:%M:%S %Z'))
        self.root.after(1000, self.update_clock)

    def update_video_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Resize frame to 320x240 for a smaller live feed window
            resized_frame = cv2.resize(frame, (320, 240))
            self.current_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(self.current_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
            now = time.time()
            if now - self.last_detection_time > self.detection_delay:
                self.run_detection_on_frame()
                self.last_detection_time = now
        self.root.after(30, self.update_video_frame)  # ~30 FPS

    def update_status_from_image(self):
        # Analyze image and update door status
        try:
            prediction, confidence, metrics = light_detection.detect_time_of_day(DEFAULT_IMAGE_PATH)
            if prediction and ("morning" in prediction.lower()):
                light_detection.open_door()
                self.status_var.set("Open")
            elif prediction and ("night" in prediction.lower()):
                light_detection.close_door()
                self.status_var.set("Closed")
            else:
                self.status_var.set("Unknown")
        except Exception:
            self.status_var.set("Unknown")
        self.update_door_visual()
        self.show_plot()

    def run_detection_on_frame(self):
        try:
            if self.current_frame is not None:
                prediction, confidence, metrics = light_detection.detect_time_of_day_from_frame(self.current_frame)
                if prediction and ("morning" in prediction.lower()):
                    light_detection.open_door()
                    self.status_var.set("Open")
                elif prediction and ("night" in prediction.lower()):
                    light_detection.close_door()
                    self.status_var.set("Closed")
                else:
                    self.status_var.set("Unknown")
                self.update_door_visual()
                self.show_plot(frame=self.current_frame)
        except Exception:
            self.status_var.set("Unknown")

    def open_door(self):
        try:
            light_detection.open_door()
            self.status_var.set("Open")
            self.update_door_visual()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def close_door(self):
        try:
            light_detection.close_door()
            self.status_var.set("Closed")
            self.update_door_visual()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def manual_detection(self):
        self.run_detection_on_frame()

    def update_door_visual(self):
        # Simple visualization: door open = rectangle up, closed = rectangle down
        status = self.status_var.get()
        if status == "Open":
            self.door_canvas.coords(self.door_rect, 20, 20, 60, 50)  # Door open (up)
            self.door_canvas.itemconfig(self.door_rect, fill="saddle brown")
        elif status == "Closed":
            self.door_canvas.coords(self.door_rect, 20, 70, 60, 100)  # Door closed (down)
            self.door_canvas.itemconfig(self.door_rect, fill="brown")
        else:
            self.door_canvas.coords(self.door_rect, 20, 40, 60, 80)
            self.door_canvas.itemconfig(self.door_rect, fill="gray")

    def show_plot(self, frame=None):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        if frame is not None:
            fig = light_detection.get_light_plot_from_frame(frame)
        else:
            fig = light_detection.get_light_plot(DEFAULT_IMAGE_PATH)
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def on_close(self):
        try:
            if self.cap.isOpened():
                self.cap.release()
            light_detection.cleanup_servo()
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChickenHouseGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
