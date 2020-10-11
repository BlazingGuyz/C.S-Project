import cv2
import numpy as np
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


video = cv2.VideoCapture(0) 
# 8. Variable
a = 0

while:
     a = a + 1
    #print(a)
    # 3.Create a frame object
    check, video = video.read()
    #print(check)
    #print(frame) 
 while :
     video.isOpened():
    _, video = video.read()
    gray = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Display the output
    cv2.imshow('video', video)
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
showPic = cv2.imwrite(str(random.randint(1100,111110)) + ".jpg", video)

print(a)

video.release()

cv2.destroyAllWindows() 