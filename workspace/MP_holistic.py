import cv2
import mediapipe as mp


def cam_MP():
    #cap = cv2.VideoCapture("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/edited_video_part/bunsyo/4.mp4")
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/edited_video_part/tango/33.mp4")
    #C:/Users/hisa/Desktop/research/
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    totalFrame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


    print("frame width : "+ str(frame_width))
    print("frame height : "+str(frame_height))
    print("total frame : "+str(totalFrame))
    
    isStop = 0
    isLoop = False
    while True:
        ret, frame = cap.read(0)
        

        if ret:
            frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            holistic_results = holistic.process(frame_RGB)

            '''
            mp_drawing.draw_landmarks(
                frame, holistic_results.face_landmarks, mp_holistic.FACE_CONNECTIONS)'''
            
            mp_drawing.draw_landmarks(
                image=frame, 
                landmark_list=holistic_results.left_hand_landmarks, 
                connections=mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=[0, 180, 0], thickness=2, circle_radius=4),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=[0, 180, 0], thickness=2, circle_radius=4))
            
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=holistic_results.right_hand_landmarks,
                connections=mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=[0, 0, 180], thickness=2, circle_radius=4),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=[0, 0, 180], thickness=2, circle_radius=4))
            
            
            mp_drawing.draw_landmarks(
                frame, holistic_results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            if holistic_results.pose_landmarks is not None:
                print(holistic_results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_SHOULDER])
            '''
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
            '''

            cv2.imshow("MP_holistic",frame)

            currentFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            print(currentFrame)

            
            key = cv2.waitKey(isStop)
            if key & 0xFF == ord('s'):
                if isStop == 0:
                    isStop = 1
                elif isStop == 1:
                    isStop = 0
            
            if key & 0xFF == ord('p'):
                startFrame = int(input("start frame?"))
                endFrame = int(input("end frame?"))
                cap.set(cv2.CAP_PROP_POS_FRAMES, startFrame)

                isLoop = True
            if isLoop:
                if cap.get(cv2.CAP_PROP_POS_FRAMES) > endFrame:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, startFrame)
            
            if key & 0xFF == ord('b'):
                cap.set(cv2.CAP_PROP_POS_FRAMES, currentFrame - 2)

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
