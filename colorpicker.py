import cv2
import numpy as np
# from datetime import datetime
# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 900, 600
SV_SIZE = 300
HUE_HEIGHT = 300

hue, sat, val = 0, 255, 255
drag_sv = drag_hue = False
dark_mode = False
history = []

# ---------------- THEME ----------------
def theme():
    return (30, 30, 30) if dark_mode else (240, 240, 240)

# ---------------- CREATE HUE BAR ----------------
def create_hue_bar():
    bar = np.zeros((HUE_HEIGHT, 30, 3), dtype=np.uint8)
    for i in range(HUE_HEIGHT):
        bar[i] = cv2.cvtColor(
            np.uint8([[[int(i * 180 / HUE_HEIGHT), 255, 255]]]),
            cv2.COLOR_HSV2BGR
        )
    return bar

hue_bar = create_hue_bar()

# ---------------- SV SQUARE ----------------
def create_sv(h):
    square = np.zeros((SV_SIZE, SV_SIZE, 3), dtype=np.uint8)
    for y in range(SV_SIZE):
        for x in range(SV_SIZE):
            square[y, x] = cv2.cvtColor(
                np.uint8([[[h, int(x * 255 / SV_SIZE), int(255 - y * 255 / SV_SIZE)]]]),
                cv2.COLOR_HSV2BGR
            )
    return square

sv_square = create_sv(hue)

# ---------------- MOUSE ----------------
def mouse(event, x, y, flags, param):
    global hue, sat, val, drag_sv, drag_hue, sv_square, history

    if 50 <= x <= 50+SV_SIZE and 50 <= y <= 50+SV_SIZE:
        if event == cv2.EVENT_LBUTTONDOWN:
            drag_sv = True
        if drag_sv and event in (cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONDOWN):
            sat = int((x-50) * 255 / SV_SIZE)
            val = int(255 - (y-50) * 255 / SV_SIZE)

    if 370 <= x <= 400 and 50 <= y <= 50+HUE_HEIGHT:
        if event == cv2.EVENT_LBUTTONDOWN:
            drag_hue = True
        if drag_hue and event in (cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONDOWN):
            hue = int((y-50) * 180 / HUE_HEIGHT)
            sv_square[:] = create_sv(hue)

    if event == cv2.EVENT_LBUTTONUP:
        drag_sv = drag_hue = False

cv2.namedWindow("Color Picker")
cv2.setMouseCallback("Color Picker", mouse)

# ---------------- MAIN LOOP ----------------
while True:
    canvas = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8)
    canvas[:] = theme()

    canvas[50:350, 50:350] = sv_square
    canvas[50:350, 370:400] = hue_bar

    # Cursor
    cv2.circle(canvas,
        (50 + int(sat*SV_SIZE/255), 50 + int((255-val)*SV_SIZE/255)),
        6, (255,255,255), 2)

    cv2.rectangle(canvas,
        (370, 50 + int(hue*HUE_HEIGHT/180)),
        (400, 55 + int(hue*HUE_HEIGHT/180)), (255,255,255), -1)

    # Current color
    bgr = cv2.cvtColor(np.uint8([[[hue, sat, val]]]), cv2.COLOR_HSV2BGR)[0][0]
    b,g,r = map(int, bgr)
    hex_code = f"#{r:02X}{g:02X}{b:02X}"

    canvas[50:200, 450:650] = (b,g,r)

    cv2.putText(canvas, f"RGB : {r}, {g}, {b}", (450,240),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.putText(canvas, f"HEX : {hex_code}", (450,280),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    # # Date Time
    # cv2.putText(canvas, datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    #     (450,320), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

    # History
    history.append((b,g,r))
    history = history[-6:]
    for i, c in enumerate(history):
        cv2.rectangle(canvas, (450+i*40,360), (480+i*40,390), c, -1)

    # Instructions
    cv2.putText(canvas,
        "C: Copy HEX  S: Save  D: Dark/Light  R: Reset  Q: Quit",
        (80,560), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

    cv2.imshow("Color Picker", canvas)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    if key == ord('d'):
        dark_mode = not dark_mode
    if key == ord('r'):
        hue, sat, val = 0, 255, 255
    if key == ord('s'):
        with open("colors.txt", "a") as f:
            f.write(hex_code + "\n")
    if key == ord('c'):
        print("Copied:", hex_code)

cv2.destroyAllWindows()
