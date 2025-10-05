"""
Rock Paper Scissors (Gesture Edition)
-------------------------------------------------------------
Camera-powered Rock, Paper, Scissors, Pencil game with a 16:9 Tkinter GUI.
"""

import random
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import cv2
import mediapipe as mp
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk

@dataclass
class GestureResult:
    name: str
    confidence: float


class GestureRecognizer:
    _FINGER_LANDMARKS = {
        "thumb": (4, 3),
        "index": (8, 6),
        "middle": (12, 10),
        "ring": (16, 14),
        "pinky": (20, 18),
    }

    def __init__(self) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
        )
        self._drawer = mp.solutions.drawing_utils
        self._drawer_styles = mp.solutions.drawing_styles

    def process(self, frame_bgr) -> Tuple[GestureResult, Optional[Any]]:
        """Process a frame and return (gesture_result, landmarks)."""

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return GestureResult("unknown", 0.0), None

        hand_landmarks = results.multi_hand_landmarks[0]
        gesture_name = self._classify(hand_landmarks)
        confidence = 1.0 if gesture_name != "unknown" else 0.0
        return GestureResult(gesture_name, confidence), hand_landmarks

    def draw_landmarks(self, frame_bgr, hand_landmarks) -> None:
        if hand_landmarks is None:
            return
        self._drawer.draw_landmarks(
            frame_bgr,
            hand_landmarks,
            self._mp_hands.HAND_CONNECTIONS,
            self._drawer_styles.get_default_hand_landmarks_style(),
            self._drawer_styles.get_default_hand_connections_style(),
        )

    def _classify(self, landmarks) -> str:
        def _is_extended(tip_idx: int, pip_idx: int) -> bool:
            return landmarks.landmark[tip_idx].y < landmarks.landmark[pip_idx].y

        fingers_extended: Dict[str, bool] = {
            finger: _is_extended(*idx_pair)
            for finger, idx_pair in self._FINGER_LANDMARKS.items()
        }

        thumb = fingers_extended["thumb"]
        index = fingers_extended["index"]
        middle = fingers_extended["middle"]
        ring = fingers_extended["ring"]
        pinky = fingers_extended["pinky"]

        if not any((thumb, index, middle, ring, pinky)):
            return "rock"
        if all((thumb, index, middle, ring, pinky)):
            return "paper"
        if index and not any((middle, ring, pinky)):
            return "pencil"
        if index and middle and not any((ring, pinky)):
            return "scissors"
        return "unknown"


class GestureRPSGame:
    MOVES = ("rock", "paper", "scissors", "pencil")
    WIN_RULES = {
        "rock": {"scissors", "pencil"},
        "paper": {"rock"},
        "scissors": {"paper", "pencil"},
        "pencil": {"paper"},
    }

    def __init__(self) -> None:
        self.score = {"player": 0, "computer": 0, "ties": 0}

    def get_computer_move(self) -> str:
        return random.choice(self.MOVES)

    def resolve_round(self, player_move: str, computer_move: str) -> str:
        if player_move == computer_move:
            self.score["ties"] += 1
            return "It's a tie!"

        if computer_move in self.WIN_RULES.get(player_move, set()):
            self.score["player"] += 1
            return f"You win! {player_move.title()} beats {computer_move}."

        self.score["computer"] += 1
        return f"I win! {computer_move.title()} beats {player_move}."

class GestureRPSApp:
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("Gesture Rock Paper Scissors")
        self.window.geometry("1280x720")  
        self.window.configure(bg="#111111")
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        self._configure_styles()

        self.game = GestureRPSGame()
        self.recognizer = GestureRecognizer()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.cap.isOpened():
            tk.messagebox.showerror("Camera Error", "Unable to access the camera.")
            self.window.destroy()
            sys.exit(1)

        self._setup_layout()

        self.last_gesture = "unknown"
        self._gesture_frames = 0
        self._lockout = False
        self._lockout_after_id: Optional[str] = None

        self._update_video()

    def run(self) -> None:
        self.window.mainloop()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#111111")
        style.configure("Title.TLabel", foreground="#FFFFFF", background="#111111", font=("Segoe UI", 28, "bold"))
        style.configure("Status.TLabel", foreground="#08f7fe", background="#111111", font=("Segoe UI", 18))
        style.configure("ScoreValue.TLabel", foreground="#FFFFFF", background="#111111", font=("Consolas", 24, "bold"))
        style.configure("ScoreLabel.TLabel", foreground="#aaaaaa", background="#111111", font=("Segoe UI", 14))
        style.configure("Info.TLabel", foreground="#cccccc", background="#111111", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12))

    def _setup_layout(self) -> None:
        container = ttk.Frame(self.window, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        self.video_label = ttk.Label(container)
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        side_panel = ttk.Frame(container)
        side_panel.grid(row=0, column=1, sticky="nsew")
        side_panel.columnconfigure(0, weight=1)

        ttk.Label(side_panel, text="Rock Paper Scissors", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(side_panel, text="Use your hand to play", style="Info.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 20))

        self.status_var = tk.StringVar(value="Show a gesture to start!")
        ttk.Label(side_panel, textvariable=self.status_var, style="Status.TLabel").grid(row=2, column=0, sticky="w")

        score_frame = ttk.Frame(side_panel, padding=(0, 30, 0, 20))
        score_frame.grid(row=3, column=0, sticky="w")

        self._player_score_var = tk.StringVar(value="0")
        self._computer_score_var = tk.StringVar(value="0")
        self._tie_score_var = tk.StringVar(value="0")

        ttk.Label(score_frame, text="You", style="ScoreLabel.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(score_frame, textvariable=self._player_score_var, style="ScoreValue.TLabel").grid(row=1, column=0, sticky="w")

        ttk.Label(score_frame, text="Me", style="ScoreLabel.TLabel").grid(row=0, column=1, padx=(40, 0), sticky="w")
        ttk.Label(score_frame, textvariable=self._computer_score_var, style="ScoreValue.TLabel").grid(row=1, column=1, padx=(40, 0), sticky="w")

        ttk.Label(score_frame, text="Ties", style="ScoreLabel.TLabel").grid(row=0, column=2, padx=(40, 0), sticky="w")
        ttk.Label(score_frame, textvariable=self._tie_score_var, style="ScoreValue.TLabel").grid(row=1, column=2, padx=(40, 0), sticky="w")

        info_text = (
            "Gestures:\n"
            "Rock = Fist\n"
            "Paper = Open palm\n"
            "Scissors = Index + middle fingers\n"
            "Pencil = Index finger only"
        )
        ttk.Label(side_panel, text=info_text, style="Info.TLabel", justify=tk.LEFT).grid(row=4, column=0, sticky="w")

        self.reset_button = ttk.Button(side_panel, text="Reset", command=self._reset_game)
        self.reset_button.grid(row=5, column=0, pady=(30, 0), sticky="w")

    def _update_video(self) -> None:
        ret, frame = self.cap.read()
        if not ret:
            self.status_var.set("Camera feed unavailable.")
            self.window.after(500, self._update_video)
            return

        frame = cv2.flip(frame, 1)
        gesture_result, hand_landmarks = self.recognizer.process(frame)
        self.recognizer.draw_landmarks(frame, hand_landmarks)

        if not self._lockout:
            self._handle_gesture(gesture_result)

        display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        display_frame = cv2.resize(display_frame, (960, 540))
        image = Image.fromarray(display_frame)
        photo = ImageTk.PhotoImage(image=image)
        self.video_label.configure(image=photo)
        self.video_label.image = photo

        self.window.after(30, self._update_video)

    def _handle_gesture(self, gesture_result: GestureResult) -> None:
        gesture = gesture_result.name
        if gesture == "unknown":
            self.last_gesture = "unknown"
            self._gesture_frames = 0
            self.status_var.set("Waiting for a gesture…")
            return

        if gesture == self.last_gesture:
            self._gesture_frames += 1
        else:
            self._gesture_frames = 1
            self.last_gesture = gesture

        if self._gesture_frames >= 10:  
            self._lockout = True
            self._resolve_round(gesture)
            self._gesture_frames = 0
            self.last_gesture = "unknown"
            self._lockout_after_id = self.window.after(1800, self._release_lockout)

    def _resolve_round(self, player_move: str) -> None:
        computer_move = self.game.get_computer_move()
        message = self.game.resolve_round(player_move, computer_move)
        self._player_score_var.set(str(self.game.score["player"]))
        self._computer_score_var.set(str(self.game.score["computer"]))
        self._tie_score_var.set(str(self.game.score["ties"]))
        self.status_var.set(
            f"You played {player_move}. I played {computer_move}.\n{message}"
        )

    def _release_lockout(self) -> None:
        self._lockout = False
        self.status_var.set("Show a gesture to play!")

    def _reset_game(self) -> None:
        if self._lockout_after_id is not None:
            self.window.after_cancel(self._lockout_after_id)
            self._lockout_after_id = None
        self._lockout = False
        self.last_gesture = "unknown"
        self._gesture_frames = 0
        self.game = GestureRPSGame()
        self._player_score_var.set("0")
        self._computer_score_var.set("0")
        self._tie_score_var.set("0")
        self.status_var.set("Scores cleared. Show a gesture to play!")

    def _on_close(self) -> None:
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()


if __name__ == "__main__":
    try:
        app = GestureRPSApp()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)
