import cv2

def videoRec():
    fps = int(camera.get(cv2.CAP_PROP_FPS))                    # カメラのFPSを取得
    w = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))              # カメラの横幅を取得
    h = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))             # カメラの縦幅を取得
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')        # 動画保存時のfourcc設定（mp4用）
    video = cv2.VideoWriter('video.mp4', fourcc, fps, (w, h))

    print("fps:{}".format(fps))
    print("width:{}".format(w))
    print("height:{}".format(h))
    while True:
        ret, frame = camera.read()                             # フレームを取得



        cv2.imshow('camera', frame)                            # フレームを画面に表示
        video.write(frame)                                     # 動画を1フレームずつ保存する


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if waitkey

        
if __name__ == "__main__":
    camera = cv2.VideoCapture(0) 

    videoRec()


    print("ended")
    camera.release()
    cv2.destroyAllWindows()