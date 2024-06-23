import cv2
import numpy
from ultralytics import YOLO
import threading
from enum import Enum

from threading import Lock
from time import sleep

from Pythoncode.Pathfinding.CornerUtils import set_placements, get_corners_as_list
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Corner import Corner
from Pythoncode.model.Egg import Egg
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.model.Robot import Robot
from Pythoncode.model.Vip import Vip
from Pythoncode.model.coordinate import Coordinate


class CourtProperty(Enum):
    BALLS = 1
    VIP = 2
    CORNERS = 3
    OBSTACLE = 4
    EGG = 5
    ROBOT = 6
    PIXEL_PER_CM = 7


class CourtState(object):
    projections = None
    frame = None
    lock = Lock()
    model = None
    cap = None

    items = {CourtProperty.BALLS: list, CourtProperty.ROBOT: Robot, CourtProperty.VIP: Vip,
             CourtProperty.CORNERS: list, CourtProperty.OBSTACLE: Coordinate, CourtProperty.PIXEL_PER_CM: float}

    dist = None
    mtx = None
    omtx = None

    @classmethod
    def initialize(cls):
        # Pre calibrated values for the webcam
        cls.mtx = numpy.loadtxt('.\\calibration\\mtx.txt')
        cls.dist = numpy.loadtxt('.\\calibration\\dist.txt')
        cls.omtx = numpy.loadtxt('.\\calibration\\omtx.txt')

        model = YOLO("../model/best.pt")
        cls.model = model
        frame = None
        current_id = 0
        while frame is None:
            _, frame = cls.cap.read()

        frame = cv2.undistort(frame, cls.mtx, cls.dist, None, cls.omtx)

        results = model.predict(frame, conf=0.5)
        corners = {}
        boxes = results[0].boxes

        for box in boxes:
            if results[0].names[box.cls.item()] == "corner":
                x0, y0, x1, y1 = box.xyxy[0]
                x0 = int(x0)
                y0 = int(y0)
                x1 = int(x1)
                y1 = int(y1)
                corner = Corner(x0, y0, x1, y1)
                corners[current_id] = corner
                current_id += 1

        corners = set_placements(corners)

        cls.items[CourtProperty.CORNERS] = get_corners_as_list(corners)
        cls.analyse_results(results, frame)

        cv2.imshow("YOLO", results[0].plot())

    @classmethod
    def updateObjects(cls, drive_points, target):
        model = cls.model
        robot = cls.getProperty(CourtProperty.ROBOT)

        frame = None
        while cls.frame is None:
            sleep(0.05)

        frame = cv2.undistort(cls.frame, cls.mtx, cls.dist, None, cls.omtx)
        results = model.predict(frame, conf=0.5)

        if cv2.waitKey(1) == ord('q'):
            return

        img = cls.analyse_results(results, frame)
        if drive_points is not None:
            for drive_point in drive_points:
                img = cv2.circle(img,(int(drive_point.x), int(drive_point.y)), radius=5, color=(255, 0, 0), thickness=-1)
        cv2.imshow("YOLO", img)


    @classmethod
    def analyse_results(cls, results, frame):
        boxes = results[0].boxes.cpu()
        projection = cls.projections
        balls = []
        corners = []
        robot = None
        vipItem = None
        robot_body = None
        egg = None
        robot_front = None
        obstacle = None
        for box in boxes:
            x0, y0, x1, y1 = box.xyxy[0]
            item = box.cls.item()

            x0 = int(x0)
            x1 = int(x1)
            y0 = int(y0)
            y1 = int(y1)

            x = int(x0 + (x1-x0)/2)
            y = int(y0 + (y1-y0)/2)

            color = (0, 255, 255)
            match results[0].names[item]:
                case "ball":
                    color = (255, 255, 0)
                    balls.append(Ball(x0, y0, x1, y1))
                case "corner":
                    color = (100, 190, 255)
                    corner = Corner(x0, y0, x1, y1)
                    corners.append(corner)
                case "r_body":
                    color = (0, 255, 0)
                    robot_body = Coordinate(x, y)
                case "r_front":
                    color = (0, 0, 255)
                    robot_front = Coordinate(x, y)
                case "obstacle":
                    obstacle = Rectangle(Coordinate(x0, y0), Coordinate(x1, y1))
                case "egg":
                    egg = Egg(x0, y0, x1, y1)
                case "orange_ball":
                    vipItem = Vip(x0, y0, x1, y1)

            frame = cv2.circle(frame, (x, y), radius=5, color=color, thickness=-1)
        """"This is the true center of the robot post adjustment of top-hat."""
        true_center = Coordinate(int((robot_front.x + robot_body.x) / 2), int((robot_front.y + robot_body.y) / 2))
        robot = Robot(true_center, robot_front)
        frame = cv2.circle(frame, (true_center.x, true_center.y), radius=5, color=(255, 0, 255), thickness=-1)

        if obstacle is not None and egg is not None:
            egg.calculate_buffers(obstacle)

            color = (0, 255, 255)
            frame = cv2.circle(frame, (egg.buffer_center.x, egg.buffer_center.y), radius=5, color=color, thickness=-1)

            color = (255, 0, 0)
            frame = cv2.circle(frame, (egg.buffer_c2.x, egg.buffer_c2.y), radius=5, color=color, thickness=-1)

            v1 = numpy.array([int(egg.buffer.c1.x), int(egg.buffer.c1.y)])
            v2 = numpy.array([int(egg.buffer.c2.x), int(egg.buffer.c2.y)])
            cv2.rectangle(frame, v1, v2, color=(255, 0, 0), thickness=1)

            cls.items[CourtProperty.EGG] = egg

        cls.items[CourtProperty.VIP] = vipItem
        if robot is not None:
            cls.items[CourtProperty.ROBOT] = robot
        if len(balls) == 0 and vipItem is not None:
            balls.append(vipItem)
        cls.items[CourtProperty.BALLS] = balls
        cls.items[CourtProperty.OBSTACLE] = obstacle

        return frame

    @classmethod
    def setupCam(cls):
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        width = 1280
        height = 720
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # turn the autofocus off
        cls.cap = cap

        thread = threading.Thread(target=cls.frameThread)
        thread.start()



    @classmethod
    def getProperty(cls, property_name: CourtProperty):
        return cls.items[property_name]

    @classmethod
    def frameThread(cls):
        ret = True
        while ret:
            _, cls.frame = cls.cap.read()
        print("ret: " + str(ret))


    @classmethod
    def getFrame(cls):
        return cls.frame

    @classmethod
    def set_property(cls, property_name: CourtProperty, value):
        cls.items[property_name] = value
