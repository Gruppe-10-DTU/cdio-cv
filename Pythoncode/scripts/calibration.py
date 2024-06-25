"""
Calculate calibration values for the webcam and save to text files. Use values to undistort image later when running robot.

Source:
https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
"""

import numpy as np
import cv2 as cv
import glob

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7 * 7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2)*3.1   # 3,1 cm size of square

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

images = glob.glob('../sample/*.jpg')

dimensions = (1280, 720)

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7, 7), None)

    # If found, add object points, image points (after refining them)
    if ret:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv.drawChessboardCorners(img, (7, 7), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

cv.destroyAllWindows()

# Calibrated values
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, dimensions, None, None)

omtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (dimensions[0], dimensions[1]), 1, (dimensions[0], dimensions[1]))

np.savetxt("../calibration/mtx.txt", mtx)
np.savetxt("../calibration/dist.txt", dist)
np.savetxt("../calibration/omtx.txt", omtx)