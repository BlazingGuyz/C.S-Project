import cv2, time
import random
import numpy as np
import os
import save
video = cv2.VideoCapture(0) 
a = 0

while True:
    a = a + 1
    #print(a)
    # 3.Create a frame object
    check, frame = video.read()
    #print(check)
    #print(frame)
    
    # 6. Converting to grayscale
    #gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    # 4.show the frame!
    cv2.imshow("Capturing",frame)
    
    # 5. for press any key to out (miliseconds)
    #cv2.waitKey(0)
    
    # 7. for playing 
    key = cv2.waitKey(1)
    
    if key == ord('q'):
        break
showPic = cv2.imwrite(str(random.randint(1100,111110)) + ".jpg", frame)
print(a)
# 2. shutdown the camera
video.release()

 
 





if __name__ == '__main__' :

    # Read image
    
    
    # Select ROI
    r = cv2.selectROI(frame)
    
    # Crop image
    imCrop = r[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    # Display cropped image
    cv2.imshow("Image", imCrop)
    cv2.waitKey()

save("98524.jpg")

cv2.destroyAllWindows()



