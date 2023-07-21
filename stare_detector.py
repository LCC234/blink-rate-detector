import time
import logging
import cv2
import dlib
import imutils
import numpy as np
from imutils import face_utils
from utils import eye_aspect_ratio, send_email, send_sms, add_to_low_blink_list, get_console_logging_handler, ALERT_CONFIRMATION_COUNT

# Define constants
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 1
BLINK_RATE_LOWER_THRESHOLD = 0.1 # blinks per second
BLINK_RATE_FRAME_COUNT = 20 # number of frames required to aggregate blink rate
FPS_AVG_FRAME_COUNT = 10 # number of frames required to aggregate frame rate
MIN_ALERT_INTERVAL = 60 * 15 # 15 mins

# FPS variables
frame_counter, fps = 0, 0
frame_start_time = time.time()

# Display variables
row_size = 30  # pixels
left_margin = 10
right_margin = 590
text_color = (0, 0, 255)  # red
font_size = 0.7
font_thickness = 2

# Blink rate variables
blink_start_time = time.time()
cur_frame_total_blinks = 0
total_blinks = 0
blink_rate = 3
eyelid_closed_counter = 0
low_blink_rate_counter = 0
low_blink_rate_list = []

# Alert variables
alert_send_time = 0

# logging
logger = logging.getLogger('stare_detector')
logger.setLevel(logging.DEBUG)
logger.addHandler(get_console_logging_handler())

# Initialise face detector and predictor
logger.info("loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while cap.isOpened():


    # Read Frame
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=800)

    # Frame counter
    frame_counter += 1

    # Calculate the FPS
    if frame_counter % FPS_AVG_FRAME_COUNT == 0:
        frame_end_time = time.time()
        fps = FPS_AVG_FRAME_COUNT / (frame_end_time - frame_start_time)
        frame_start_time = time.time()
        
    # Display FPS
    fps_text = f'{round(fps,2)} Frames/Sec'
    text_location = (right_margin, row_size)
    cv2.putText(frame, fps_text, text_location, cv2.FONT_HERSHEY_SIMPLEX,
                font_size, text_color, font_thickness)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:

        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            eyelid_closed_counter += 1
        else:
            if eyelid_closed_counter >= EYE_AR_CONSEC_FRAMES:
                total_blinks += 1
                cur_frame_total_blinks += 1
            eyelid_closed_counter = 0
        
        # Calculate the blink rate
        if frame_counter % BLINK_RATE_FRAME_COUNT == 0:
            blink_end_time = time.time()
            blink_rate = round(cur_frame_total_blinks / (blink_end_time - blink_start_time),2)
            cur_frame_total_blinks = 0
            blink_start_time = time.time()

        cv2.putText(
            frame,
            "Total Blinks: {}".format(total_blinks),
            (left_margin, row_size),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size,
            text_color,
            font_thickness,
        )
        cv2.putText(
            frame,
            "EAR: {:.2f}".format(ear),
            (left_margin + 200, row_size),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size,
            text_color,
            font_thickness,
        )

        if blink_rate < BLINK_RATE_LOWER_THRESHOLD:
            blink_rate_display_msg = f'Blink rate: {blink_rate} Blinks/Sec (Warning! Low Blink Rate/Staring detected!)'
            # Reads when new blink rate is computed
            if frame_counter % BLINK_RATE_FRAME_COUNT == 0:
                low_blink_rate_counter += 1
                low_blink_rate_list = add_to_low_blink_list(blink_rate, low_blink_rate_list)
                logger.info(f"{low_blink_rate_counter = }")
                logger.info(f"Added low blink rate of {blink_rate}. Warning list now contains {','.join(str(b) for b in low_blink_rate_list)}")
                if low_blink_rate_counter > ALERT_CONFIRMATION_COUNT:
                    low_blink_rate_counter = 0
                    if (time.time() - alert_send_time) > MIN_ALERT_INTERVAL:
                        consec_blink_rate = ','.join(str(b) for b in low_blink_rate_list)
                        logger.info(f"Warning counter more than {ALERT_CONFIRMATION_COUNT} times! Sending Email and SMS now.")
                        # send_email(f"Seizure Early Warning Alert!", f"Consective low blink rates of {consec_blink_rate} Frames per second. Please alert relevant medical team!") 
                        logger.info(f"Email sent!")
                        # send_sms(f"Seizure Early Warning Alert! Consective low blink rates of {consec_blink_rate} Frames per second. Please alert relevant medical team!")
                        logger.info(f"SMS sent!")
                        alert_send_time = time.time()
                        logger.info(f"Alert time reset")
                    low_blink_rate_list = []
                    
        else:
            blink_rate_display_msg = f'Blink rate: {blink_rate} Blinks/Sec (Normal)'

        cv2.putText(
            frame,
            blink_rate_display_msg,
            (left_margin, row_size * 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size,
            text_color,
            font_thickness,
        )

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


cv2.destroyAllWindows()