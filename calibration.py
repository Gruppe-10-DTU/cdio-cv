"""
Source:
https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga887960ea1bde84784e7f1710a922b93c
"""

import numpy as np
import cv2 as cv
import glob

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6 * 7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

images = glob.glob('./sample/*.jpg')

# dimensions = (1920, 1080)
dimensions = (640, 480)

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7, 6), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv.drawChessboardCorners(img, (7, 6), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

cv.destroyAllWindows()

# Calibrated values
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, dimensions, None, None)


test = cv.undistortImagePoints(np.array([[50, 30],[600, 400]], dtype=np.float32), mtx, dist)

