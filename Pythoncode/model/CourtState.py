import threading
from time import sleep
from enum import Enum
from threading import Thread, Lock

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

    model = None
    cap = None
    thread = None
    lock = Lock()
    items = {CourtProperty.BALLS: list, CourtProperty.ROBOT: Robot, CourtProperty.VIP: Vip,
                  CourtProperty.CORNERS: list, CourtProperty.OBSTACLE: Coordinate}
    ready = False
    plot = None

    @classmethod
    def addProperties(cls, model, cap):
        CourtState.model = model
        CourtState.cap = cap

    @classmethod
    def startThread(cls):
        cls.thread = Thread(target=cls.updateObjects)
        cls.thread.start()

    @classmethod
    def initialize(cls):
        model = YOLO("model/best.pt")
        cls.model = model
        cv2.namedWindow("YOLO", cv2.WINDOW_NORMAL)

        # cap = cv2.VideoCapture('videos/with_egg.mp4')
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        cls.cap = cap

        ret, frame = cap.read()
        if ret:
            results = model.track(frame, persist=True)
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
            if robot_body is None or robot_front is None:
                print("Robot blev ikke fundet, indtast værdier selv")
                frame_ = results[0].plot()
                """frame2 = cv2.resize(frame_, (620, 480))"""
                height, width, channels = frame2.shape
                for x in range(0, width - 1, 20):
                    cv2.line(frame2, (x, 0), (x, height), (255, 0, 0), 1, 1)
                for y in range(0, height - 1, 20):
                    cv2.line(frame2, (0, y), (width, y), (255, 0, 0), 1, 1)
                cv2.imshow("YOLO", frame2)
                if robot_body is None:
                    print("Indtast center af robottens body (det store X). Først x, så y:")
                    robot_body = Coordinate(float(input()), float(input()))

                if robot_front is None:
                    print("Indtast center af robotten front (cirklen). Først x, så y:")
                    robot_front = Coordinate(float(input()), float(input()))

            robot = Robot(robot_body, robot_front)

            with cls.lock:
                cls.items[CourtProperty.VIP] = vipItem
                if robot is not None:
                    cls.items[CourtProperty.ROBOT] = robot
                cls.items[CourtProperty.BALLS] = balls
                cls.items[CourtProperty.CORNERS] = corners
                cls.ready = True
                cls.plot = results[0].plot()

    @classmethod
    def updateObjects(cls):
        model = cls.model
        cap = cls.cap

        while True:
            print("Updating models")
            ret, frame = cap.read()
            if ret:
                results = model.track(frame, persist=True)
                boxes = results[0].boxes.cpu()
                # track_ids = results[0].boxes.id.int().cpu().tolist()

                # Plot the tracks
                # for box, track_id in zip(boxes, track_ids):
                balls = []
                corners = {}
                robot = None
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
                try:
                    robot = Robot(robot_body, robot_front)
                except:
                    print("Robot blev ikke fundet")
                    robot = None
                with cls.lock:
                    cls.items[CourtProperty.VIP] = vipItem
                    if robot is not None:
                        cls.items[CourtProperty.ROBOT] = robot
                    cls.items[CourtProperty.BALLS] = balls
                    cls.items[CourtProperty.CORNERS] = corners
                    cls.ready = True
                    cls.plot = results[0].plot()



    @classmethod
    def getProperty(cls, property_name: CourtProperty):
        with cls.lock:
            item = cls.items[property_name]
        return item

