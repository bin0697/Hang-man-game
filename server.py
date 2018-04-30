import socket
import time
import sys
import json
import time
import random
import re

UDP_IP= "localhost"
UDP_PORT=5020
guesses = ''
game = 0
my_dict = {}
rand_line = random.choice(open('words.txt').readlines())

reg = re.compile('(.+)(\t)(.+)')
if reg.search(rand_line):
    word = reg.search(rand_line).group(1)
    desc = reg.search(rand_line).group(3)

print('Description: ' + desc)

sock = socket.socket( socket.AF_INET, 
                      socket.SOCK_DGRAM )

sock.bind( (UDP_IP,UDP_PORT) )

clients = []

def broadcast(data):
  global clients
  for client in clients:
    sock.sendto(data, client[1])

while True:
    data = None
    message = None
    # make a counter that starts with zero 
    try:
      
      data, addr = sock.recvfrom( 1024, socket.MSG_DONTWAIT ) 

      message = json.loads(data)
      client = (message['username'], addr)
      if client not in clients:
        clients.append(client)
      
    except socket.error:

      time.sleep(0.01)

    if data:           
      print data
      try: 

        if( message['message'].startswith("/hello") ):

          outjson = {"username" : "server",\
            "message" : message['username'] + " joined the chat",\
            "color" : 35 } 
          broadcast( json.dumps(outjson) )

          if (game == 0):

            outjson = {"username" : "server",\
              "message" : "type start to begin ",\
              "color" : 35 } 
            broadcast( json.dumps(outjson) )

          elif (game == 1):

            outjson = {"username" : message['username'],\
              "message" : "game in process, plz wait ",\
              "color" : 35 } 
            broadcast( json.dumps(outjson) )

        elif ( message['message'].startswith("/who") ):

          outjson = {"username" : "server",\
            "message" : "people in room: " + ', '.join([y[0] for y in clients]),\
            "color" : 35 } 

          sock.sendto( json.dumps(outjson), client[1] )

        elif ( message['message'].startswith("/goodbye") ):

          outjson = {"username" : "server",\
            "message" : message['username'] + " left the chat",\
            "color" : 35 } 

          clients.remove(client)

          broadcast( json.dumps(outjson) )

        elif ( message['message'].startswith("/me") ):

          newmsg = message['username'] + message['message'][3:]
          outjson = {"username" : None,\
            "message" : newmsg,\
            "color" : message['color'] } 

          broadcast( json.dumps(outjson) )

        elif ( message['message'] == "the scroce" ):
          my_dict[message['username']] = message['scroce']

          print(my_dict)
          game += 1
          print game
          if (game == len(clients)+1):
            print "ok"
            mas = max(my_dict.keys(), key=lambda x: my_dict[x])
            print mas
            #print [k for (k, v) in my_dict.items() if v == mas][0]
            win = mas + " win the game"
            outjson = {"username" : "server",\
              "message" : win }
            broadcast( json.dumps(outjson) )


  
        elif (message['message'] == "start" and game == 0):
          game = 1
          ans = ''
          for char in word: 
            if char == " ":
                   ans = ans + "  "
            elif char.lower() not in guesses and char != " ":
              # if not found, print a dash
                   ans = ans + " _" 

          outjson = {"username" : "server",\
            "message" : desc,\
            "color" : message['color'] }
          broadcast( json.dumps(outjson) )

          outjson = {"username" : "init",\
            "message" : ans,\
            "color" : message['color'] }
          broadcast( json.dumps(outjson) )

        elif (len(message['message']) == 1):
          guesses = guesses + message['message']
          ans = ''
          # for every character in secret_word    
          for char in word:      
          # see if the character is in the players guess
              if char.lower() in guesses:    
          
              # print then out the character
                   ans = ans + " " + char 

              if char == " ":
                   ans = ans + "  "
              elif char.lower() not in guesses and char != " ":
              # if not found, print a dash
                   ans = ans + " _"  

          has_underscore = re.findall(r' _', ans)  

          outjson = {"username" : message['username'],\
            "message" : ans,\
            "color" : message['color'] } 
          broadcast( json.dumps(outjson) )

          if (len(has_underscore) == 0):

            bonus = message['username'] + " get the bonus point"
            outjson = {"username" : "server",\
            "message" : bonus,\
            "color" : message['color'] } 
            broadcast( json.dumps(outjson) )

            outjson = {"username" : "server",\
            "message" : "Game over",\
            "color" : message['color'] } 
            broadcast( json.dumps(outjson) )

        
        print clients

      except ValueError:

        print "indecipherable json"