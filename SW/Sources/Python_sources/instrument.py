"""
#TWIST Software

Copyright (c) 2018: Andrea Carloni, Roberto Di Rienzo, Roberto Roncella, Federico Baronti, Roberto Saletti, 
					Dipartimento di Ingegneria dell'Informazione (DII), Università di Pisa, ITALY.

All rights reserved.

**GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007**


 This file is part of TWIST-software.

    TWIST-software is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    TWIST-software is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TWIST-software.  If not, see <https://www.gnu.org/licenses/>.
"""
#--------------------- BULT-IN Python modules-------------------#
import sys
import socket
import rele as re
import time

#----------------------- Setting Charge ----------------------------
#setCharge() function opens a connective socket to the charger and sets the current and the dropout voltage on it.
#Prototype: setCharge(ip,port,testCurrent,limitVoltage)
#-----Args---------#
#   ip              -> it is the string that contains the charger's ip address
#   port            -> it is the string that contains the charger's port number 
#   testCurrent     -> it is the current amplitude by which the test are conducting
#   limitVoltage    -> it is the dropout voltage by which the test are conducting
#-----Return-------#
#   sockSupp        -> it is the connective socket to charger

def setCharge(ip,port,testCurrent,limitVoltage):

    #------------- Open Socket Phase ----------------------#
    sockSupp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockSupp.settimeout(10)
    chargerAddress = (ip,int(port))
    try:
        sockSupp.connect(chargerAddress)
    except socket.timeout:
        print('initCahrger -> Error num: 001')
        sys.exit(1);
    except ConnectionRefusedError:
        print('initCharger -> Error num: 002')
        sys.exit(1)
    except OSError:
        print('initCharger -> Error num: 002')
        sys.exit(1)

    sockSupp.settimeout(1)

    #------------ Setting charger phase ------------------#
    try:
        message = 'OP1?\n'                                      #it asks to charger how is its output state.
        sockSupp.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockSupp.recv(100),'utf-8')
        if recvMessage != '0\r\n':
            message = 'OP1 0\n';                                #if charger's output state is ON, it switches OFF the output
            sockSupp.sendall(bytes(message,'utf-8')) 

        message = 'SENSE1 1\n'                                  #it enables external sense 
        sockSupp.sendall(bytes(message,'utf-8'))
        
        message = 'I1?\n'                                       #it ask to charger, how is the current level sets
        sockSupp.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockSupp.recv(100),'utf-8')
        recvMessage = recvMessage.split()
        if float(recvMessage[1]) != float(testCurrent):         #if setting current is different from the new current value, it updates the new value
            message = 'I1 ' + testCurrent + '\n'
            sockSupp.sendall(bytes(message,'utf-8'))
        
        message = 'V1?\n'                                       #it ask to charger, how is the voltage level sets
        sockSupp.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockSupp.recv(100),'utf-8')   
        recvMessage = recvMessage.split()
        if float(recvMessage[1]) != float(limitVoltage):        #if setting voltage is different from the new voltage value, it updates the new value
            message = 'V1 ' + limitVoltage +'\n'
            sockSupp.sendall(bytes(message,'utf-8'))
       
        message = 'OP1 1\n';                                    #Enabling charger's output 
        sockSupp.sendall(bytes(message,'utf-8'))

        message = 'OP1?\n'                                      #it ask to charger if the output is enables 
        sockSupp.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockSupp.recv(100),'utf-8')        
        if recvMessage != '1\r\n':    
            print('setCahrge -> Error num: 004')    
            sys.exit(1)
            
    except socket.timeout:
        print('setCharge -> Error num: 001')
        try:
            sockSupp.sendall(bytes('OP1 0\n','utf-8'))         #If there is an error, it switches OFF the charger output
            sockSupp.close()
        except BrokenPipeError:                                #if the program try to switches off the charger output while the charger isn't on line, the program close the socket anyway
            sockSupp.close()
        sys.exit(1)
        
    except SystemExit:
        try:
            sockSupp.sendall(bytes('OP1 0\n','utf-8'))         #If there is an error, it switches OFF the charger output
            sockSupp.close()
        except BrokenPipeError:                                #if the program try to switches off the charger output while the charger isn't on-line, the program close the socket anyway
            sockSupp.close()
        sys.exit(1)
        
    except:
        print('setCharge -> Error num: 002')
        sockSupp.close()
        sys.exit(1)

    return sockSupp

#----------------------- Setting Load ----------------------------
#setLoad() function opens socket to the load and sets the current and the dropout voltage on it.
#Prototype: setLoad(ip,port,testCurrent,limitVoltage)
#-----Args---------#
#   ip              -> it is the string that contains the load's ip address
#   port            -> it is the string that contains the load's port number 
#   testCurrent     -> it is the current amplitude by which the test are conducting
#   limitVoltage    -> it is the dropout voltage by which the test are conducting
#-----Return-------#
#   sockLoad        -> it is load's socket identifier

def setLoad(ip,port,testCurrent,limitVoltage):

    #------------- Open Socket Phase ----------------------#
    sockLoad = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockLoad.settimeout(10)
    chargerAddress = (ip,int(port))
    try:
        sockLoad.connect(chargerAddress)
    except socket.timeout:
        print('initCahrger -> Error num: 001')
        sys.exit(1);
    except ConnectionRefusedError:
        print('initCharger -> Error num: 002')
        sys.exit(1)
    except OSError:
        print('initCharger -> Error num: 002')
        sys.exit(1)

    sockLoad.settimeout(1)

    #------------- Setting Load phase ------------------------#
    try:
        message = 'INP?\n'                                  #it asks to load how is the input state
        sockLoad.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockLoad.recv(100),'utf-8')
        if recvMessage != 'INP 0\r\n':
            message = 'INP 0\n'                             #if input state is ON, it switches OFF it
            sockLoad.sendall(bytes(message,'utf-8'))

        message = 'A?\n'                                    #it asks to load how is the amplitude of current sets
        sockLoad.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockLoad.recv(100),'utf-8')
        recvMessage = recvMessage.split()
        if float(recvMessage[1]) != float(testCurrent):
            message = 'A ' + testCurrent + '\n'             #if current amplitude isn't the same of previews one, a new current amplitude is set
            sockLoad.sendall(bytes(message,'utf-8'))
        
        message = 'DROP?\n'                                 #it asks to load how is the dropout voltage setting
        sockLoad.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockLoad.recv(100),'utf-8')
        recvMessage = recvMessage.split()
        if float(recvMessage[1]) != float(limitVoltage):
            message = 'DROP ' + limitVoltage + '\n'         #it dropout voltage is different from the new dropout voltage, it sets it
            sockLoad.sendall(bytes(message,'utf-8'))
    
        message = 'INP 1\n'                                 #it sets ON the input state 
        sockLoad.sendall(bytes(message,'utf-8'))
 
        message = 'INP?\n'                                  #It verifies if the input state is ON
        sockLoad.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockLoad.recv(100),'utf-8')
        if recvMessage != 'INP 1\r\n':
            print('setLoad -> Error num: 002')
            sys.exit(1)
            
    except socket.timeout:
        print('setLoad -> Error num: 001')
        try:
            sockLoad.sendall(bytes('INP 0\n','utf-8'))         #If there is an error, it switches OFF the load input
            sockLoad.close()
        except BrokenPipeError:                                #if the program try to switches off the load input while the charger isn't on-line, the program close the socket anyway
            sockLoad.close()
        sys.exit(1)
        
    except SystemExit:
        try:
            sockLoad.sendall(bytes('INP 0\n','utf-8'))         #If there is an error, it switches OFF the load input
            sockLoad.close()
        except BrokenPipeError:                                #if the program try to switches off the load input while the charger isn't on line, the program close the socket anyway
            sockLoad.close()
        sys.exit(1)
        
    except:
        print('setLoad -> Error num: 002')
        sockLoad.close()
        sys.exit(1)

    return sockLoad
    
#----------------------- Resetting Charge ----------------------------
#resetCharge() function  switches off charger's output, external sense and closes socket. 
#Prototype: resetCharge(sockCharger)
#-----Args---------#
#   sockCharge      -> it is charger's socket identifier
#-----Return-------#
#   any

def resetCharge(sockCharger):

    #----------------- Resetting charger phase -----------------------#
    try:
        message = 'OP1 0\n'                             #it disables the output 
        sockCharger.sendall(bytes(message,'utf-8'))
  
        message = 'SENSE1 0\n'                          #it disables the external sense (external sense produces 1.5mA absorption
        sockCharger.sendall(bytes(message,'utf-8'))
   
        message = 'OP1?\n'                              #it verifies if output is really switch OFF
        sockCharger.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockCharger.recv(100),'utf-8')
        if recvMessage != '0\r\n':
            print('resetCahrge -> Error num: 004')                      
            sys.exit(1)

        while(True):                                    #it waits that current amplitude reaches the zero level
            message = 'I1O?\n'
            sockCharger.sendall(bytes(message,'utf-8'))
            recvMessage = str(sockCharger.recv(100),'utf-8')
            recvMessage = recvMessage.split('A')
            if(float(recvMessage[0]) <= 0.0):
                break

    except socket.timeout:
        print('resetCharge -> Error num: 001')
        try:
            sockCharger.sendall(bytes('OP1 0\n','utf-8'))         #If there is an error, it switches OFF the charger output
            sockCharger.close()
        except BrokenPipeError:                                #if the program try to switches off the charger output while the charger isn't on line, the program close the socket anyway
            sockCharger.close()
        sys.exit(1)
        
    except SystemExit:
        try:
            sockCharger.sendall(bytes('OP1 0\n','utf-8'))         #If there is an error, it switches OFF the charger output
            sockCharger.close()
        except BrokenPipeError:                                #if the program try to switches off the charger output while the charger isn't on-line, the program close the socket anyway
            sockCharger.close()
        sys.exit(1)
        
    except:
        print('resetCharge -> Error num: 002')
        sockCharger.close()
        sys.exit(1)
    

    #------- Closing socket Phase --------------#
    sockCharger.close()

 
#----------------------- Resetting Load ----------------------------
#resetLoad() function switches off the input of load instrument and closes the socket
#Prototype: resetLoad(sockC,sockLoad)
#-----Args---------#
#   sockLoad    -> it is Load's socket identifier
#-----Return-------#
#   any


def resetLoad(sockLoad):

    #------------ Resetting load phase -------------------------#
    try:
        message = 'INP 0\n'                             #it disables the load's input
        sockLoad.sendall(bytes(message,'utf-8'))
   
        message = 'INP?\n'                              #it asks to load how is the input state
        sockLoad.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockLoad.recv(100),'utf-8')
        if recvMessage != 'INP 0\r\n':
            print('resertLoad -> Error num: 004')
            sys.exit(1)

        while(True):                                    #it waits the current amplitude reaches the zero level
            message= 'I?\n'
            sockLoad.sendall(bytes(message,'utf-8'))
            recvMessage = str(sockLoad.recv(100),'utf-8')
            recvMessage = recvMessage.split('A')
            if float(recvMessage[0]) <= 0.0:
                break
        
    except socket.timeout:
        print('resetLoad -> Error num: 001')
        try:
            sockLoad.sendall(bytes('INP 0\n','utf-8'))         #If there is an error, it switches OFF the load input
            sockLoad.close()
        except BrokenPipeError:                                #if the program try to switches off the load input while the charger isn't on-line, the program close the socket anyway
            sockLoad.close()
        sys.exit(1)
        
    except SystemExit:
        try:
            sockLoad.sendall(bytes('INP 0\n','utf-8'))         #If there is an error, it switches OFF the load input
            sockLoad.close()
        except BrokenPipeError:                                #if the program try to switches off the load input while the charger isn't on-line, the program close the socket anyway
            sockLoad.close()
        sys.exit(1)
        
    except:
        print('resetLoad -> Error num: 002')
        sockLoad.close()
        sys.exit(1)

    #------------- Closing load's socket phase -------------#
    sockLoad.close()

#----------------------- Setting instrument before test-step starting  ----------------------------#
#setBeforeStart() function  sets relays state and instruments according with the type of step
#Prototype: setBeforeStart(ip,port,skC,info)
#-----Args---------#
#   ip          -> it is a 1x2 tuple that contain in [0] Charger's ip address and  in [1] Load's ip Address
#   port        -> it is a 1x2 tuple that contain in [0] Charger's port number and  in [1] Load's port number
#   skC         -> it is child-thread's socket identifier 
#   info        -> it is a tuple that contains command raw of current step-test. Info format is: info = [<type of measure>,<EnLog>,<samplesTime>,<Duration>,<limit current>,<limit voltage>,<stop test current>]
#-----Return-------#
#   socketTTi    -> it is the charger's or the Load's socket identifier

 
def setBeforeStart(ip,port,skC,info):
                                                     #Be careful to operation order. First setting relays then setting instrument
    if info[0] == 'charge':
        re.switchOn(skC,info[0])                                #it switches ON charger relay
        socketTTi = setCharge(ip[0],port[0],info[4],info[5])    #it sets charger
                                   
    elif info[0] == 'discharge':
        re.switchOn(skC,info[0])                                #it switches ON load relay
        socketTTi = setLoad(ip[1],port[1],info[4],info[5])      #it sets load
                           
    elif info[0] == 'measure':
        re.switchOff(skC)                                       #it switches OFF both relays 

        #---- Creating  load's socket ---------#

        socketTTi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #it can not use setLoad function, because it enables the input of load. (in this case, it must be disable) 
        socketTTi.settimeout(10)
        loadAddress = (ip[1],int(port[1]))
        try:
            socketTTi.connect(loadAddress)
        except socket.timeout:
            print('setBeforeStart -> Error num: 001')
            sys.exit(1);
        except ConnectionRefusedError:
            print('setBeforeStart -> Error num: 002')
            sys.exit(1)
        except OSError:
            print('setBeforeStart -> Error num: 002')
            sys.exit(1)

        socketTTi.settimeout(1)
        
    return socketTTi


#----------------------- Resetting Load after step-test stopping ----------------------------
#resetAfterStop() function  resets relays state and instruments in function of type of step
#Prototype: resetAfterStop(sockC,skTTi,info)
#-----Args---------#
#   sockC       -> it is child-thread's socket identifier 
#   skTTi       -> it is the actually use TTi instrument's socket identifier 
#   info        -> it is a tuple that contains command raw of current step-test. Info format is: info = [<type of measure>,<EnLog>,<samplesTime>,<Duration>,<limit current>,<limit voltage>,<stop test current>]
#-----Return-------#
#   any

def resetAfterStop(sockC,skTTi,info):       
    
                                    #Be careful to operation order. First resetting instrument then resetting relays
    if info[0] == 'charge':
        resetCharge(skTTi)          #it resets charger
        re.switchOff(sockC)         #it switches OFF charger's relay   
                                             
    elif info[0] == 'discharge':
        resetLoad(skTTi)            #it resets load
        re.switchOff(sockC)         #it switches OFF load's relay 
        
    elif info[0] == 'measure':
        skTTi.close()               #it close only the load's socket that was enable without using the setLoad() function                             
      


#----------------------- Sending start request to child thread----------------------------
#sendStart() function sends a starts request to child thread that starts the picolog data acquisition
#Prototype: sendStart(sockC)
#-----Args---------#
#   sockC       -> it is child-thread's socket identifier 
#-----Return-------#
#   any    
              
   
def sendStart(sockC):    
    try:
        sockC.sendall(bytes('Start\r\n','utf-8'))               #Sending start request that format is: <Start\r\n>
        recvMessage = str(sockC.recv(100),'utf-8')
        recvMessage = recvMessage.split('\r\n')
    except socket.timeout:
        print('sendStart -> Error num: 001')
        sys.exit(1)
    except:
        print('sendStart -> Error num: 004')
        sys.exit(1)
    
    if recvMessage[0] != 'Ack':                             #if it doesn't receive an Ack response something goes wrong so it aborts program execution
        print('sendStart -> Error num: 006')
        sys.exit(1)


#----------------------- Sending the New file request to child thread----------------------------
#sendNewFile(sockC,stepID) function sends an opening new file-log request to child thread
#Prototype: sendStart(sockC)
#-----Args---------#
#   sockC       -> it is child-thread's socket identifier
#   typeStep    -> it contains the type of current step (charge,discharge,measure)
#-----Return-------#
#   any    

def sendNewFile(sockC,stepID,typeStep):
    try:
        sockC.sendall(bytes('New_' + str(stepID) + '_' + typeStep + '\r\n', 'utf-8'))    #Request format: New_<Step_number>_<type_of_Step>\r\n
        recvMessage = str(sockC.recv(100),'utf-8')
        recvMessage = recvMessage.split('\r\n')
    except socket.timeout:
        print('sendNewFile -> Error num: 001')
        sys.exit(1)
    except:
        print('sendNewFile-> Error num: 004')
        sys.exit(1)
    
    if recvMessage[0] != 'Ack':                                     #if it doesn't receive an Ack response something goes wrong so it aborts program execution
        print('sendNewFile -> Error num: 006')
        sys.exit(1)


#----------------------- Sending the End file request to child thread----------------------------
#sendEndFile() function sends an ending file-log request to child thread
#Prototype: sendEndFile(sockC)
#-----Args---------#
#   sockC       -> it is child-thread's socket identifier 
#-----Return-------#
#   any    

def sendEndFile(sockC):
    try:
        sockC.sendall(bytes('End\r\n','utf-8'))                 #Request format: End\r\n
        recvMessage = str(sockC.recv(100),'utf-8')
        recvMessage = recvMessage.split('\r\n')
    except socket.timeout:
        print('sendEndFile -> Error num: 001')
        sys.exit(1)
    except:
        print('sendEndFile-> Error num: 004')
        sys.exit(1)
    
    
    if recvMessage[0] != 'Ack':                             #if it doesn't receive an Ack response something goes wrong so it aborts program execution
        print('sendEndFile -> Error num: 006')
        sys.exit(1)

#----------------------- Sending the Exit request to child thread----------------------------
#sendExit(sockC) function sends an abort of execution request to child thread
#Prototype: sendExit(sockC)
#-----Args---------#
#   sockC       -> it is child-thread's socket identifier 
#-----Return-------#
#   any    


def sendExit(sockC):
    try:
        sockC.sendall(bytes('Exit\r\n','utf-8'))    #Request format: Exit\r\n
        recvMessage = str(sockC.recv(100),'utf-8')
        recvMessage = recvMessage.split('\r\n')
    except socket.timeout:
        print('sendExit -> Error num: 001')
        sys.exit(1)
    except:
        print('sendExit -> Error num: 004')
        sys.exit(1)

    if recvMessage[0] != 'Ack':                 #if it doesn't receive an Ack response something goes wrong so it aborts program execution
        print('sendExit -> Error num: 006')
        sys.exit(1)


    

    
   
  



