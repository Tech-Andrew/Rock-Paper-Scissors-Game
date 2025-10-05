# Rock-Paper-Scissors-Game
Play Rock, Paper, Scissors, and Pencil using your hand gestures! 
A Mediapipe-powered real-time computer vision game with a modern 16:9 Tkinter GUI.
🎮 Rock Paper Scissors (Gesture Edition)
A camera-powered Rock–Paper–Scissors–Pencil game built with Python, MediaPipe, OpenCV, and Tkinter.
The game recognizes your hand gestures in real-time and lets you play against the computer inside a sleek 16:9 GUI window.

**✋ Features**

_🧠 Gesture Recognition_ — Detects your hand and classifies gestures as Rock, Paper, Scissors, or Pencil using MediaPipe landmarks.

_🎥 Live Camera Feed_ — Real-time OpenCV camera preview integrated into the Tkinter window.

_🪟 Modern GUI_ — Clean, responsive interface built with ttk themes and styled labels.

_🧩 Smart Gameplay_ — Tracks wins, losses, and ties with auto-scoring.

_🕹️ Gesture Lockout_ — Prevents double-counting by requiring consistent gesture detection across frames.

_🧼 Reset Button_ — Instantly clear scores and start fresh.

**🪄 How It Works**
1. Launch the program.
2. Show one of the following gestures in front of your webcam:
✊ Rock → Fist
✋ Paper → Open palm
✌️ Scissors → Index + middle fingers
☝️ Pencil → Index finger only

The computer makes its move and the winner is shown in real-time.

Scores update automatically.

**⚙️ Requirements**

Python 3.9+

Packages:

pip install opencv-python mediapipe pillow


(Tkinter is included with most Python installations.)

**🚀 Run It**
python gesture_rps.py

**🧩 Tech Stack**

OpenCV – For camera handling and frame processing

MediaPipe Hands – For detecting and classifying hand gestures

Tkinter + ttk – For building the interactive GUI

PIL (Pillow) – For converting frames to displayable images

**🧠 Game Logic**

The game supports four moves:

rock     beats scissors, pencil
paper    beats rock
scissors beats paper, pencil
pencil   beats paper


Ties are counted separately.

🧑‍💻 Author

Built with ❤️ by Tech-Andrew — combining computer vision, game logic, and Python UI design into one playful experience.
