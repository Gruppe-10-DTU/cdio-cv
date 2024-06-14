import threading
from enum import Enum
import uuid
from threading import Lock
from time import sleep
import cv2
from ultralytics import YOLO

from Pythoncode.model.Ball import Ball
from Pythoncode.model.Corner import Corner
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

        sleep(5.0)
        frame = None
        while frame is None:
            frame = cls.getFrame()
        results = model.track(frame, persist=True, conf=0.8)
        boxes = results[0].boxes.cpu()
        # track_ids = results[0].boxes.id.int().cpu().tolist()

        # Plot the tracks
        # for box, track_id in zip(boxes, track_ids):
        balls = []
        corners = {}
        robot = None
        vipItem = None
        robot_body = None
        robot_front = None

        for box in boxes:
            if results[0].names[box.cls.item()] == "ball":
                x, y, w, h = box.xywh[0]
                current_id = int(box.id)
                balls.append(Ball(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id))
            elif results[0].names[box.cls.item()] == "robot_front":
                x, y, w, h = box.xywh[0]
                robot_front = Coordinate(int(x), int(y))
            elif results[0].names[box.cls.item()] == "robot_body":
                x, y, w, h = box.xywh[0]
                robot_body = Coordinate(int(x), int(y))
            elif results[0].names[box.cls.item()] == "corner":
                x, y, w, h = box.xywh[0]
                current_id = int(box.id)
                corners[current_id] = Corner(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)
            elif results[0].names[box.cls.item()] == "obstacle":
                print("Cross")
            elif results[0].names[box.cls.item()] == "egg":
                print("Egg")
            elif results[0].names[box.cls.item()] == "orange_ball":
                x, y, w, h = box.xywh[0]
                current_id = int(box.id)
                vipItem = Vip(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)

        robot = Robot(robot_body, robot_front)

        cls.items[CourtProperty.VIP] = vipItem
        if robot is not None:
            cls.items[CourtProperty.ROBOT] = robot
        cls.items[CourtProperty.BALLS] = balls
        cls.items[CourtProperty.CORNERS] = corners

    @classmethod
    def setupCam(cls):
        # cap = cv2.VideoCapture('videos/with_egg.mp4')
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        width = 1920
        height = 1080
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # turn the autofocus off
        cls.cap = cap

        thread = threading.Thread(target=cls.frameThread)
        thread.start()

    @classmethod
    def updateObjects(cls):
        model = cls.model
        frame = None
        while frame is None:
            frame = cls.getFrame()
        results = model.track(frame, persist=True, conf=0.8)
        boxes = results[0].boxes.cpu()
        # track_ids = results[0].boxes.id.int().cpu().tolist()

        # Plot the tracks
        # for box, track_id in zip(boxes, track_ids):
        balls = []
        corners = {}
        robot = None
        robot_body = None
        robot_front = None
        vipItem = None
        for box in boxes:
            current_id = int(box.id)

            if results[0].names[box.cls.item()] == "ball":
                x, y, w, h = box.xywh[0]
                balls.append(Ball(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id))
            elif results[0].names[box.cls.item()] == "robot_front":
                x, y, w, h = box.xywh[0]
                robot_front = Coordinate(int(x), int(y))
            elif results[0].names[box.cls.item()] == "robot_body":
                x, y, w, h = box.xywh[0]
                robot_body = Coordinate(int(x), int(y))
            elif results[0].names[box.cls.item()] == "corner":
                x, y, w, h = box.xywh[0]
                corners[current_id] = Corner(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)
            elif results[0].names[box.cls.item()] == "obstacle":
                print("Cross")
            elif results[0].names[box.cls.item()] == "egg":
                print("Egg")
            elif results[0].names[box.cls.item()] == "orange_ball":
                x, y, w, h = box.xywh[0]
                vipItem = Vip(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)

        if robot_body is None or robot_front is None:
            print("robot not found!")
            raise Exception('Robot not found')

        cls.items[CourtProperty.VIP] = vipItem
        if robot is not None:
            cls.items[CourtProperty.ROBOT] = robot
        cls.items[CourtProperty.BALLS] = balls
        cls.items[CourtProperty.CORNERS] = corners
        cv2.imshow("YOLO", results[0].plot())


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
