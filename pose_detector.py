import cv2
import time
import mediapipe as mp
import argparse
import mediapipe as mp
import time


class PoseDetector:

    def __init__(self, mode = False, upBody = False, smooth=True, detectionCon = False, trackCon = 0.5):

        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)

    def findPose(self, img, draw=True):
        # print(img)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS

    def getPosition(self, img, draw=True):
        lmList= []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return lmList


# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--input", required=True,
#                 help="path to our input video")
# ap.add_argument("-o", "--output", required=True,
#                 help="path to our output video")
# ap.add_argument("-s", "--fps", type=int, default=30,
#                 help="set fps of output video")
# ap.add_argument("-b", "--black", type=str, default=False,
#                 help="set black background")
# args = vars(ap.parse_args())

if __name__ == "__main__":
    pTime = 0
    # black_flag = eval(args["black"])
    # cap = cv2.VideoCapture(args["input"])
    # out = cv2.VideoWriter(args["output"], cv2.VideoWriter_fourcc(*"MJPG"),
    #                       args["fps"], (int(cap.get(3)), int(cap.get(4))))

    cap = cv2.VideoCapture(0)
    detector = PoseDetector()
    print(1)
    while (cap.isOpened()):
        print(2)
        success, img = cap.read()
        print(img)

        if success == False:
            break

        img, p_landmarks, p_connections = detector.findPose(img, False)


        # draw points
        # print(p_landmarks)
        # print(p_connections)

        mp.solutions.drawing_utils.draw_landmarks(img, p_landmarks, p_connections)
        lmList = detector.getPosition(img)
        print(lmList)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # out.write(img)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


    cap.release()
    #out.release()
    cv2.destroyAllWindows()