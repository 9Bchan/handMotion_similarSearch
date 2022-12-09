import cv2
import mediapipe as mp


def cam_MP():
    cap = cv2.VideoCapture("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/edited_video/tango/1.mp4")
    
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    isStop = 0
    while True:
        ret, frame = cap.read()

        if ret:
            frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            holistic_results = holistic.process(frame_RGB)

            mp_drawing.draw_landmarks(
                frame, holistic_results.face_landmarks, mp_holistic.FACE_CONNECTIONS)
            mp_drawing.draw_landmarks(
                frame, holistic_results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(
                frame, holistic_results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(
                frame, holistic_results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            if holistic_results.right_hand_landmarks is not None:
                rightHand_randmarks = holistic_results.right_hand_landmarks.landmark
                rightWrist_randmarks = rightHand_randmarks[0]
                cv2.putText(frame,
                            text='R',
                            org=(int(rightWrist_randmarks.x*frame_width), int(rightWrist_randmarks.y*frame_height)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=1.0,
                            color=(0, 100, 255),
                            thickness=6,
                            lineType=cv2.LINE_4)

            if holistic_results.left_hand_landmarks is not None:
                leftHand_randmarks = holistic_results.left_hand_landmarks.landmark
                leftWrist_randmarks = leftHand_randmarks[0]
                cv2.putText(frame,
                            text='L',
                            org=(int(leftWrist_randmarks.x*frame_width), int(leftWrist_randmarks.y*frame_height)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=1.0,
                            color=(255, 100, 0),
                            thickness=6,
                            lineType=cv2.LINE_4)
            

            cv2.imshow("MP_holistic",frame)
        

            
            key = cv2.waitKey(isStop)
            if key & 0xFF == ord('s'):
                isStop = 1
            if key & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()




if __name__ == "__main__":
    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic

    holistic =  mp_holistic.Holistic(
            static_image_mode=False,        # 静止画:True 動画:False
            #UPPER_BODY_ONLY=True,           # 上半身のみ:True 全身:False
            smooth_landmarks=True,          # ジッターを減らすかどうか
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    cam_MP()

    print("ended")