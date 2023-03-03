import cv2
import numpy as np


# Load the image in grayscale
img = cv2.imread('test/meshing/075775_treated_xye.png', 0)
# Apply Gaussian blur to smooth the image
blur = cv2.GaussianBlur(img, (5, 5), 0)

# Apply adaptive thresholding to binarize the image
thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
# Find the contours in the thresholded image
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# Create a blank image to draw the components onto
components = np.zeros_like(thresh)

# Iterate through the contours and draw each one onto the components image
for i in range(len(contours)):
    cv2.drawContours(components, contours, i, (255, 255, 255), -1)

