# !/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from math import pi, sin, cos, degrees, radians
from constant import constants
from equipment import Equipment


class Odometry:
    lastMotorPosition = (0, 0)
    dR = []
    dL = []
    newCoordinate = (0, 0)
    currentCoordinate = (0, 0)
    angleTotal = 0

    @staticmethod
    def initStartingOrientation():

        Odometry.lastMotorPosition = Equipment.getPositions()

    @staticmethod
    def storeValues():  # stores motorpositions for later calculations
        positions = Equipment.getPositions()
        deltaA = positions[0] - Odometry.lastMotorPosition[0]
        deltaB = positions[1] - Odometry.lastMotorPosition[1]

        Odometry.dR.append(deltaA)
        Odometry.dL.append(deltaB)

        Odometry.lastMotorPosition = positions

    @staticmethod
    def calculateAngle(dr, dl):

        # calculate angle (alpha)
        alpha = (dr - dl) / constants.wheelGap

        return alpha

    @staticmethod
    def resetAll():  # reset all motorpositions

        Equipment.resetMotors()
        Odometry.lastMotorPosition = Equipment.getPositions()
        Odometry.dR = []
        Odometry.dL = []

    @staticmethod
    def calculateDistance(dr, dl, alpha):

        # calculate travelled distance
        if alpha == 0:
            return dr

        distance = ((dr + dl) / alpha) * sin(alpha / 2)
        return distance

    @staticmethod
    def calculateDeltaXY(exAlpha, beta, distance):  # calculate the change in coordinates

        deltaX = (sin(exAlpha + beta) * distance) * -1
        deltaY = cos(exAlpha + beta) * distance
        return deltaX, deltaY

    @staticmethod
    def calculateOdometryData():
        distanceTotal = 0
        deltaXYTotal = (0, 0)

        for i in range(len(Odometry.dR)):
            # convert motorpositions into rotations

            Odometry.dR[i] = Odometry.dR[i] * constants.wheelCircumferenceInCm / 360
            Odometry.dL[i] = Odometry.dL[i] * constants.wheelCircumferenceInCm / 360

            # calculations
            alpha = Odometry.calculateAngle(Odometry.dR[i], Odometry.dL[i])
            distance = Odometry.calculateDistance(Odometry.dR[i], Odometry.dL[i], alpha)
            deltaXY = Odometry.calculateDeltaXY(Odometry.angleTotal, alpha / 2, distance)

            distanceTotal += distance
            Odometry.angleTotal += alpha
            deltaXYTotal = (deltaXYTotal[0] + deltaXY[0], deltaXYTotal[1] + deltaXY[1])  # End Coordinaten
        distanceTotal = distanceTotal + constants.distanceTolerance
        Odometry.newCoordinate = Odometry.calculateCoodinate(deltaXYTotal)
        Odometry.currentCoordinate = ((Odometry.currentCoordinate[0] + Odometry.newCoordinate[0]),
                                      (Odometry.currentCoordinate[1] + Odometry.newCoordinate[1]))

        # print("Distance: ", distanceTotal)
        # print("AngleSum", Odometry.angleTotal * 180 / pi)
        # print("DeltaXYTOTAL", deltaXYTotal)
        # print("(X ,Y) new ", Odometry.newCoordinate)
        # print("(X ,Y) current", Odometry.currentCoordinate)
        # print("Distance",distanceTotal)

        return Odometry.currentCoordinate

    @staticmethod
    def calculateCoodinate(deltaXY):
        x = deltaXY[0]
        y = deltaXY[1]

        return round(x / 50), round(y / 50)

    """ 
    @staticmethod
    def calculateNewPosition(coordXY):
        orientation = Equipment.getOrientation()
        print(orientation)
        x = coordXY[0]
        y = coordXY[1]
        if orientation == 0:
            print("Nord")
            y = abs(coordXY[1])
        if orientation == 1:
            print("Est")
            x = abs(coordXY[0])
        if orientation == 2:
            print("Sud")
            y = - abs(coordXY[1])
        if orientation == 3:
            print("Ouest")
            x = - abs(coordXY[0])
        return x, y
    """

    @staticmethod
    def updateAngleTotal(orientation):
        # after each pass we update the angle with the orientation
        if orientation == 'N':
            Odometry.angleTotal = 0

        elif orientation == 'E':
            Odometry.angleTotal = -pi / 2
        elif orientation == 'S':
            Odometry.angleTotal = pi
        else:
            Odometry.angleTotal = pi / 2
        #print("Odometry set to angleTotal:",Odometry.angleTotal,"("+str(orientation)+")")

    @staticmethod
    def updatePositionFromServer(x, y):
        # Updated currentPosition with the position of the server
        Odometry.currentCoordinate = (x, y)

    @staticmethod
    def getOrientationServer():
        #  return the current orientation of the robot
        newAngle = -Odometry.angleTotal * 180 / pi
        if (315 < newAngle % 360 <= 360) or (0 <= newAngle % 360 <= 45):
            # print("N")
            return 'N'
        if 45 < newAngle % 360 <= 135:
            # print("E")
            return 'E'
        if 135 < newAngle % 360 <= 225:
            # print("S")
            return 'S'
        if 225 < newAngle % 360 <= 315:
            # print("W")
            return 'W'

    @staticmethod
    def getOppositeOrientationServer():
        #  return the opposite of current orientation of the robot
        newAngle = -Odometry.angleTotal * 180 / pi
        if (315 < newAngle % 360 <= 360) or (0 <= newAngle % 360 <= 45):
            # print("S")
            return 'S'
        if 45 < newAngle % 360 <= 135:
            # print("W")
            return 'W'
        if 135 < newAngle % 360 <= 225:
            # print("N")
            return 'N'
        if 225 < newAngle % 360 <= 315:
            # print("E")
            return 'E'

    @staticmethod
    def wrapAngle(angle):
        # Translate angle into String
        if (315 < angle % 360 <= 360) or (0 <= angle % 360 <= 45):
            # print("N")
            return 'N'
        if 45 < angle % 360 <= 135:
            # print("E")
            return 'E'
        if 135 < angle % 360 <= 225:
            # print("S")
            return 'S'
        if 225 < angle % 360 <= 315:
            # print("W")
            return 'W'

    @staticmethod
    def unwrapAngle(dir):
        # Translate String into angle
        if dir == 'N':
            return 0
        if dir == 'E':
            return 90
        if dir == 'S':
            return 180
        if dir == 'W':
            return 270

    # Decode and encode Method
    @staticmethod
    def decodeAngle(dir):
        if dir == 'N':
            return 0
        if dir == 'E':
            return 1
        if dir == 'S':
            return 2
        if dir == 'W':
            return 3

    @staticmethod
    def encodeAngle(dir):
        if dir == 0:
            return 'N'
        if dir == 1:
            return 'E'
        if dir == 2:
            return 'S'
        if dir == 3:
            return 'W'


    @staticmethod
    def invertDirection(dir):
        # invert the direction
        if dir == 'S':
            return 'N'
        if dir == 'W':
            return 'E'
        if dir == 'N':
            return 'S'
        if dir == 'E':
            return 'W'