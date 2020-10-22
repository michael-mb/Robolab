import ev3dev.ev3 as ev3
import time
from constant import constants
from equipment import Equipment
from odometry import Odometry
from planet import Direction


class Action:

    def __init__(self):
        """
        Initialize all variables
        """
        self.integral = 0  # integral value
        self.derivative = 0  # derivative value
        self.error = 0
        self.lastError = 0

        self.optimalColorIntensity = 174
        self.nodeColor = 0
        self.colorIntensity = 0

        self.powerA = 0
        self.powerB = 0

        self.direction = constants.NORTH
        self.allDirection = []

    @staticmethod
    def average(myList):
        _int = Action.sum(myList) / len(myList)
        return _int

    @staticmethod
    def sum(myList):
        _int = 0
        for i in myList:
            _int = _int + i
        return _int

    """
    Calibration of the color
    """

    def calibration(self):
        white = []
        black = []

        while Equipment.touchSensor.value() == 0:
            print("Is messing white")
            white.append(Equipment.getBrightness())
            print(white)
            time.sleep(3)

        print("white ok")
        time.sleep(5)

        while Equipment.touchSensor.value() == 0:
            print("Is messing black")
            black.append(Equipment.getBrightness())
            print(black)
            time.sleep(3)

        print("black ok")

        whiteColor = Action.average(white)
        blackColor = Action.average(black)

        print(whiteColor)
        print(blackColor)

        self.optimalColorIntensity = (whiteColor + blackColor) / 2
        print("Optimal value ok now start")
        print(self.optimalColorIntensity)
        time.sleep(5)

        """
        Goal: Write a function that helps to keep the robot on the black line
        """

    def lineFollowing(self):

        self.colorIntensity = Equipment.getBrightness()  # Calculate the average
        # Apply PID formula
        self.error = (self.colorIntensity - self.optimalColorIntensity)
        self.integral = self.integral + self.error
        self.derivative = self.error - self.lastError

        turn = (constants.kp * self.error + constants.ki * self.integral + self.derivative * constants.kd)

        self.powerA = constants.initialSpeed + turn
        self.powerB = constants.initialSpeed - turn

        # Limit power of motors
        if self.powerA >= 200:
            self.powerA = 199
        elif self.powerA <= -200:
            self.powerA = -199
        if self.powerB >= 200:
            self.powerB = 199
        elif self.powerB <= -200:
            self.powerB = -199

        Action.runTimed(self.powerA, self.powerB)
        self.lastError = self.error

    @staticmethod
    def runTimed(MASpeed, MBSpeed):

        # runs both motors for a certain time
        Equipment.motorA.speed_sp = MASpeed
        Equipment.motorB.speed_sp = MBSpeed

        Equipment.motorA.command = "run-forever"
        Equipment.motorB.command = "run-forever"

    @staticmethod
    def stepOver(distance=7.35):
        Equipment.resetMotors()
        Equipment.stopMotors()
        Equipment.motorA.position_sp = 360 * distance / constants.wheelCircumferenceInCm
        Equipment.motorB.position_sp = 360 * distance / constants.wheelCircumferenceInCm
        Equipment.motorA.speed_sp = 100
        Equipment.motorB.speed_sp = 100
        Equipment.motorA.stop_action = "hold"
        Equipment.motorB.stop_action = "hold"
        Equipment.motorA.command = "run-to-rel-pos"
        Equipment.motorB.command = "run-to-rel-pos"
        time.sleep(0.5 + abs(Equipment.motorA.position_sp / Equipment.motorA.speed_sp))

    def turnAround(self, facingDirection):  # parameter

        path: int = 0
        i = 0
        Equipment.stopMotors()
        Equipment.resetMotors()
        Equipment.motorA.position_sp = 980
        Equipment.motorB.position_sp = -980
        position_start = Equipment.motorB.position
        print("FACING", facingDirection)
        while Equipment.motorA.position < 980 and Equipment.motorB.position > -980:
            Equipment.motorA.speed_sp = 85
            Equipment.motorB.speed_sp = -85
            Equipment.motorA.command = "run-to-rel-pos"
            Equipment.motorB.command = "run-to-rel-pos"

            self.colorIntensity = Equipment.getBrightness()

            if self.colorIntensity < 70:
                time.sleep(0.4)
                position_end = Equipment.motorB.position
                angle = (position_end - position_start) * constants.wheelDiameterInCm / constants.wheelGap

                print("WINKEL", angle)
                self.allDirection.append(Equipment.getOrientation(facingDirection, angle))

        Equipment.stopMotors()
        Equipment.resetMotors()

        return 0

    def pathDetection(self, facingDirection):
        turn_amount = self.turnAround(facingDirection)
        return turn_amount

    def turnLeft(self, degrees=88):

        #self.stepOver(1.0)

        Equipment.stopMotors()
        Equipment.resetMotors()

        Equipment.motorA.position_sp = degrees * constants.wheelGap / constants.wheelDiameterInCm
        Equipment.motorB.position_sp = - degrees * constants.wheelGap / constants.wheelDiameterInCm
        position_start = Equipment.motorB.position
        position_end = position_start

        while Equipment.motorA.position < Equipment.motorA.position_sp and \
                Equipment.motorB.position > Equipment.motorB.position_sp:
            Equipment.motorA.speed_sp = -100
            Equipment.motorB.speed_sp = 100
            Equipment.motorA.command = "run-to-rel-pos"
            Equipment.motorB.command = "run-to-rel-pos"
        position_end = Equipment.motorB.position
        Equipment.stopMotors()
        Equipment.resetMotors()

        return degrees

    def turnRight(self, degrees=90):

        #self.stepOver(-1.0)

        Equipment.stopMotors()
        Equipment.resetMotors()

        Equipment.motorA.position_sp = - degrees * constants.wheelGap / constants.wheelDiameterInCm
        Equipment.motorB.position_sp = degrees * constants.wheelGap / constants.wheelDiameterInCm
        position_start = Equipment.motorB.position
        position_end = position_start

        while Equipment.motorA.position > Equipment.motorA.position_sp and \
                Equipment.motorB.position < Equipment.motorB.position_sp:
            Equipment.motorA.speed_sp = -100
            Equipment.motorB.speed_sp = 100
            Equipment.motorA.command = "run-to-rel-pos"
            Equipment.motorB.command = "run-to-rel-pos"

        position_end = Equipment.motorB.position
        Equipment.stopMotors()
        Equipment.resetMotors()

        return -degrees

    def turnBack(self):

        Equipment.stopMotors()
        Equipment.resetMotors()

        Equipment.motorA.position_sp = 445
        Equipment.motorB.position_sp = -445
        position_start = Equipment.motorB.position
        position_end = position_start

        while Equipment.motorA.position < 445 and Equipment.motorB.position > -445:
            Equipment.motorA.speed_sp = 100
            Equipment.motorB.speed_sp = -100
            Equipment.motorA.command = "run-to-rel-pos"
            Equipment.motorB.command = "run-to-rel-pos"

        position_end = Equipment.motorB.position
        Equipment.stopMotors()
        Equipment.resetMotors()
        return 180

    def chooseDirection(self):
        stop = False
        Equipment.stopMotors()
        Equipment.resetMotors()

        Equipment.motorA.position_sp = 980
        Equipment.motorB.position_sp = -980
        position_start = Equipment.motorB.position
        position_end = position_start

        while Equipment.motorA.position < 980 and Equipment.motorB.position > -980 and not stop:
            Equipment.motorA.speed_sp = 100
            Equipment.motorB.speed_sp = -100
            Equipment.motorA.command = "run-to-rel-pos"
            Equipment.motorB.command = "run-to-rel-pos"

            self.colorIntensity = Equipment.getBrightness()

            if self.colorIntensity < 70:
                position_end = Equipment.motorB.position
                stop = True

        Equipment.stopMotors()
        Equipment.resetMotors()
        return (position_end - position_start) * constants.wheelDiameterInCm / constants.wheelGap

    def resetError(self):
        self.error = 0
        self.error = 0
        self.integral = 0
        self.derivative = 0
        turn = 0
        self.powerA = constants.initialSpeed + turn
        self.powerB = constants.initialSpeed - turn
        self.lastError = 0

    def resetDirection(self):
        self.allDirection = []

    def chooseNewDirection(self, direction, newDirection):

        if direction == 'N':
            if newDirection == 'E':
                return self.turnRight()
            if newDirection == 'W':
                return self.turnLeft()
            if newDirection == 'S':
                return self.turnBack()
            else:
                return 0

        if direction == 'S':
            if newDirection == 'W':
                return self.turnRight()
            if newDirection == 'E':
                return self.turnLeft()
            if newDirection == 'N':
                return self.turnBack()
            else:
                return 0

        if direction == 'E':
            if newDirection == 'S':
                return self.turnRight()
            if newDirection == 'N':
                return self.turnLeft()
            if newDirection == 'W':
                return self.turnBack()
            else:
                return 0
        if direction == 'W':
            if newDirection == 'S':
                return self.turnLeft()
            if newDirection == 'N':
                return self.turnRight()
            if newDirection == 'E':
                return self.turnBack()
            else:
                return 0
