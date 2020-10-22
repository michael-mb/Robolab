import ev3dev.ev3 as ev3
from constant import constants
from planet import Direction
import time


class Equipment:
    motorA = ev3.LargeMotor("outA")  # Erste Motor
    motorB = ev3.LargeMotor("outB")  # Zweite Motor
    colorSensor = ev3.ColorSensor("in1")
    touchSensor = ev3.TouchSensor("in3")
    usSensor = ev3.UltrasonicSensor("in2")
    lastColor = 0
    currentColor = 0

    @staticmethod
    def initEquipment():
        # sets initial part-configurations

        Equipment.colorSensor.mode = 'RGB-RAW'
        Equipment.usSensor.mode = 'US-DIST-CM'
        time.sleep(2)

        print('Initialized Parts')

    @staticmethod
    def getBrightness():
        # returns "pseudo-brightness"
        color = Equipment.getRGBValues()

        return (color[0] + color[1] + color[2]) / 3

    @staticmethod
    def getRGBValues():
        # returns tuple with RGB-Values
        return Equipment.colorSensor.bin_data('hhh')

    @staticmethod
    def resetMotors():
        Equipment.motorA.reset()
        Equipment.motorB.reset()

    @staticmethod
    def stopMotors():
        Equipment.motorA.position_sp = 0
        Equipment.motorB.position_sp = 0
        Equipment.motorA.speed_sp = 0
        Equipment.motorB.speed_sp = 0
        Equipment.motorA.stop()
        Equipment.motorB.stop()

    @staticmethod
    def reachedPoint():
        # returns True if a point has been reached, else False
        red = Equipment.colorSensor.value(0)
        blue = Equipment.colorSensor.value(2)
        if (red > (2 * blue) - 30 and red > 160):
            Equipment.lastColour = Equipment.currentColor
            Equipment.currentColour = 1
            return True
        elif (blue > 2 * red and blue > 100):
            Equipment.lastColour = Equipment.currentColor
            Equipment.currentColour = 0
            return True

        return False

    @staticmethod
    def reachedPoint2():
        # returns True if a point has been reached, else False
        color = Equipment.getRGBValues()
        optimalColor = (color[0] + color[1] + color[2]) / 3  # Der Durchschnitt berechnen

        if color[0] > (color[1] + color[2]):
            print("red")
            return True
        if (color[0] < 55) and (color[1] > 115) and (color[2] > 125):
            print("blue")
            return True

        return False

    @staticmethod
    def obstacleDetected():
        # returns True if an obstacle has been detected, else False
        if Equipment.usSensor.distance_centimeters <= constants.minDectectionDistance:
            return True

        return False

    @staticmethod
    def getPositions():  # return a tuple with the  current positions of the motors (left,right)
        return Equipment.motorA.position, Equipment.motorB.position

    @staticmethod
    def getOrientation(direction , angle):
        #  return the current orientation of the robot
        roundAngle = abs(angle) % 360

        if direction == 'N':
            if 315 < roundAngle <= 0 or 0<= roundAngle < 45:
                return 'N'
            if 45 <= roundAngle <= 135:
                return 'W'
            if 135 < roundAngle <= 225:
                return 'S'
            if 225 < roundAngle <= 315:
                return 'E'

        if direction == 'S':
            if 315 < roundAngle <= 0 or 0<= roundAngle < 45:
                return 'S'
            if 45 <= roundAngle <= 135:
                return 'E'
            if 135 < roundAngle <= 225:
                return 'N'
            if 225 < roundAngle <= 315:
                return 'W'

        if direction == 'E':
            if 315 < roundAngle <= 0 or 0<= roundAngle < 45:
                return 'E'
            if 45 <= roundAngle <= 135:
                return 'N'
            if 135 < roundAngle <= 225:
                return 'W'
            if 225 < roundAngle <= 315:
                return 'S'

        if direction == 'W':
            if 315 < roundAngle <= 0 or 0<= roundAngle < 45:
                return 'W'
            if 45 <= roundAngle <= 135:
                return 'S'
            if 135 < roundAngle <= 225:
                return 'E'
            if 225 < roundAngle <= 315:
                return 'N'

    @staticmethod
    def getDirectionWithAngle(dir, angle):
        # return the update direction after a rotation
        if dir == 0:
            if 270 < angle <= 360 or 0 <= angle <= 15:
                return dir % 4
            if 15 <= angle <= 90:
                return (dir + 1) % 4
            if 90 < angle <= 180:
                return (dir + 2) % 4
            if 180 < angle <= 270:
                return (dir + 3) % 4

        if dir == 1:
            if 270 < angle <= 360 or 0 <= angle <= 15:
                return dir % 4
            if 15 <= angle <= 90:
                return (dir + 1) % 4
            if 90 < angle <= 180:
                return (dir + 2) % 4
            if 180 < angle <= 270:
                return (dir + 3) % 4

        if dir == 2:
            if 270 < angle <= 360 or 0 <= angle <= 15:
                return dir % 4
            if 15 <= angle <= 90:
                return (dir + 1) % 4
            if 90 < angle <= 180:
                return (dir + 2) % 4
            if 180 < angle <= 270:
                return (dir + 3) % 4

        if dir == 3:
            if 270 < angle <= 360 or 0 <= angle <= 15:
                return dir % 4
            if 15 <= angle <= 90:
                return (dir + 1) % 4
            if 90 < angle <= 180:
                return (dir + 2) % 4
            if 180 < angle <= 270:
                return (dir + 3) % 4

    @staticmethod
    def directionPlanet(list):
        # translated an enum position to be used by the planet
        newList = []
        for e in list:
            if e == 'N':
                newList.append(Direction.NORTH)
            elif e == 'E':
                newList.append(Direction.EAST)
            elif e == 'S':
                newList.append(Direction.SOUTH)
            else:
                newList.append(Direction.WEST)

        return newList

    @staticmethod
    def decodeDirectionPlanet(direction):
        # translated an planet position to be used by the actions and communication
        if direction is None:
            while direction is None:
                direction = input("direction was None, please insert a direction to use (N/E/S/W):")[0].upper()
                if direction != "D":
                    return direction
                exec(input('>>>'), globals(), locals())
                # Odometry ändern
                direction = None

        if direction == Direction.NORTH:
            return 'N'
        elif direction == Direction.EAST:
            return 'E'
        elif direction == Direction.SOUTH:
            return 'S'
        elif direction == Direction.WEST:
            return 'W'

    @staticmethod
    def translateFromPathToServer(currentPosition, list):
        newList = []
        for e in list:
            newList.append((currentPosition, e))

        return newList
