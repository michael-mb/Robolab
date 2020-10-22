#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging
import os
import paho.mqtt.client as mqtt
import uuid
from actions import Action
from equipment import Equipment

import time

from communication import Communication
from odometry import Odometry
from planet import Direction, Planet

client = None  # DO NOT EDIT


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client = mqtt.Client(client_id=str(uuid.uuid4()),  # Unique Client-ID to recognize our program
                         clean_session=False,  # We want to be remembered
                         protocol=mqtt.MQTTv31  # Define MQTT protocol version
                         )
    log_file = os.path.realpath(__file__) + '/../../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    Equipment.initEquipment()

    action = Action()
    com = Communication(client, logger)

    nextDirection = 'N'
    eDir = 'S'
    isObstacle = 'free'
    end = False
    firstRun = True
    exPosition = (0,0)
    if input("Calibrate? (y/n)").lower() == "y":
        action.calibration()


    while not end:


        if Equipment.reachedPoint():
            Equipment.stopMotors()
            #print("POINT REACHED !")
            if firstRun:
                com.send_first_message()
                # Update start point and end point
                time.sleep(1)  # waiting for server
                startPosition = com.get_start_position()
                Odometry.updatePositionFromServer(startPosition[0], startPosition[1])
                com.planet.my_planet[startPosition] = {}
                action.stepOver()
                facing_direction = Odometry.invertDirection(eDir)
                action.pathDetection(facing_direction)
                action.allDirection.remove(eDir)
                action.allDirection = Equipment.directionPlanet(action.allDirection)
                com.planet.add_no_visited_paths(startPosition,action.allDirection)
                #print('com.planet.get_node_with_undiscovered_paths()',com.planet.get_node_with_undiscovered_paths())
                #print('DIRECTION', com.planet.get_no_visited_paths_for_node(com.planet.get_node_with_undiscovered_paths()))
                nextDirection = com.planet.get_no_visited_paths_for_node(com.planet.get_node_with_undiscovered_paths())
                print('NextDirection--->', nextDirection)
                action.chooseNewDirection('N', nextDirection)
                action.resetDirection()
                firstRun = False
                com.planet.visited_nodes.append(startPosition)
            else:
                currentPosition = Odometry.calculateOdometryData()
                eDir = Odometry.getOppositeOrientationServer()
                action.stepOver()
                if isObstacle == 'blocked' :
                    currentPosition = exPosition
                    com.point_reached(currentPosition, nextDirection, isObstacle)

                else:
                    com.point_reached(currentPosition, eDir, isObstacle)

                time.sleep(1)
                checkTuple = com.check_Correct(currentPosition, nextDirection, eDir)
                currentPosition = checkTuple[1:3]

                eDir = checkTuple[3]
                facing_direction = Odometry.invertDirection(eDir)
                isObstacle = 'free'  # init obstacle
                target_reacheable= False
                if com.isTarget is True :
                    futurDirection = com.planet.shortest_path(currentPosition, com.targetPosition)
                    if futurDirection is None:
                        pass
                    elif not futurDirection:
                        pass
                    else:
                        target_reacheable = True
                        print("FuturDirection",futurDirection)
                        futurDirection = futurDirection[::-1]
                        nextDirection = futurDirection[-1][1]

                if currentPosition == com.targetPosition:
                    com.target_reached_explore()

                if not target_reacheable or nextDirection is None:
                    if currentPosition in com.planet.visited_nodes:

                        next_super_node = com.planet.get_node_with_undiscovered_paths()
                        print("NEXT SUPER NODE ", next_super_node)
                        if next_super_node is not None:
                            if next_super_node == currentPosition:
                                #com.planet.no_visited_paths[currentPosition] = None
                                # print("com.planet.no_visited_paths[currentPosition] = None",com.planet.no_visited_paths[currentPosition])
                                next_super_node = com.planet.get_node_with_undiscovered_paths()
                                # print("new next_super_node :",next_super_node)
                                #nextDirection = com.planet.get_node_with_undiscovered_paths()[currentPosition][0]
                                nextDirection = com.planet.get_no_visited_paths_for_node(currentPosition)[-1]
                            else:
                                #nextDirection = com.planet.shortest_path(currentPosition, next_super_node)
                                futurDirection = com.planet.shortest_path(currentPosition, next_super_node)
                                futurDirection = futurDirection[::-1]
                                nextDirection = futurDirection[-1][1]
                        else:
                            print('Ganze Planete erkunden !!')
                            com.map_completed_explore()
                            time.sleep(2)
                            end = True
                    else:
                        action.pathDetection(facing_direction)
                        action.allDirection.remove(eDir)
                        action.allDirection = Equipment.directionPlanet(action.allDirection)
                        com.planet.add_no_visited_paths(currentPosition, action.allDirection)

                        for direction in com.planet.my_planet[currentPosition]:
                            if com.planet.my_planet[currentPosition][direction][2] == -1 :
                                com.planet.remove_no_visited_path(currentPosition,direction)

                        if not com.planet.get_no_visited_paths_for_node(com.planet.get_node_with_undiscovered_paths()):
                            if com.planet.get_next_unvisited_node() is None:
                                print('Ganze Planete erkunden !!')
                                com.map_completed_explore()
                                time.sleep(2)
                                break
                            else:
                                toGo = com.planet.get_next_unvisited_node()
                                #print("TOGO",toGo)
                                #nextDirection = com.planet.shortest_path(currentPosition,toGo)
                                futurDirection = com.planet.shortest_path(currentPosition, toGo)
                                if futurDirection is None:
                                    com.map_completed_explore()
                                    break
                                futurDirection = futurDirection[::-1]
                                nextDirection = futurDirection[-1][1]
                        else:
                            nextDirection = com.planet.get_no_visited_paths_for_node(com.planet.get_node_with_undiscovered_paths())[0]
                       # print("NextDirection (no_visited_paths_for_node)",nextDirection)

               # print("NextDirection (pre-decode)",nextDirection,type(nextDirection))
                nextDirection = Equipment.decodeDirectionPlanet(nextDirection)
                action.chooseNewDirection(currentPosition, nextDirection)
                print("Result of nextDirection: ", nextDirection)
                if nextDirection is None:
                    print('Ganze Planete erkunden !!')
                    com.map_completed_explore()
                    time.sleep(2)
                    break
                com.start_going(nextDirection)
                time.sleep(2)

                if com.get_bool_direction():
                    nextDirection = com.get_direction()

                # input("Waiting with next direction: "+str(facing_direction)+" --> "+str(nextDirection))
                action.chooseNewDirection(facing_direction, nextDirection)
                Odometry.updateAngleTotal(nextDirection)
                Odometry.resetAll()
                action.resetDirection()
                action.resetError()
                com.planet.visited_nodes.append(currentPosition)
                com.planet.remove_no_visited_path(currentPosition,nextDirection)
                exPosition = currentPosition
                Odometry.updatePositionFromServer(*currentPosition)
            print("VISITED NODE",com.planet.visited_nodes)
            #end = not com.check_Running

        elif Equipment.obstacleDetected():
            action.turnBack()
            isObstacle = 'blocked'

        else:
            action.lineFollowing()
            if not firstRun:
                Odometry.storeValues()
        # DO NOT EDIT


if __name__ == '__main__':
    run()
