from math import pi


class constants:
    # lineFollower

    kp = 0.7  # Proportionale Koefficient
    ki = 0.13  # Integrative Koefficient
    kd = 0.001  # Derivative Koefficient
    initialSpeed = 165  # initiale geschwindigkeit
    minDectectionDistance = 22
    followTime = 0

    # odometry

    wheelDiameterInCm = 5.6
    wheelGap = 14.85
    wheelCircumferenceInCm = wheelDiameterInCm * pi
    distanceBetweenNodes = 500
    distanceTolerance = 6

    # direction

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    # commucation

    sessionTopic = 'explorer/208'
    sessionID = '208'
    sessionBroker = 'mothership.inf.tu-dresden.de'
