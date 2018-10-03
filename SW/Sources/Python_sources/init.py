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

#--------------- BUILT-IN Python module ------------#
import socket
import sys
import time
import threading
import subprocess
import tkinter as tk
import rele as re


#------------------- Charger  Initialization ------------------------------------#
# initCHarger() function creates a socket interfaces to charger and initializes it. Socket's information and Instrument model are token in chargerinfo.txt.
#The function return socket's identifier.

#Prototype; initCharger()
#------Arguments----------
#   Any
#------ Return ----------
#   [ip,port] -> is a 1x2 tuple that contains charge's ip address in [0], and port number in [1]
def initCharger():

    #--------- Reading technical information ---------------------#
    
    with open("../../Setting_File/chargerinfo.txt") as chargerInfoFile:  
        chargerInfo = chargerInfoFile.read()
        chargerInfoFile.close()
    

    chargerInfoRaw = chargerInfo.splitlines()

    for i in range(len(chargerInfoRaw)):
        if chargerInfoRaw[i] != '':
            if chargerInfoRaw[i][0] != '#':                 #rows contains information only if they don't start with # character
                socketInfo = chargerInfoRaw[i].split()
                if socketInfo[0] == 'Model:':               #Model number
                    model = socketInfo[1]
                elif socketInfo[0] == 'IPAddress:':         #Socket IP address
                    ip = socketInfo[1]
                elif socketInfo[0] == 'Port:':              #Port No
                    port = socketInfo[1]
                    break
    
    #----------- Configuring socket interface --------------------#
                
    sockCharger = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockCharger.settimeout(10)
    chargerAddress = (ip,int(port))
    try:
        sockCharger.connect(chargerAddress)
    except socket.timeout:
        print('initCahrger -> Error num: 001')
        sys.exit(1);
    except ConnectionRefusedError:
        print('initCharger -> Error num: 002')
        sys.exit(1)
    except OSError:
        print('initCharger -> Error num: 002')
        sys.exit(1)

    #----------- Initial System Setting----------------------------#
        
    message = '*IDN?'                                           #Sending Request to knows the model of charger         
    try:
        sockCharger.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockCharger.recv(100),'utf-8')
        recvMessage = recvMessage.split(',');                   
        recvMessage[1] = recvMessage[1].strip();                #Deleting space
      
        if model != recvMessage[1]:                             #ERROR: If the model is different from that contains in chargerinfo.txt
            print('initCahrger -> Error num: 003')
            sockCharger.close()
            sys.exit(1)

        
        message = 'LSE1 32\n'                           #It enables the bit enable of trip error in the status error register of charger
        sockCharger.sendall(bytes(message,'utf-8'))
               
        message = 'OP1 0\n'                             #it disables output
        sockCharger.sendall(bytes(message,'utf-8'))
    
        message = 'SENSE1 0\n'                          #It disables external sense of instrument. (Sense is only enable when output is ON 
        sockCharger.sendall(bytes(message,'utf-8'))
  
        message = 'V1V 0\n'                             #it sets voltage to 0V
        sockCharger.sendall(bytes(message,'utf-8'))

        message = 'I1 0\n'                              #it sets current to 0A
        sockCharger.sendall(bytes(message,'utf-8'))

        message = 'CONFIG?'                             #It is a question that say to charger  "have you been configure?"
        sockCharger.sendall(bytes(message,'utf-8'))     
        
        recvMessage = str(sockCharger.recv(100),'utf-8')    
    
        if recvMessage != '1\r\n':
            print('initCahrger -> Error num: 004')              #it receives a response different from one, some error occurred
            sys.exit(1)
            
        message = '*STB?\n'                                         #if *STB is different from 0 there is a trip error
        sockCharger.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockCharger.recv(100),'utf-8')
        recvMessage = recvMessage.split('\r\n');
        if recvMessage[0] != '0':                                        
            print('initCharger -> Error num: 05')
            sockCharger.close()
            sys.exit(1)
    
    except socket.timeout:
        print('initCahrger -> Error num: 001')              
        sockCharger.close()
        sys.exit(1)
    except SystemExit:
        sockCharger.close()
        sys.exit(1)        
    except:
        print('initCahrger -> Error num: 002')
        sockCharger.close()
        sys.exit(1);

    #--------------- closing socket phase ------------#
    sockCharger.close()                                         #it closes socket

    
    return [ip,port]



#------------------- Load  Initialization ------------------------------------#
# initLoad() function creates a socket interfaces to load and initializes the load. Socket's information and Instrument model are pick in loadinfo.txt.
#The function return socket's identifier.

#Prototype; initLoad()
#------Arguments----------
#   Any
#------ Return ----------
# [ip,port] -> is a 1x2 tuple that contains load's ip address in [0], and port number in [1]
def initLoad():
    
    #------------- Reading technical information ----------#
    
    with open("../.././Setting_File/loadinfo.txt") as loadInfoFile:  
        loadInfo = loadInfoFile.read()
        loadInfoFile.close()
    

    loadInfoRaw = loadInfo.splitlines()
   
    for i in range(len(loadInfoRaw)):
        if loadInfoRaw[i] != '':
            if loadInfoRaw[i][0] != '#':                            #rows contains information only if they don't start with # carachter
                socketInfo = loadInfoRaw[i].split()
                if socketInfo[0] == 'Model:':                       #Model 
                    model = socketInfo[1]
                elif socketInfo[0] == 'IPAddress:':                 #Socket IP address
                    ip = socketInfo[1]  
                elif socketInfo[0] == 'Port:':                      #Port No
                    port = socketInfo[1]
                    break
    
    #-------------- Creating socket interface ----------------------#
                
    sockLoad = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockLoad.settimeout(10)
    loadAddress = (ip,int(port))
    try:
        sockLoad.connect(loadAddress)
    except socket.timeout:
        print('initLoad -> Error num: 001')
        sys.exit(1)
    except ConnectionRefusedError:
        print('initLoad -> Error num: 002')
        sys.exit(1)
    except OSError:
        print('initLoad -> Error num: 002')
        sys.exit(1)
        

    #--------------- Initial Setting of load ------------------------#
               
    message = '*IDN?'                                           #it asks to load the model number and confronts with that in Loadinfo.txt
    try:
        sockLoad.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockLoad.recv(100),'utf-8')
   
        recvMessage = recvMessage.split(',');    
        recvMessage[1] = recvMessage[1].strip(); 
      
        if model != recvMessage[1]:              
            print('initLoad -> Error num: 003')
            sockLoad.close()
            sys.exit(1)
 
    
        message = 'INP 0\n'                             #Disabling input
        sockLoad.sendall(bytes(message,'utf-8'))
    
        message = 'MODE C\n'                            #Setting CC mode
        sockLoad.sendall(bytes(message,'utf-8'))

        message = '600W 0\n'                            #Setting 400W
        sockLoad.sendall(bytes(message,'utf-8'))

        message = 'RANGE 0\n'                           #it fixed the current range to 80A
        sockLoad.sendall(bytes(message,'utf-8'))
        
        message = 'A 0\n'                               #Setting level A current to 0A
        sockLoad.sendall(bytes(message,'utf-8'))
  
        message = 'B 0\n'                               #Setting level B current to 0A
        sockLoad.sendall(bytes(message,'utf-8'))

        message = 'DROP 0\n'                            #Setting dropout voltage to 0V
        sockLoad.sendall(bytes(message,'utf-8'))

        message = 'LVLSEL A\n'                          #Enabling A level
        sockLoad.sendall(bytes(message,'utf-8'))
        message = 'LVLSEL?'                             #it asks a generic question to load, in this way it wait load  completing operation
        sockLoad.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockLoad.recv(100),'utf-8')
        if recvMessage != 'LVLSEL A\r\n':
            print('initLoad -> Error num: 004')
            sys.exit(1)

    except socket.timeout:
        print('initLoad -> Error num: 001')
        sockLoad.close()
        sys.exit(1)
    except SystemExit:
        sockLoad.close()
        sys.exit(1)
    except:
        print('initLoad -> Error num: 002')
        sockLoad.close()
        sys.exit(1);

    #------------------ closing socket phase --------------------#
    sockLoad.close()

    return [ip,port]


#------------------- Picolog  Initialization ------------------------------------#
# startPicolog() function starts a child thread. The Child thread is a C language Thread that aim is to manage the Picolog data logger. Python communicate with its child thread through socket interfaces.
#It return a tuple which contains Pid, and socket identifier

#Prototype; startPicolog()
#------Arguments----------
#   Any
#------ Return ----------
#   infoPico[<Pid>,<Socket>] where:
#        Pid        -> is the child's identifier
#        Socket     -> is the socket identifier

def startPicoLog():
    command_line = '.././C++_sources/main'
    pid = subprocess.Popen(command_line)     #It creates a child thread
    time.sleep(2)                            #it waits two seconds. At the end the child thread had created the socket interface
  
   
    #----------------- Creating socket at IP address <127.0.0.1> Port No <1234> -------------------------#
    
    sockPico = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 1234)
    sockPico.settimeout(30)
    
    try:
        sockPico.connect(server_address)   
    except ConnectionRefusedError:
        print('startPicoLog -> Error num: 002')
        pid.terminate()
        sys.exit(1)
    except OSError:
        print('startPicoLog -> Error num: 002')
        pid.terminate()
        sys.exit(1)        
    except socket.timeout:
        print('startPicoLog -> Error num: 001')
        pid.terminate()
        sys.exit(1)

    
    sockPico.settimeout(120)    #CAUTION: Timeout is set at 120sec because Picolog starting require 90 sec, the first time.

    try:
        recv = str(sockPico.recv(100),'utf-8')
    except socket.timeout:
        print('startPicoLog -> Error num: 001')      #May be Picolog isn't connect
        pid.terminate()
        sockPico.close()
        sys.exit(1)
        
   
    recv = recv.split('\r\n')
    
    if recv[0] != 'Ack':                            #If there isn't an Ack response, Python aborts the execution, and Child thread kills him self
        print('startPicoLog -> Error num: 006')
        pid.terminate()
        sockPico.close()
        sys.exit(1)
    
    sockPico.settimeout(1)
  
    infoPico = (pid,sockPico)

    return infoPico
    



#-------------Initialization of relays ---------------------------#
#initRelè() reads from picologinfo.txt the pin position of relays and sends this information to child thread.

#Prototype: initRelè(sockC)
#-----------Arguments-----------------------#
#   sockC       ->      Child thread sockets identifier 
#-----------Return--------------------------#
#    any

def initRelè(sockC):

    #-------------Reading Picolog tecnical information -------------#
    with open("../.././Setting_File/picologinfo.txt") as picoInfoFile:  
        picoInfo = picoInfoFile.read()
        picoInfoFile.close()

    picoInfoRaw = picoInfo.splitlines()
       
    for i in range(len(picoInfoRaw)):
        if picoInfoRaw[i] != '':
            if picoInfoRaw[i][0] != '#':                                        #rows contains information only if they don't start with # character
                instrumentInfo = picoInfoRaw[i].split()
                if instrumentInfo[0] == 'DigitalChargerRelèPin:':               #Digital pin position of charger relay 
                    digitChargerRelèPin = instrumentInfo[1]
                elif instrumentInfo[0] == 'AnalogChargerRelèChecker:':          #Analog channel position where reading charge relay's state
                    analogChargerRelèChecker = instrumentInfo[1]
                elif instrumentInfo[0] == 'DigitalLoadRelèPin:':                #Digital pin position of load relay          
                    digitLoadRelèPin = instrumentInfo[1]
                elif instrumentInfo[0] == 'AnalogLoadRelèChecker:':             #Analog channel position where reading load relay's state       
                    analogLoadRelèChecker = instrumentInfo[1]
                elif instrumentInfo[0] == 'RelèThreshold:':                     #Relay voltage threshold that separates OFF from ON state
                    relèThreshold = instrumentInfo[1]
                    break     

              
    #------------------Cheking insertes information ---------------------------#
                
    if (int(digitChargerRelèPin) > 4) or (int(digitChargerRelèPin) < 1):            #Digital pin position range is from 1 to 4
        print('initRelè -> Error num: 007')
        sys.exit(1)

    if (int(analogChargerRelèChecker) > 8) or (int(analogChargerRelèChecker) < 1):  #Analog channels range is from 1 to 8
        print('initRelè -> Error num: 008')
        sys.exit(1)

    if (int(digitLoadRelèPin) > 4) or (int(digitLoadRelèPin) < 1):                  #Digital pin position range is from 1 to 4
        print('initRelè -> Error num: 007')
        sys.exit(1)
        
    elif (analogChargerRelèChecker == analogLoadRelèChecker) or (digitLoadRelèPin == digitChargerRelèPin): #It excludes overlapping position between analog channel and digital pin that control the relays
        print('initRelè -> Error num: 009')
        sys.exit(1)

    if (int(analogLoadRelèChecker) > 8) or (int(analogLoadRelèChecker) < 1):        #Analog channels range is from 1 to 8
        print('initRelè -> Error num: 008')
        sys.exit(1)

    if (float(relèThreshold) < 0):                                                  #Relays threshold may not be negative
        print('initRelè -> Error num: 010')
        sys.exit(1)

    
    #-------------- sending information to Child thread -------------------------#
    
    message = 'SetRelè ' + digitChargerRelèPin + ' ' + analogChargerRelèChecker + ' ' + digitLoadRelèPin + ' ' + analogLoadRelèChecker + '\r\n'
    try:
        sockC.sendall(bytes(message,'utf-8'))                  #Request service format: SetRelè <Digital pin to control charger's relay> <analog channel that control the state of charger's relay>....
        recvMessage = str(sockC.recv(100),'utf-8')                                         #....<Digital pin to control load's relay> <analog channel that control the state of charger's relay>
    except socket.timeout:
        print('initRelè -> Error num: 001')
        sys.exit(1)
    except:
        print('initRelè -> Error num: 002')
        sys.exit(1)
        
    Crisp = recvMessage.split('\r\n')
    if Crisp[0] != 'Ack':
        print('initRelè -> Error num: 006')
        sys.exit(1)

    re.switchOff(sockC)                   #it switches of both relays 



#-------------Initialization of temperature sensor ---------------------------#
#initTemp() sets the analog channel where the temperature sensor is reads, and sends this information to child thread. Analog Channel information is picks from picologinfo.txt

#Prototype: initTemp(sockC)
#-----------Arguments-----------------------#
#   sockC       ->      Child thread sockets identifier 

#-----------Return--------------------------#
#    any

def initTemp(sockC):

    #---------------- Reading technical information ------------------#
    
    with open("../.././Setting_File/picologinfo.txt") as tempInfoFile:  
        tempInfo = tempInfoFile.read()
        tempInfoFile.close()

    tempInfoRaw = tempInfo.splitlines()

    #--------------- Cheking errors-----------------------------------#
    
    for i in range(len(tempInfoRaw)):
        if tempInfoRaw[i] != '':
            if tempInfoRaw[i][0] != '#':                                #rows contains information only if they don't start with # character
                instrumentInfo = tempInfoRaw[i].split()
                if instrumentInfo[0] == 'AnalogTempChannel:':           #Analog channel position where temperature sensor is reading 
                    tempCh = instrumentInfo[1]
                    break

    if (int(tempCh) > 8) or (int(tempCh) < 1):                          #Analog channel range is from 1 to 8           
        print('initTemp -> Error num: 008')
        sys.exit(1)

    
    
    #--------------- Sending information to Child thread--------------#

    message = 'SetTempCh '  + tempCh + '\r\n'                       # Request format is: SetTempCh <analog_channel_position>
    try:
        sockC.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockC.recv(100),'utf-8')
    except socket.timeout:
        print('initTemp -> Error num: 001')
        sys.exit(1)
    except:
        print('initTemp -> Error num: 002')
        sys.exit(1)

    Crisp = recvMessage.split('\r\n')
    if Crisp[0] != 'Ack':
        print('initTemp -> Error num: 006')
        sys.exit(1)



#-------------Initialization of GUI interface---------------------------#
#initGUI() initializes the GUI interface where user can reads  information about the test current state. 

#Prototype: initGUI()
#-----------Arguments-----------------------#
#   any

#-----------Return--------------------------#
#   GUITable    -> is a Tuple that contains all label of GUI interfaces GUItable = [<root>]
#                                                                                      [<currentStep>,<type_of_step>,<enLog>,<ledEnLog>,<period>,...
#                                                                                                   ...<testLen>,<test_I>,<droput_V>,<stop_I>,<realtime_voltage>,...
#                                                                                                   ...<realtime_current>,<realtime_deltaQ>,<instrTimeStamp>,...
#                                                                                                   ...<localTimeStamp>,<temperature>,<timeStart>,<date_to_Start>,...
#                                                                                                   ...<timeStop>,<date_Stop>,<numOfStep>,<totalStep>,<error>,...
#                                                                                                   ...<ledError>,<run>,<ledRun>] 
                             

def initGUI():
    root = tk.Tk()

    #------------ Background-----------------#
    root.configure(bg = 'sky blue')

    #------------ Title ----------------------#
    title = tk.Label(root, text = "Test description", bg = 'sky blue', fg = 'blue', font = ("Times",30,"bold"), bd = '5', highlightbackground = 'blue',relief = 'raised')
    title.grid(row = 0, column = 0, columnspan = 10)
    
    currentStep = tk.Label(root, text = '', bg = 'white', fg = 'black', highlightthickness = '1', highlightbackground = 'black',width = 5,relief = 'ridge')
    currentStep.grid(row = 1, column = 0)

    #------------- Raw command section ----------------#
    frameCommand = tk.Frame(root, bg = 'light steel blue', bd = '1',highlightthickness = '5', highlightbackground = 'sky blue', relief = 'ridge')
    frameCommand.grid(row = 1, column = 1, columnspan = 9, rowspan = 2, sticky = 'W' )


    txtcmd = tk.Label(frameCommand, text = 'cmd', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 10)
    txtcmd.grid(row = 0, column = 0)

    txtLogEn = tk.Label(frameCommand, text = 'log_en', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 10)
    txtLogEn.grid(row = 0, column = 1)

    txtPeriod = tk.Label(frameCommand, text = 'log_period', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 10)
    txtPeriod.grid(row = 0, column = 2)

    txtTestLen = tk.Label(frameCommand, text = 'test_length', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 10)
    txtTestLen.grid(row = 0, column = 3)

    txtTestI = tk.Label(frameCommand, text = 'test_I', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 10)
    txtTestI.grid(row = 0, column = 4)

    txtLimitV = tk.Label(frameCommand, text = 'limit_V', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 10)
    txtLimitV.grid(row = 0, column = 5)

    txtStopI = tk.Label(frameCommand, text = 'stop_I', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 10)
    txtStopI.grid(row = 0, column = 6)


    cmd = tk.Label(frameCommand, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 10)
    cmd.grid(row = 1, column = 0)

    enLog = tk.Canvas(frameCommand, width = '20', height = '20', bg = 'light steel blue', highlightbackground = 'light steel blue')
    enLog.grid(row = 1, column = 1)

    ledEnLog = enLog.create_oval(20,20,5,5, fill='green2' )
   


    period = tk.Label(frameCommand, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 10)
    period.grid(row = 1, column = 2)

    testLen = tk.Label(frameCommand, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 10)
    testLen.grid(row = 1, column = 3)

    testI = tk.Label(frameCommand, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 10)
    testI.grid(row = 1, column = 4)

    limitV= tk.Label(frameCommand, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 10)
    limitV.grid(row = 1, column = 5)

    stopI = tk.Label(frameCommand, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 10)
    stopI.grid(row = 1, column = 6)

    root.grid_rowconfigure(1, pad = 100)

    #---------------------------- Real-time Data section----------------------------------#
    
    frameData = tk.Frame(root, bg = 'light steel blue', bd = '1',highlightthickness = '5', highlightbackground = 'sky blue', relief = 'ridge')
    frameData.grid(row = 3, column = 1, columnspan = 3, rowspan = 2, sticky = 'W')

    txtVoltage = tk.Label(frameData, text = 'Voltage[V]', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 20)
    txtVoltage.grid(row = 0, column = 0)

    txtCurrent = tk.Label(frameData, text = 'Current[A]', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 20)
    txtCurrent.grid(row = 0, column = 1)

    txtDeltaQ= tk.Label(frameData, text = 'Q[Ah]', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 25)
    txtDeltaQ.grid(row = 0, column = 2)

    voltage = tk.Label(frameData, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 20)
    voltage.grid(row = 1, column = 0)

    current = tk.Label(frameData, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 20)
    current.grid(row = 1, column = 1)

    deltaQ = tk.Label(frameData, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 25)
    deltaQ.grid(row = 1, column = 2)



    #---------------------------- Time-stamp data section ---------------------------------#
    
    frameTimeStamp = tk.Frame(root, bg = 'light steel blue', bd = '1',highlightthickness = '5', highlightbackground = 'sky blue', relief = 'ridge')
    frameTimeStamp.grid(row = 5, column = 1, columnspan = 3, rowspan = 2, sticky = 'W')

    txtInstrTimeStamp = tk.Label(frameTimeStamp, text = 'Local_Time', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 20)
    txtInstrTimeStamp.grid(row = 0, column = 0)

    txtLocalTime= tk.Label(frameTimeStamp, text = 'CPU_Time', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black', width = 20)
    txtLocalTime.grid(row = 0, column = 1)

    txtTemperature = tk.Label(frameTimeStamp, text = 'Temperature[°C]', bg = 'light steel blue', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 20)
    txtTemperature.grid(row = 0, column = 2)

    instrTimeStamp = tk.Label(frameTimeStamp, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 20)
    instrTimeStamp.grid(row = 1, column = 0)

    localTimeStamp = tk.Label(frameTimeStamp, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 20)
    localTimeStamp.grid(row = 1, column = 1)

    temperature = tk.Label(frameTimeStamp, text = '', bg = 'white', fg = 'black',highlightthickness = '1', highlightbackground = 'black',width = 20)
    temperature.grid(row = 1, column = 2)


    root.grid_columnconfigure(4, pad = 100)

    #----------------------------- Start time data section----------------------------------#
    
    frameTimeStart = tk.Frame(root, bg = 'sky blue', bd = '3', highlightbackground = 'sky blue', relief = 'sunken')
    frameTimeStart.grid(row = 3, column = 4, rowspan = 3)

    txtTimeStart = tk.Label(frameTimeStart, text = 'test_start_time', bg = 'sky blue', fg = 'blue',font = ("Times",11,"bold"),width = 20)
    txtTimeStart.grid(row = 0, column = 0)

    timeStart = tk.Label(frameTimeStart, text = '', bg = 'white', fg = 'black',width = 20)
    timeStart.grid(row = 1, column = 0)

    dateStart = tk.Label(frameTimeStart, text = '', bg = 'white', fg = 'black',width = 20)
    dateStart.grid(row = 2, column = 0)



    #-----------------------------Remaning time --------------------------------#
    
    frameTimeStop = tk.Frame(root, bg = 'sky blue', bd = '3', highlightbackground = 'sky blue', relief = 'sunken')
    frameTimeStop.grid(row = 6, column = 4, rowspan = 3)

    txtTimeStop = tk.Label(frameTimeStop, text = 'remaning_step_time_[s]', bg = 'sky blue', fg = 'blue', font = ("Times",11,"bold"), width = 20)
    txtTimeStop.grid(row = 0, column = 0)

    timeStop = tk.Label(frameTimeStop, text = '', bg = 'white', fg = 'black',width = 20)
    timeStop.grid(row = 1, column = 0)

    dateStop = tk.Label(frameTimeStop, text = '', bg = 'white', fg = 'black',width = 20)
    dateStop.grid(row = 2, column = 0)

    #-------------------------- Step progress section ------------------------#
    frameStep = tk.Frame(root, bg = 'sky blue', bd = '3', highlightbackground = 'sky blue', relief = 'flat')
    frameStep.grid(row = 7, column = 5, rowspan = 2, columnspan = 3)

    txtStep = tk.Label(frameStep, text = 'Step', bg = 'sky blue', fg = 'blue', font = ("Times",11,"bold"), width = 5)
    txtStep.grid(row = 0, column = 0)

    numOfStep = tk.Label(frameStep, text = '', bg = 'white', fg = 'black',width = 5, bd = '3', relief = 'sunken')
    numOfStep.grid(row = 1, column = 0)

    of = tk.Label(frameStep, text = 'of', bg = 'sky blue', fg = 'blue', font = ("Times",11,"bold"), width = 5)
    of.grid(row = 1, column = 1)

    totalStep = tk.Label(frameStep, text = '', bg = 'white', fg = 'black',width = 5, bd = '3', relief = 'sunken' )
    totalStep.grid(row = 1, column = 2)

    #--------------------------State of test----------------------------------#
    frameRun = tk.Frame(root, bg = 'sky blue', bd = '1',highlightthickness = '5', highlightbackground = 'sky blue', relief = 'flat')
    frameRun.grid(row = 1, column = 5, rowspan = 2 )

    txtRun = tk.Label(frameRun, text = 'Running?', bg = 'sky blue', fg = 'blue',font = ("Times",11,"bold"), width = 10)
    txtRun.grid(row = 0, column = 0)

    run = tk.Canvas(frameRun, width = '35', height = '35', bg = 'sky blue', highlightbackground = 'sky blue')
    run.grid(row = 1, column = 0)

    ledRun = run.create_oval(35,35,5,5, fill='green2')

    frameAll = tk.Frame(root, bg = 'sky blue', bd = '3', highlightbackground = 'sky blue',relief = 'flat')
    frameAll.grid(row = 3, column = 5, rowspan = 2)

    txtRun = tk.Label(frameAll, text = 'allright?', bg = 'sky blue', fg = 'blue',font = ("Times",11,"bold"), width = 10)
    txtRun.grid(row = 0, column = 0)

    error = tk.Canvas(frameAll, width = '35', height = '35', bg = 'sky blue', highlightbackground = 'sky blue')
    error.grid(row = 1, column = 0)

    ledError = error.create_oval(35,35,5,5, fill='green2')

    root.update()

    #----------------------------- return section ---------------------#
    idLabel = (currentStep,cmd,enLog,ledEnLog,period,testLen,testI,limitV,stopI,voltage,current,deltaQ,instrTimeStamp,localTimeStamp,temperature,timeStart,dateStart,timeStop,dateStop,numOfStep,totalStep,error,ledError,run,ledRun)
    GUITable = (root,idLabel)

    return GUITable



