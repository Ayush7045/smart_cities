import sys
import time
from typing import Optional

import cv2


def try_load_yolo() -> Optional[object]:
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception:
        return None

    # Try a few common lightweight checkpoints present in recent Ultralytics releases
    candidates = [
        "yolo11n.pt",  # 2024+
        "yolov10n.pt", # mid-2024
        "yolov8n.pt",  # widely available
    ]
    for ckpt in candidates:
        try:
            model = YOLO(ckpt)
            return model
        except Exception:
            continue
    return None


def draw_banner(frame, text: str, color=(0, 0, 255)) -> None:
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 50), color, thickness=-1)
    alpha = 0.35
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.putText(frame, text, (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)


def run_simulated_detection(cap: cv2.VideoCapture) -> None:
    """Fallback mode: no YOLO. Lets you toggle an 'EMERGENCY VEHICLE DETECTED' overlay.
    Controls:
      - E: toggle emergency banner
      - Q: quit
      - Space: pause/resume
    """
    emergency = False
    paused = False

    while True:
        if not paused:
            ok, frame = cap.read()
            if not ok:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # loop video; if webcam, it keeps streaming
                ok, frame = cap.read()
                if not ok:
                    break

        # Draw an example bounding box to simulate detection when emergency is on
        if emergency:
            h, w = frame.shape[:2]
            cx, cy = w // 2, int(h * 0.6)
            box_w, box_h = int(w * 0.35), int(h * 0.25)
            x1, y1 = cx - box_w // 2, cy - box_h // 2
            x2, y2 = cx + box_w // 2, cy + box_h // 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(frame, "Ambulance (simulated)", (x1, max(30, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            draw_banner(frame, "EMERGENCY VEHICLE DETECTED", color=(0, 0, 255))

        cv2.putText(frame, "Keys: [E]=Toggle Emergency  [Space]=Pause  [Q]=Quit", (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow("Detection Demo (Simulated)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q')):
            break
        if key == ord('e') or key == ord('E'):
            emergency = not emergency
        if key == 32:  # space
            paused = not paused

    cap.release()
    cv2.destroyAllWindows()


def run_yolo_detection(cap: cv2.VideoCapture, model: object) -> None:
    """YOLO mode: runs real detections (COCO). COCO doesn't have 'ambulance' label, so we
    highlight vehicles (car, truck, bus, motorcycle). You can still toggle the emergency banner.
    """
    try:
        names = model.names  # type: ignore[attr-defined]
    except Exception:
        names = None

    vehicle_names = set(["car", "truck", "bus", "motorcycle", "bicycle"])
    emergency = False

    while True:
        ok, frame = cap.read()
        if not ok:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = cap.read()
            if not ok:
                break

        # Run inference
        try:
            results = model(frame, verbose=False)[0]  # type: ignore[operator]
            # Draw boxes
            for box in results.boxes:  # type: ignore[attr-defined]
                cls_id = int(box.cls[0]) if hasattr(box, 'cls') else -1
                conf = float(box.conf[0]) if hasattr(box, 'conf') else 0.0
                xyxy = box.xyxy[0].tolist() if hasattr(box, 'xyxy') else None
                if xyxy is None:
                    continue
                x1, y1, x2, y2 = map(int, xyxy)
                label = names[cls_id] if names and 0 <= cls_id < len(names) else f"id{cls_id}"
                color = (0, 255, 0)

                # Emphasize vehicles; show a stronger color and thicker box
                is_vehicle = label in vehicle_names
                if is_vehicle:
                    color = (0, 200, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2 if not is_vehicle else 3)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # If you want to mark first detected vehicle as emergency for demo, uncomment:
                # emergency = emergency or is_vehicle
        except Exception:
            # If something goes wrong with inference, fallback to simulated overlay controls
            run_simulated_detection(cap)
            return

        if emergency:
            draw_banner(frame, "EMERGENCY VEHICLE DETECTED", color=(0, 0, 255))

        cv2.putText(frame, "Keys: [E]=Toggle Emergency Banner  [Q]=Quit", (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow("Detection Demo (YOLO)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q')):
            break
        if key == ord('e') or key == ord('E'):
            emergency = not emergency

    cap.release()
    cv2.destroyAllWindows()


def main() -> None:
    """Usage:
      python detect_demo.py              # webcam
      python detect_demo.py path\to\video.mp4
    
    Press 'E' to toggle the EMERGENCY banner for a clear recording cue.
    If Ultralytics is installed and a small model is available, real detections will be shown.
    Otherwise, simulated bounding boxes will be used.
    """
    source = 0 if len(sys.argv) < 2 else sys.argv[1]

    try:
        cap = cv2.VideoCapture(source)
    except Exception:
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open video source. Falling back to webcam 0.")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: No camera available.")
            return

    model = try_load_yolo()
    if model is None:
        run_simulated_detection(cap)
    else:
        run_yolo_detection(cap, model)


if __name__ == "__main__":
    main()
