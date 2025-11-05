import threading
import time
import tkinter as tk
from dataclasses import dataclass
from typing import List


@dataclass
class IntersectionState:
    name: str
    distance_cm: float
    green_on: bool
    # Once vehicle has passed (<10cm), mark cleared to prevent re-green flicker
    cleared: bool = False


class TrafficDemoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart Traffic Management - Emergency Vehicle Demo")
        self.is_running = False
        self.reset_requested = False

        self.intersections: List[IntersectionState] = [
            IntersectionState(name="Node 1", distance_cm=120.0, green_on=False),
            IntersectionState(name="Node 2", distance_cm=220.0, green_on=False),
            IntersectionState(name="Node 3", distance_cm=320.0, green_on=False),
        ]

        self._build_ui()
        self._render_all()

    def _build_ui(self) -> None:
        header = tk.Label(
            self.root,
            text=(
                "Emergency vehicle approaches intersections sequentially.\n"
                "When distance < 20 cm, the intersection turns GREEN to give way;\n"
                "when vehicle passes (< 10 cm), it returns to RED and next node prepares."
            ),
            justify=tk.LEFT,
            font=("Segoe UI", 10),
        )
        header.pack(padx=12, pady=(12, 6), anchor="w")

        self.cards_frame = tk.Frame(self.root)
        self.cards_frame.pack(padx=12, pady=12, fill=tk.X)

        self.cards: List[tk.Frame] = []
        self.state_labels: List[tk.Label] = []
        self.distance_labels: List[tk.Label] = []
        self.red_lights: List[tk.Canvas] = []
        self.green_lights: List[tk.Canvas] = []

        for idx, state in enumerate(self.intersections):
            card = tk.Frame(self.cards_frame, borderwidth=1, relief=tk.GROOVE)
            card.grid(row=0, column=idx, padx=8, pady=8, sticky="n")
            self.cards.append(card)

            title = tk.Label(card, text=state.name, font=("Segoe UI", 12, "bold"))
            title.pack(padx=10, pady=(10, 4))

            distance_label = tk.Label(card, text="Distance: -- cm", font=("Segoe UI", 10))
            distance_label.pack(padx=10)
            self.distance_labels.append(distance_label)

            state_label = tk.Label(card, text="State: RED", font=("Segoe UI", 10))
            state_label.pack(padx=10, pady=(2, 8))
            self.state_labels.append(state_label)

            lights = tk.Frame(card)
            lights.pack(padx=10, pady=(0, 10))

            red = tk.Canvas(lights, width=30, height=30, bg="#300", highlightthickness=0)
            red.grid(row=0, column=0, padx=4)
            red.create_oval(4, 4, 26, 26, fill="#700", outline="")
            self.red_lights.append(red)

            green = tk.Canvas(lights, width=30, height=30, bg="#030", highlightthickness=0)
            green.grid(row=0, column=1, padx=4)
            green.create_oval(4, 4, 26, 26, fill="#070", outline="")
            self.green_lights.append(green)

        controls = tk.Frame(self.root)
        controls.pack(padx=12, pady=(0, 12), fill=tk.X)

        self.start_btn = tk.Button(controls, text="Start Ambulance", command=self.start_demo)
        self.start_btn.pack(side=tk.LEFT)

        self.reset_btn = tk.Button(controls, text="Reset", command=self.reset_demo)
        self.reset_btn.pack(side=tk.LEFT, padx=(8, 0))

        note = tk.Label(
            self.root,
            text="Tip: Start screen recording, click 'Start Ambulance', and narrate the behavior.",
            font=("Segoe UI", 9, "italic"),
        )
        note.pack(padx=12, pady=(0, 12), anchor="w")

    def _render_all(self) -> None:
        for idx, st in enumerate(self.intersections):
            self.distance_labels[idx].config(text=f"Distance: {st.distance_cm:.0f} cm")
            self.state_labels[idx].config(text=f"State: {'GREEN' if st.green_on else 'RED'}")

            # Update light visuals
            if st.green_on:
                self.green_lights[idx].itemconfig(1, fill="#0f0")
                self.red_lights[idx].itemconfig(1, fill="#700")
            else:
                self.green_lights[idx].itemconfig(1, fill="#070")
                self.red_lights[idx].itemconfig(1, fill="#f00")

    def start_demo(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self.reset_requested = False
        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._run_sequence, daemon=True).start()

    def reset_demo(self) -> None:
        self.reset_requested = True
        self.is_running = False
        for idx, st in enumerate(self.intersections):
            st.distance_cm = 100.0 * (idx + 1) + 20.0
            st.green_on = False
            st.cleared = False
        self._render_all()
        self.start_btn.config(state=tk.NORMAL)

    def _run_sequence(self) -> None:
        try:
            # Simulate ambulance approaching each node in order
            for idx, st in enumerate(self.intersections):
                # Approach phase: from current distance down to 5 cm
                while st.distance_cm > 5.0 and not self.reset_requested:
                    # Move faster when far, slower when near for dramatic effect
                    step = 8.0 if st.distance_cm > 80 else 4.0 if st.distance_cm > 40 else 2.0
                    st.distance_cm = max(5.0, st.distance_cm - step)

                    # Control rule: if distance < 20 and not yet cleared, go green
                    if st.distance_cm < 20.0 and not st.green_on and not st.cleared:
                        st.green_on = True
                    # If at/past the stop line, briefly show green then return to red and mark cleared
                    if st.distance_cm <= 10.0 and st.green_on and not st.cleared:
                        # Briefly keep green, then switch back to red to simulate vehicle passing
                        self._render_all_async()
                        time.sleep(0.6)
                        st.green_on = False
                        st.cleared = True

                    self._render_all_async()
                    time.sleep(0.12)

                if self.reset_requested:
                    break

                # Ensure final state after pass
                st.distance_cm = 8.0
                st.green_on = False
                # Keep cleared True so it doesn't re-green in this cycle
                self._render_all_async()

                # Brief pause before next node starts reacting
                time.sleep(0.6)
        finally:
            self.is_running = False
            self._enable_start_async()

    def _render_all_async(self) -> None:
        self.root.after(0, self._render_all)

    def _enable_start_async(self) -> None:
        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficDemoApp(root)
    root.mainloop()
