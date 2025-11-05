import argparse
import base64
import os
from typing import List, Optional

import cv2
import tkinter as tk
from tkinter import filedialog, messagebox


def load_yolo(model_path: Optional[str]):
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception:
        return None

    if model_path and os.path.exists(model_path):
        try:
            return YOLO(model_path)
        except Exception:
            return None

    # Try some small public models as a convenience (may not include an ambulance class)
    for ckpt in ["yolo11n.pt", "yolov10n.pt", "yolov8n.pt"]:
        try:
            return YOLO(ckpt)
        except Exception:
            continue
    return None


def cv_to_photoimage(frame) -> tk.PhotoImage:
    ok, buf = cv2.imencode('.png', frame)
    if not ok:
        raise RuntimeError("Failed to encode image for Tk")
    data_b64 = base64.b64encode(buf.tobytes())
    return tk.PhotoImage(data=data_b64)


class TrafficPanel:
    def __init__(self, parent: tk.Widget) -> None:
        self.frame = tk.Frame(parent, borderwidth=1, relief=tk.GROOVE)
        self.frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        title = tk.Label(self.frame, text="Signal State", font=("Segoe UI", 12, "bold"))
        title.pack(pady=(10, 6))

        self.red = tk.Canvas(self.frame, width=50, height=50, bg="#300", highlightthickness=0)
        self.red.pack(pady=6)
        self.red.create_oval(6, 6, 44, 44, fill="#f00", outline="")

        self.green = tk.Canvas(self.frame, width=50, height=50, bg="#030", highlightthickness=0)
        self.green.pack(pady=6)
        self.green.create_oval(6, 6, 44, 44, fill="#070", outline="")

        self.state_lbl = tk.Label(self.frame, text="RED", font=("Segoe UI", 11))
        self.state_lbl.pack(pady=(6, 10))

    def set_green(self) -> None:
        self.green.itemconfig(1, fill="#0f0")
        self.red.itemconfig(1, fill="#700")
        self.state_lbl.config(text="GREEN")

    def set_red(self) -> None:
        self.green.itemconfig(1, fill="#070")
        self.red.itemconfig(1, fill="#f00")
        self.state_lbl.config(text="RED")


class IntegratedApp:
    def __init__(self, root: tk.Tk, model_path: Optional[str], target_classes: List[str], conf_threshold: float = 0.75) -> None:
        self.root = root
        self.root.title("Integrated Detection + Traffic Signal Demo")
        self.model = load_yolo(model_path)
        self.target_classes = [c.strip().lower() for c in target_classes if c.strip()]
        self.conf_threshold = conf_threshold
        # Cap preview size so the signal panel stays visible
        self.max_preview_w = 640
        self.max_preview_h = 480
        self.current_img_bgr = None
        self.current_img_disp: Optional[tk.Label] = None
        self.photo_ref: Optional[tk.PhotoImage] = None

        top = tk.Frame(root)
        top.pack(fill=tk.X, padx=10, pady=8)

        self.path_var = tk.StringVar()
        tk.Label(top, text="Image:").pack(side=tk.LEFT)
        tk.Entry(top, textvariable=self.path_var, width=60).pack(side=tk.LEFT, padx=6)
        tk.Button(top, text="Browse", command=self._browse).pack(side=tk.LEFT)
        tk.Button(top, text="Run Detection", command=self._run_detection).pack(side=tk.LEFT, padx=(8, 0))
        # Fit-to-window toggle
        self.fit_to_window = tk.BooleanVar(value=True)
        tk.Checkbutton(top, text="Fit to window", variable=self.fit_to_window).pack(side=tk.LEFT, padx=(12, 0))
        # Zoom slider (percentage)
        tk.Label(top, text="Zoom:").pack(side=tk.LEFT, padx=(12, 4))
        self.zoom_var = tk.DoubleVar(value=100.0)
        zoom = tk.Scale(top, from_=50, to=200, orient=tk.HORIZONTAL, showvalue=True, variable=self.zoom_var, length=140)
        zoom.pack(side=tk.LEFT)

        info = tk.Label(
            root,
            text=(
                "Loads an image, runs YOLO, and flips the signal GREEN if an ambulance is detected;"
                " otherwise stays RED. Configure target classes via --classes (default: 'ambulance')."
            ),
            justify=tk.LEFT,
            font=("Segoe UI", 9),
        )
        info.pack(padx=10, pady=(0, 6), anchor="w")

        body = tk.Frame(root)
        body.pack(fill=tk.BOTH, expand=True)

        self.preview_container = tk.Frame(body)
        self.preview_container.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.preview = tk.Label(self.preview_container)
        self.preview.pack(side=tk.LEFT, padx=10, pady=10)

        self.panel = TrafficPanel(body)
        self.panel.set_red()

        if self.model is None:
            messagebox.showwarning(
                "YOLO not available",
                "Ultralytics not installed or model not found. You can still load an image to show,"
                " but detections won't run until YOLO is available.")

    def _browse(self) -> None:
        fname = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Images", "*.jpg;*.jpeg;*.png;*.bmp;*.gif"),
                ("All Files", "*.*"),
            ],
        )
        if fname:
            self.path_var.set(fname)
            self._load_image(fname)

    def _load_image(self, path: str) -> None:
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", f"Failed to load image: {path}")
            return
        self.current_img_bgr = img
        self._update_preview(img)
        self.panel.set_red()

    def _get_available_preview_size(self) -> tuple[int, int]:
        # Estimate available space for the preview image
        self.root.update_idletasks()
        try:
            total_w = self.root.winfo_width()
            total_h = self.root.winfo_height()
            panel_w = self.panel.frame.winfo_width() or 200
            # margins/padding allowance
            avail_w = max(total_w - panel_w - 80, 320)
            avail_h = max(total_h - 180, 240)
            return int(avail_w), int(avail_h)
        except Exception:
            return self.max_preview_w, self.max_preview_h

    def _update_preview(self, bgr_img) -> None:
        # Scale image to fit window if enabled, otherwise use fixed caps
        h, w = bgr_img.shape[:2]
        if self.fit_to_window.get():
            avail_w, avail_h = self._get_available_preview_size()
            base_scale = min(avail_w / float(w), avail_h / float(h))
            # user zoom multiplies the base scale
            zoom_factor = max(0.1, min(self.zoom_var.get() / 100.0, 3.0))
            scale = base_scale * zoom_factor
            # cap to reasonable bounds
            scale = max(min(scale, 3.0), 0.1)
        else:
            base_scale = min(self.max_preview_w / float(w), self.max_preview_h / float(h), 1.0)
            zoom_factor = max(0.1, min(self.zoom_var.get() / 100.0, 3.0))
            scale = max(min(base_scale * zoom_factor, 3.0), 0.1)

        if abs(scale - 1.0) > 1e-3:
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
            bgr_img = cv2.resize(bgr_img, (new_w, new_h), interpolation=interp)

        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        photo = cv_to_photoimage(rgb)
        self.photo_ref = photo  # keep reference to avoid GC
        if self.current_img_disp is None:
            self.current_img_disp = tk.Label(self.preview, image=photo)
            self.current_img_disp.pack()
        else:
            self.current_img_disp.config(image=photo)

    def _run_detection(self) -> None:
        path = self.path_var.get().strip()
        if not path:
            messagebox.showinfo("Select Image", "Please select an image first.")
            return
        if self.current_img_bgr is None:
            self._load_image(path)
            if self.current_img_bgr is None:
                return

        if self.model is None:
            messagebox.showwarning("YOLO not available", "Detections cannot run without a YOLO model.")
            return

        img = self.current_img_bgr.copy()
        try:
            results = self.model(img, verbose=False)[0]  # type: ignore[operator]
            names = getattr(self.model, 'names', None)
        except Exception as e:
            messagebox.showerror("Detection Error", str(e))
            return

        detected_target = False
        if hasattr(results, 'boxes'):
            for box in results.boxes:  # type: ignore[attr-defined]
                xyxy = getattr(box, 'xyxy', None)
                cls = getattr(box, 'cls', None)
                conf = getattr(box, 'conf', None)
                if xyxy is None:
                    continue
                x1, y1, x2, y2 = map(int, xyxy[0].tolist())
                cls_id = int(cls[0]) if cls is not None else -1
                conf_v = float(conf[0]) if conf is not None else 0.0
                label = None
                if names and 0 <= cls_id < len(names):
                    label = str(names[cls_id]).lower()

                color = (0, 255, 0)
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img, f"{label or 'obj'} {conf_v:.2f}", (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                if label and self.target_classes:
                    if label in self.target_classes and conf_v >= self.conf_threshold:
                        detected_target = True
        
        self._update_preview(img)
        if detected_target:
            self.panel.set_green()
        else:
            self.panel.set_red()


def parse_args():
    p = argparse.ArgumentParser(description="Integrated YOLO + Traffic Signal demo (image input)")
    p.add_argument("--model", type=str, default=None, help="Path to YOLO model .pt (recommended: custom model with 'ambulance' class)")
    p.add_argument("--classes", type=str, default="emergency", help="Comma-separated target class names to trigger green signal (default: 'emergency')")
    p.add_argument("--conf", type=float, default=0.75, help="Confidence threshold required to trigger green (default: 0.75)")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    classes = [c.strip() for c in args.classes.split(",")]

    root = tk.Tk()
    app = IntegratedApp(root, model_path=args.model, target_classes=classes, conf_threshold=args.conf)
    root.mainloop()
