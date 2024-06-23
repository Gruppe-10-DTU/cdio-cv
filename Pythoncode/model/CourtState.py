import cv2
import numpy
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


class CourtState(object):
    projections = None
    frame = None
    lock = Lock()
    model = None
    cap = None

    items = {CourtProperty.BALLS: list, CourtProperty.ROBOT: Robot, CourtProperty.VIP: Vip,
             CourtProperty.CORNERS: list, CourtProperty.OBSTACLE: Coordinate}

    dist = None
    mtx = None

    @classmethod
    def initialize(cls):
        cls.mtx = numpy.loadtxt(
            'C:/Users/nts96/PycharmProjects/cdio-cv/Pythoncode/calibration/mtx.txt')
        cls.dist = numpy.loadtxt(
            'C:/Users/nts96/PycharmProjects/cdio-cv/Pythoncode/calibration/dist.txt')

        model = YOLO("../model/best.pt")
        cls.model = model
        cls.projections = Projection(Coordinate(1389.0, 830.5), 162.5)
        sleep(5.0)
        frame = None
        current_id = 0
        while frame is None:
            cls.cap.grab()
            _,frame = cls.cap.retrieve()


        results = model.predict(frame, conf=0.5)
        corners = {}
        boxes = results[0].boxes

        for box in boxes:

            if results[0].names[box.cls.item()] == "corner":
                x, y, w, h = box.xyxy[0]
                x = int(x)
                y = int(y)
                w = int(w)
                h = int(h)
                corner = Corner(x, y, w, h, current_id)
                #corner.center = cls.projections.projection_from_coordinate(corner.center, 7.2)
                corners[current_id] = corner
                current_id += 1

        corners = set_placements(corners)

        cls.items[CourtProperty.CORNERS] = get_corners_as_list(corners)
        cls.analyse_results(results, frame)

        cv2.imshow("YOLO", results[0].plot())

    @classmethod
    def updateObjects(cls,drive_points,target):
        model = cls.model
        frame = None
        robot = cls.getProperty(CourtProperty.ROBOT)

        while cls.frame is None:
            sleep(0.05)

        frame = cls.frame
        results = model.predict(frame, conf=0.5)
        frame = results[0].plot()
        if cv2.waitKey(3000) & 0xFF == ord('q'):
            return
        img = cls.analyse_results(results, frame)
        for drive_point in drive_points:
            img = cv2.circle(img,(int(drive_point.x), int(drive_point.y)),radius=5,color=(255,0,0),thickness=-1)
        #rbf = cv2.undistortImagePoints(numpy.array([[robot.front.x,robot.front.y]], dtype=numpy.float32), cls.mtx, cls.dist)
        #rbc = cv2.undistortImagePoints(numpy.array([[robot.center.x,robot.center.y]], dtype=numpy.float32), cls.mtx, cls.dist)

        #if target is not None:
        #    img = cv2.arrowedLine(img, (rbf.x, rbf.y), (target.center.x, target.center.y),
        #color=(255, 192, 203), thickness=-1)
        #img = cv2.circle(img, (int(rbc[0][0][0]), int(rbc[0][0][1])), radius=5, color=(0, 255, 0), thickness=-1)
        #img = cv2.circle(img, (int(rbf[0][0][0]), int(rbf[0][0][1])), radius=5, color=(0, 0, 255), thickness=-1)
        cv2.imshow("YOLO", img)
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
        egg = None
        robot_front = None
        obstacle = None
        for box in boxes:
            x, y, w, h = box.xywh[0]
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)

            current_id = 0

            item = box.cls.item()

            uc = cv2.undistortImagePoints(numpy.array([[x, y]], dtype=numpy.float32), cls.mtx,
                                          cls.dist)
            color = (0, 255, 255)
            if results[0].names[item] == "ball":
                color = (255, 255, 0)
            elif results[0].names[item] == "corner":
                color = (100, 190, 255)
            elif results[0].names[item] == "r_body":
                color = (0, 255, 0)
            elif results[0].names[item] == "r_front":
                color = (0, 0, 255)
            #frame = cv2.circle(frame, (int(uc[0][0][0]), int(uc[0][0][1])), radius=5, color=color, thickness=-1)

            if results[0].names[item] == "ball":
                x0, y0, x1, y1 = box.xyxy[0]
                balls.append(Ball(int(x0), int(y0), int(x1), int(y1), current_id))
            elif results[0].names[item] == "r_front":
                robot_front = Coordinate(x,y)
                #robot_front = Coordinate(x + (w-x) / 2, y + (h-y)/2)
                #robot_front = projection.projection_from_coordinate(target=robot_front, height=9.8)
            elif results[0].names[item] == "r_body":
                #robot_body = Coordinate(x + (w-x) / 2, y + (h-y)/2)
                robot_body = Coordinate(x,y)
                #robot_body = projection.projection_from_coordinate(target=robot_body, height=22.5)
            elif results[0].names[item] == "corner":
                x0, y0, x1, y1 = box.xyxy[0]
                corner = Corner(int(x0), int(y0), int(x1), int(y1), current_id)
                #corner.center = projection.projection_from_coordinate(corner.center, 7.2)
                corners.append(corner)
            elif results[0].names[item] == "obstacle":
                x0, y0, x1, y1 = box.xyxy[0]
                obstacle = Rectangle(Coordinate(int(x0), int(y0)), Coordinate(int(x1), int(y1)))
            elif results[0].names[item] == "egg":
                x0, y0, x1, y1 = box.xyxy[0]
                egg = Egg(int(x0), int(y0), int(x1), int(y1))
            elif results[0].names[item] == "orange_ball":
                x0, y0, x1, y1 = box.xyxy[0]
                vipItem = Vip(int(x0), int(y0), int(x1), int(y1), current_id)
        """"This is the true center of the robot post adjustment of top-hat."""
        true_c = Coordinate((robot_front.x + robot_body.x) / 2, (robot_front.y + robot_body.y) / 2)
        robot = Robot(true_c, robot_front)

        if obstacle is not None and egg is not None:
            egg.calculate_buffers(obstacle)

            uc = cv2.undistortImagePoints(numpy.array([[egg.buffer_center.x, egg.buffer_center.y]], dtype=numpy.float32), cls.mtx,
                                          cls.dist)
            color = (0, 255, 255)

            frame = cv2.circle(frame, (int(uc[0][0][0]), int(uc[0][0][1])), radius=5, color=color, thickness=-1)
            uc = cv2.undistortImagePoints(numpy.array([[egg.buffer_c2.x, egg.buffer_c2.y]], dtype=numpy.float32), cls.mtx,
                                          cls.dist)
            color = (255, 0, 0)
            frame = cv2.circle(frame, (int(uc[0][0][0]), int(uc[0][0][1])), radius=5, color=color, thickness=-1)
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
        # cap = cv2.VideoCapture('videos/with_egg.mp4')
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        width = 1280
        height = 720
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # turn the autofocus off
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
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
            with cls.lock:
                ret = cls.cap.grab()
                _,cls.frame = cls.cap.retrieve()
        print("ret: " + str(ret))



    @classmethod
    def getFrame(cls):
        #with cls.lock:
        ret = cls.cap.grab()
        _, frame = cls.cap.retrieve()
        return frame
