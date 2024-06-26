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
        cls.mtx = numpy.loadtxt(
            'calibration/mtx.txt')
        cls.dist = numpy.loadtxt(
            'calibration/dist.txt')
        cls.omtx = numpy.loadtxt(
            'calibration/omtx.txt')

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
                corner = Corner(x0, y0, x1, y1,current_id)
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

        if cv2.waitKey(200) == ord('q'):
            return

        img = cls.analyse_results(results, frame)
        #cv2.imshow("YOLO", img)


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

            match results[0].names[item]:
                case "ball":
                    balls.append(Ball(x0, y0, x1, y1))
                case "corner":
                    corner = Corner(x0, y0, x1, y1,0)
                    corners.append(corner)
                case "r_body":
                    robot_body = Coordinate(x, y)
                case "r_front":
                    robot_front = Coordinate(x, y)
                case "obstacle":
                    obstacle = Rectangle(Coordinate(x0, y0), Coordinate(x1, y1))
                case "egg":
                    egg = Egg(x0, y0, x1, y1)
                case "orange_ball":
                    vipItem = Vip(x0, y0, x1, y1)

        """"This is the true center of the robot post adjustment of top-hat."""
        true_center = Coordinate(int((robot_front.x + robot_body.x) / 2), int((robot_front.y + robot_body.y) / 2))
        robot = Robot(true_center, robot_front)

        if obstacle is not None and egg is not None:
            egg.calculate_buffers(obstacle)

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
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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
