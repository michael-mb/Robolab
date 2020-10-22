#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import paho.mqtt.client as mqtt
import time
from constant import constants
from planet import Planet, Direction


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    planet_Name = ''
    startX = -999
    startY = -999
    endX = -999
    endY = -999
    tX = -999
    tY = -999
    sDir = "N"
    eDir = ""
    pathStatus = "free"
    pathWeight = -999
    forced_Dir = False
    check_Running = True


    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THESE VARIABLES
        self.client = mqtt_client
        self.client.on_message = self.safe_on_message_handler
        self.logger = logger
        # Add your client setup here
        self.client.username_pw_set('208', password='zQW9xur2Mf')
        self.planet = Planet()
        self.connection_check()
        self.open_connection()

        #self.send_message(constants.sessionTopic, {"from": "client", "type": "testplanet", "payload": {"planetName": \
        #                                                                    self.planet_Name}})
        #self.send_message(constants.sessionTopic, {"from": "client", "type": "ready"})
        self.targetPosition = (-999 , -999)
        self.isTarget = False
        time.sleep(3)

        """
        while True:
            input('Press any Key to continue \n')
            break
        self.close_connection()
        """
    # Need to close the connection
    def close_connection(self):
        self.client.loop_stop()
        self.client.disconnect()

    # Need to establish the connection
    def open_connection(self):
        self.client.connect(constants.sessionBroker, port=1883)
        self.client.subscribe(constants.sessionTopic, qos=1)
        self.client.loop_start()

    # Just want it to look better
    def connection_check(self):
        #self.client.on_log = on_log
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect

    # Path status must be changed according to the Odometry
    # Send the Coordination we THINK we are at AFTER ARRIVING
    def send_current_position(self):
        self.send_message('planet/' + self.planet_Name + '/' + constants.sessionID, {"from": "client", "type": "path", \
    "payload": {"startX": self.startX, "startY": self.startY, "startDirection": self.sDir, "endX": self.endX, 'endY': \
        self.endY, "endDirection": self.eDir, "pathStatus": self.pathStatus}})
        print("Message sent to: ", 'planet/' + self.planet_Name + '/' + constants.sessionID )

    # Need to send the path we want to go BEFORE GOING
    def send_path_chosen(self):
        self.send_message('planet/' + self.planet_Name + '/' + constants.sessionID, {"from": "client",   \
        "type": "pathSelect",  "payload": {"startX": self.startX, "startY": self.startY, "startDirection": \
                self.sDir}})

    # Go from A(startX,startY) to go_to(endX,endY)
    # Only to be called after reaching the Point go_to
    # Call before send_current_position
    def point_reached(self, go_to, direction, status):
        self.endX = go_to[0]
        self.endY = go_to[1]
        self.eDir = direction
        self.pathStatus = status
        self.send_current_position()

    # Only to be called immediately after leaving the Point:
    # To be continuously called after the first Run before send_path_chosen
    def start_going(self, direction):
        self.startX = self.endX
        self.startY = self.endY
        # To be filled with the Exploring Strategy Method
        self.sDir = direction
        self.send_path_chosen()

    """ 
        (GOING) => Reached First Point => point_reached => send_current_position (STOP)
        => start_going => send_path_chosen (GOING) => Reached Second Point usw...
    """

    # Need to end the exploration?
    # If target reached
    def target_reached_explore(self):
        self.send_message(constants.sessionTopic, {"from": "client", "type": "targetReached", "payload": \
                {"message": "Target Reached"}})
        self.isTarget = False


    # If the map is completed, send the message and finish exploring
    def map_completed_explore(self):
        self.send_message(constants.sessionTopic, {"from": "client","type": "explorationCompleted","payload": {\
         "message": "Exploration Completed"}})
        self.check_Running = False

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))
        # YOUR CODE FOLLOWS (remove pass, please!)

        if payload['from'] == 'client':
            print('Message sent: ', payload)

        if payload['from'] == 'debug':
            print('Message received from debug: ', payload)

        if payload['from'] == 'server':
            print('Message received from server: ', payload)
            if payload['type'] == 'planet':
                self.client.unsubscribe(constants.sessionTopic)
                self.planet_Name = payload['payload']['planetName']
                self.client.subscribe([(constants.sessionTopic, 1), ('planet/'+self.planet_Name+'/208', 1)])
                self.startX = payload['payload']['startX']
                self.startY = payload['payload']['startY']
                self.planet.my_planet[(self.startX, self.startY)]= {}
                """ 
            elif payload['type'] == 'debug':
                print('Message from debug: ', payload)
                """

            elif payload['type'] == 'path':
                self.endX = payload['payload']['endX']
                self.endY = payload['payload']['endY']
                self.sDir = payload['payload']['startDirection']
                self.eDir = payload['payload']['endDirection']
                self.pathStatus = payload['payload']['pathStatus']
                self.pathWeight = payload['payload']['pathWeight']
                #Server Confirms the PATH => PATH MUST BE ADDED
                self.planet.add_path(((payload['payload']['startX'], payload['payload']['startY']), \
                                    Direction(payload['payload']['startDirection'])), ((payload['payload']['endX'], \
                        payload['payload']['endY']), Direction(payload['payload']['endDirection'])),
                                     payload['payload']['pathWeight'])
            elif payload['type'] == 'pathUnveiled':
                self.planet.add_path(((payload['payload']['startX'], payload['payload']['startY']), \
                                      Direction(payload['payload']['startDirection'])), ((payload['payload']['endX'], \
                payload['payload']['endY']), Direction(payload['payload']['endDirection'])), payload['payload']['pathWeight'])

                if (payload['payload']['startX'], payload['payload']['startY']) not in self.planet.nodes_from_server:
                    self.planet.nodes_from_server.append((payload['payload']['startX'], payload['payload']['startY']))
                if (payload['payload']['endX'], payload['payload']['endY']) not in self.planet.nodes_from_server:
                    self.planet.nodes_from_server.append((payload['payload']['endX'], payload['payload']['endY']))

            elif payload['type'] == 'pathSelect':
                if payload['payload']['startDirection'] != self.sDir:
                    self.sDir = payload['payload']['startDirection']
                    self.forced_Dir = True
            elif payload['type'] == 'target':
                self.tX = payload['payload']['targetX']
                self.tY = payload['payload']['targetY']
                self.isTarget = True
                self.targetPosition = (self.tX,self.tY)
                #self.planet.shortest_path((self.startX, self.startY), (self.tX, self.tY))
            elif payload['type'] == 'done':
                self.check_Running = False

    def return_check_Running(self):
        return self.check_Running

    def get_bool_direction(self):
        return self.forced_Dir

    # To be called immediately after receiving a forced Direction from Server
    def get_direction(self):
        return self.sDir

    # To be called immediately AFTER get_direction
    def reset_Position(self):
        self.forced_Dir = False

    def get_start_position(self):
        return self.startX, self.startY

    def check_Correct(self, to_check, startD, endD):
        if to_check[0] == self.endX and to_check[1] == self.endY and startD == self.sDir and endD == self.eDir:
            return True, self.endX, self.endY, self.eDir
        return False, self.endX, self.endY, self.eDir

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))
        # YOUR CODE FOLLOWS (remove pass, please!)
        self.client.publish(topic, json.dumps(message))

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise

    def send_first_message(self):
        self.send_message(constants.sessionTopic, {"from": "client", "type": "ready"})

# Need to know the logging
def on_log(client, data, level, buf):
    print("log: ", buf)


# Need to know if the connection is established
def on_connect(client, data, flags, rc):
    if rc == 0:
        print("connect OK")
    else:
        print("Bad connection returned", rc)


# Need to know if it's disconnected
def on_disconnect(client, data, flags, rc=0):
    print("Disconnected " + str(rc))
