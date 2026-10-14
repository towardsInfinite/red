import cv2
import time

cap = cv2.VideoCapture(0)
prev_gray = None
score = 0
state = "GREEN"
last_switch = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # 1. Motion Detection (Same concept as Bubble Pop!)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    if prev_gray is None:
        prev_gray = gray
        continue

    diff = cv2.absdiff(prev_gray, gray)
    _, mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    prev_gray = gray
    movement = cv2.countNonZero(mask)

    # 2. Traffic Light Timer (Switch states every few seconds)
    elapsed = time.time() - last_switch
    if state == "GREEN" and elapsed > 4.0:
        state = "YELLOW"
        last_switch = time.time()
    elif state == "YELLOW" and elapsed > 1.5:
        state = "RED"
        last_switch = time.time()
    elif state == "RED" and elapsed > 3.0:
        state = "GREEN"
        last_switch = time.time()

    # 3. Game Rules per State
    if state == "GREEN":
        color = (0, 255, 0)
        msg = "GREEN LIGHT: DANCE TO SCORE!"
        if movement > 3000:
            score += 1
    elif state == "YELLOW":
        color = (0, 255, 255)
        msg = "YELLOW LIGHT: GET READY TO FREEZE!"
    elif state == "RED":
        color = (0, 0, 255)
        msg = "RED LIGHT: DON'T MOVE A MUSCLE!"
        if movement > 1500:  # Caught flinching!
            msg = "CAUGHT MOVING! -5 POINTS!"
            score = max(0, score - 5)
            frame[:] = (0, 0, 255)  # Flash the whole screen red

    # 4. Draw UI Banner
    cv2.rectangle(frame, (0, 0), (w, 90), color, -1)
    cv2.putText(frame, msg, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 3)
    cv2.putText(frame, f"Score: {score}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 2)

    cv2.imshow("Red Light, Green Light! (Press 'q' to quit)", frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()