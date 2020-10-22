import cv2, time
import numpy as np
import random
import os 

if __name__ == '__main__' :

    # Read image
    im = cv2.imread("64129.jpg")
    
    # Select ROI
    r = cv2.selectROI(im)
    
    # Crop image
    imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    # Display cropped image
    cv2.imshow("Image", imCrop)
    cv2.waitKey(0)





    # Image path 
image_path = r'C:\\Users\\HP\Desktop\\C.S-Project\\60569.jpg'

# Image directory 
directory = r'C:\\Users\\HP\\Desktop'

# Using cv2.imread() method 
# to read the image 
img = cv2.imread(image_path) 

# Change the current directory 
# to specified directory 
os.chdir(directory) 

# List files and directories 
# in 'C:/Users/Rajnish/Desktop/GeeksforGeeks' 
print("Before saving image:") 
print(os.listdir(directory)) 

# Filename 
filename = 'savedImage.jpg'

# Using cv2.imwrite() method 
# Saving the image 
cv2.imwrite(filename, img) 

# List files and directories 
# in 'C:/Users / Rajnish / Desktop / GeeksforGeeks' 
print("After saving image:") 
print(os.listdir(directory)) 

print('Successfully saved') 

