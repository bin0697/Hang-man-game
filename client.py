import socket
import os
import sys
import thread
import time
import json
import re

server_ip = "localhost"
server_port = 5020
username = raw_input ("Enter username: ")
turn = -1
appe = 0
mess = ''
score = 0

color = 0
allow_color = True

try:
    color = sys.argv[4]
    if color == "--nocolor":
        allow_color = False
        color = "0"
except: pass

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_messages():
    global sock, username, color, mess, turn, appe, score, game
    while True:
        data = None
        try:
            data, addr = sock.recvfrom(1024, socket.MSG_DONTWAIT)
        except socket.error:
            time.sleep(0.01)
        
        if data:
            try:
                message = json.loads(data)
                if (message['message'] != mess):
                    words=zip(mess,message['message'])
                    incorrect=len([c for c,d in words if c!=d])
                    #print incorrect
                    if (message['username'] == username):
                        #mess = message['message']
                        score += 100*incorrect
                        print "score: ", score
                        
                    
                    elif (message['username'] == "init"):
                        mess = message['message']
                        has_underscore = re.findall(r'_', mess)
                        turn = len(has_underscore)
                        print "You have ", turn, " turn"

                    if (mess != ''):
                        mess = message['message']
                elif(message['message'] == mess):
                    if(message['username'] == username):
                        turn = turn - 1
                        print "wrong, turn remaining: ", turn
                        time.sleep(5)


                print message['username'], ": " ,message['message']


                if (message['message'] == username + " get the bonus point"):
                        score += 500
                        print "score: ", score

                if (message['message'] == "Game over"):
                        message = { "username" : username, "message" : "the score", "score" : score }
                        sock.sendto( json.dumps(message), (server_ip, int(server_port)) )

                '''
                elif (message['message'].endswith("win the game")):
                    message = { "username" : username, "message" : "/goodbye", "color" : color  }
                    sock.sendto( json.dumps(message), (server_ip, int(server_port)) )
                    sys.exit(0)
                '''

                
                '''
                if(message['username']):
                    msg_str = message['username'] + ": " + message['message']
                    
                if len(message['message']) > 0:
                    if allow_color:
                        print "\033[%sm%s\033[0m" % (message['color'], msg_str)
                '''

            except ValueError:
                print "error: tried to decode something invald"
                
def get_input():
    global sock, username, color
    try:
        while True and turn != 0:
            message = { "username" : username, "message" : raw_input().strip(), "color" : color  }
            sock.sendto( json.dumps(message), (server_ip, int(server_port)) )
    except KeyboardInterrupt:
        print "byebye now"

thread.start_new_thread(get_input, ())
thread.start_new_thread(get_messages, ())

message = { "username" : username, "message" : "/hello", "color" : color  }
sock.sendto( json.dumps(message), (server_ip, int(server_port)) )
message = { "username" : username, "message" : "/who", "color" : color  }
sock.sendto( json.dumps(message), (server_ip, int(server_port)) )
try: 
    while 1:
        time.sleep(0.01)
except KeyboardInterrupt:
    print "bye"
    message = { "username" : username, "message" : "/goodbye", "color" : color  }
    sock.sendto( json.dumps(message), (server_ip, int(server_port)) )
    sys.exit(0)