import cv2
from ultralytics import YOLO
import threading
from enum import Enum

from threading import Lock
from time import sleep

from Pythoncode.Pathfinding import drive_points
from Pythoncode.Pathfinding.CornerUtils import set_placements, get_corners_as_list
from Pythoncode.Pathfinding.Projection import Projection
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Corner import Corner
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


class CourtState(object):
    projections = None
    frame = None
    lock = Lock()
    model = None
    cap = None

    items = {CourtProperty.BALLS: list, CourtProperty.ROBOT: Robot, CourtProperty.VIP: Vip,
             CourtProperty.CORNERS: list, CourtProperty.OBSTACLE: Coordinate}

    @classmethod
    def initialize(cls):
        model = YOLO("../model/best.pt")
        cls.model = model
        cls.projections = Projection(Coordinate(1423.5, 905.5), 156.7)
        sleep(5.0)
        frame = None
        current_id = 0
        while frame is None:
            frame = cls.getFrame()

        results = model.predict(frame, conf=0.5)
        corners = {}
        boxes = results[0].boxes.cpu()

        for box in boxes:

            if results[0].names[box.cls.item()] == "corner":
                x, y, w, h = box.xyxy[0]
                x = int(x)
                y = int(y)
                w = int(w)
                h = int(h)
                corner = Corner(x, y, x + w, y + h, current_id)
                #corner.center = cls.projections.projection_from_coordinate(corner.center, 7.2)
                corners[current_id] = corner
                current_id += 1

        corners = set_placements(corners)

        cls.items[CourtProperty.CORNERS] = get_corners_as_list(corners)
        cls.analyse_results(results, frame)

        cv2.imshow("YOLO", results[0].plot())

    @classmethod
    def updateObjects(cls,drive_points):
        model = cls.model
        frame = None
        while frame is None:
            frame = cls.getFrame()
        results = model.predict(frame, conf=0.8)
        img = cls.analyse_results(results, frame)

        for drive_point in drive_points:
            img = cv2.circle(img,(int(drive_point.x), int(drive_point.y)),radius=5,color=(255,0,0),thickness=-1)
        robot = cls.getProperty(CourtProperty.ROBOT)
        img = cv2.circle(img, (int(robot.center.x), int(robot.center.y)), radius=5, color=(0, 255, 0), thickness=-1)
        img = cv2.circle(img, (int(robot.front.x), int(robot.front.y)), radius=5, color=(0, 0, 255), thickness=-1)


        cv2.imshow("YOLO",img)
        cv2.waitKey()

    @classmethod
    def analyse_results(cls, results, frame):
        boxes = results[0].boxes.cpu()
        projection = cls.projections
        balls = []
        corners = []
        robot = None
        vipItem = None
        robot_body = None
        robot_front = None
        obstacle = None
        for box in boxes:
            x, y, w, h = box.xyxy[0]
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)
            current_id = 0
            item = box.cls.item()
            frame = cv2.circle(frame, (x, y), radius=2, color=(255,255,255), thickness=1)

            if results[0].names[item] == "ball":
                balls.append(Ball(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id))
            elif results[0].names[item] == "r_front":
                #robot_front = Coordinate(x,y)
                robot_front = Coordinate(x + (w-x) / 2, y + (h-y)/2)
                robot_front = projection.projection_from_coordinate(target=robot_front, height=9.8)
            elif results[0].names[item] == "r_body":
                robot_body = Coordinate(x + (w-x) / 2, y + (h-y)/2)
                #robot_body = Coordinate(x,y)
                robot_body = projection.projection_from_coordinate(target=robot_body, height=22.5)
            elif results[0].names[item] == "corner":
                corner = Corner(x, y, w, h, current_id)
                #corner.center = projection.projection_from_coordinate(corner.center, 7.2)
                corners.append(corner)
            elif results[0].names[item] == "obstacle":
                x0, y0, x1, y1 = box.xyxy[0]
                obstacle = Rectangle(Coordinate(x0, y0), Coordinate(x1, y1))
            elif results[0].names[item] == "egg":
                print("Egg")
            elif results[0].names[item] == "orange_ball":
                vipItem = Vip(x, y, w, h, current_id)

        robot = Robot(robot_body, robot_front)

        cls.items[CourtProperty.VIP] = vipItem
        if robot is not None:
            cls.items[CourtProperty.ROBOT] = robot
        cls.items[CourtProperty.BALLS] = balls
        cls.items[CourtProperty.OBSTACLE] = obstacle

        return frame

    @classmethod
    def setupCam(cls):
        # cap = cv2.VideoCapture('videos/with_egg.mp4')
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
        width = 1920
        height = 1080
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
        while True:
            with cls.lock:
                ret = cls.cap.grab()

    @classmethod
    def getFrame(cls):
        with cls.lock:
            _, frame = cls.cap.retrieve()
        return frame
