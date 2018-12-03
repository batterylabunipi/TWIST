#!/usr/bin/python3.4
# coding=utf-8

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



#------ Importing Python's BUILT-IN module --------
import socket
import time
import sys
import threading
import queue
import subprocess
import tkinter
from apscheduler.schedulers.background import BackgroundScheduler


#------ Importing some Custom module -------
import init as it           #This module initialized: the TTi and Picolog ADC-24 communication interfaces; the position of temperature sensor and relays, and the GUIs.   
import instrument as st     #This module provide setting function to manage the TTi and Picolog instruments 
import path_search as ph    #This module provide information about paths where to save the TTi and Picolog  Log-files.


#------- Global labels --------
#timeBeforeEnd = 0   	#it used from acq and loop to count the time lapse between two steps
samplesDone = 0     	#it used only inside acq thread to counts the number of picked samples



#-------Definition of principal function used in the main() task -------------------#

#------- Data acquisition loop -------------------------#
# dataAcquisition() task asks periodically the measurements voltage, current and temperature from TTi instruments,
# and also asks the temperature and the relays state from PicoLog. After that, all information are send to a share buffer with main task.

# --- Prototype: dataAcquisition(sockC,socketTTi,chargeLoop,queueInfo,sched,totalSamples,samplesTime,numBytes) -----

#   sockC,socketTTi    -> they indicate the socket of Picolog and TTi instruemnts, respectively
#   chargeLoop         -> it is a flag that if True indicate a charging phase
#   queueInfo          -> it is a share data buffer identifier with the main task
#   sched              -> it is a scheduler identifier
#   totalSamples       -> it indicates the total number of samples to pick from instruments
#   samplesTime        -> it indicates the samples time used 
#   numBytes           -> it indicates the length of data send to the C-thread that manages Picolog
# ---- return ------
#   The function return nothing.

def dataAcquisition(sockC,socketTTi,chargeLoop,queueInfo,sched,totalSamples,samplesTime,numBytes):
    global samplesDone      #samplesDone is a samples counter
    #global timeBeforeEnd

    #-----init variables------- 
    state = 'ok'                                        #State specify if an error occurred
    remainingTime = -1                                  #indicates the remaining time to the current step ending 
    recvMessage = 'c'                                 
    UTC = time.strftime("%H:%M:%S",time.localtime())    #UTC contain the local time in hours:minute:seconds
    CPUTime = time.perf_counter()                       #CPUTime contains processor time
    control = 0                                         #control contains the data comes from Picolog
    voltage = 0                                         #voltage contains the data of voltage measurements come from charger or load
    current = 0                                         #current contains the data comes of current measurement come from charger or load

    
    if(samplesDone == 0):                               #It starts the scheduler and dataAcquisition task.
        sched.add_job(dataAcquisition, 'interval', args = [sockC,socketTTi,chargeLoop,queueInfo,sched,totalSamples,samplesTime,numBytes], seconds = samplesTime, id='MEASURE')  #Initialization of Periodic thread 
        sched.start()


    #------------ Choosing command phase --------------------#
    if chargeLoop == True:              #checking if the current test step is a charging one
        commandV = 'V1O?\n'             #Voltage reading requests to Charger
        commandI = 'I1O?\n'             #Current reading requests to Charger          
    else:
        commandV = 'V?\n'               #Voltage reading requests to load      
        commandI = 'I?\n'               #Current reading requests to Load


    #------------ Sending command to TTi instruments currently in use -------------------#
    #------------ Voltage reading ---------------------#
    try:
        socketTTi.sendall(bytes(commandV,'utf-8'))
        recvMessage = str(socketTTi.recv(100),'utf-8')
        recvMessage = recvMessage.split('V')
        voltage = float(recvMessage[0])
    except socket.timeout:
        print('dataAcquisition (TTi) -> Error num: 001')
        state = 'err'
        sched.remove_job('MEASURE')
    except:
        print('dataAcquisition (TTi) -> Error num: 002')
        state = 'err'
        sched.remove_job('MEASURE')

    #------------ Current Reading ---------------------#
    if state != 'err':               #Checking state flag to discover the occurrence of an error    
        try:
            socketTTi.sendall(bytes(commandI,'utf-8'))
            recvMessage = str(socketTTi.recv(100),'utf-8')
            recvMessage = recvMessage.split('A')
            if chargeLoop == True:
                current = -float(recvMessage[0])
            else:
                current = float(recvMessage[0])
        except socket.timeout:
            print('dataAcquisition (TTi) -> Error num: 001')
            state = 'err'
            sched.remove_job('MEASURE')
        except:
            print('dataAcquisition (TTi) -> Error num: 002')
            state = 'err'
            sched.remove_job('MEASURE')

    #----------- Reading Temperature from Picolog  --------------#
    if state != 'err':                  #Checking state flag to discover the occurrence of some error 
        try:
            sockC.sendall(bytes('Samples?\r\n','utf-8'))
            control = int.from_bytes(sockC.recv(numBytes), byteorder = 'little',signed = True) #the pattern data received from Picolog is [temperature, state charger's relay, state of load's relay]			is composed by 3 pattern of 4bytes (total = 12bytes)
        except socket.timeout:
            print('dataAcquisition (PicoLog) ->  Error num: 001')
            state = 'err'
            sched.remove_job('MEASURE')
        except:
            print('dataAcquisition (PicoLog) ->  Error num: 002')
            state = 'err'
            sched.remove_job('MEASURE')
 
    #----------- Elaboration phase ---------------------------#    
   
    if totalSamples != -1:                                          
        remainingTime = (totalSamples - samplesDone)*samplesTime    #it calculates the time to the end of acquisition
        if samplesDone >= totalSamples:                             #if samplesDone is equal to totalsamples the python stops the step acquisition
            if state != 'err':
                state = 'stp'
                sched.remove_job('MEASURE') #if there isn't error it stops scheduler otherwise it doesn't because it was already stopped

                       
    dataToSend = [control,voltage,current,UTC,CPUTime,remainingTime,state,samplesDone]  #sending data to GUI interface in mainloop

    samplesDone = samplesDone + 1                                                      
    
    try:
        queueInfo.put(dataToSend, timeout = 10)                     #sending data to share buffer (paradigm producer - consumer)
    except queue.Full:
        print('acquisition -> Error num: 023')
        sched.remove_job('MEASURE')
 

#------- loop() -------------------------#
# This function initialized useful resources to executing periodically the DataAcquisition() and reads the information from dataAcquisition() task 
#in order to updating the GUI interfaces. Finally it opens, manages and closes the correspondingly textual Log-files.

# Prototype: loop(sockC,sockTTi,infoTest,logFile,GUITable,TempMin,TempMax,releTh,Nbit,picoVoltageRange,Coeff,nStep)
#   sockC,sockTTi               -> they contain respectively the socket interfaces of PicoLog, TTi instruments.
#   infoTest                    -> is a Tuple that contains all information reported on step file raws: infoTest = {<type of measure>,<EnLog>,<samplesTime>,<Duration>,<limit current>,<limit voltage>,<stop test current>}
#   logFile                     -> contains the file descriptor of File log where the data saving
#   GUITable                    -> is a Tuple that contains all label of GUI interfaces GUItable = [<root>]
#                                                                                                  [<currentStep>,<type_of_step>,<enLog>,<ledEnLog>,<period>,...
#                                                                                                   ...<testLen>,<test_I>,<droput_V>,<stop_I>,<realtime_voltage>,...
#                                                                                                   ...<realtime_current>,<realtime_deltaQ>,<instrTimeStamp>,...
#                                                                                                   ...<localTimeStamp>,<temperature>,<timeStart>,<date_to_Start>,...
#                                                                                                   ...<timeStop>,<date_Stop>,<numOfStep>,<totalStep>,<error>,...
#                                                                                                   ...<ledError>,<run>,<ledRun>] 
                                                                                                    
#   TempMin                     -> is the inferior limit of temperature range where the cell works correctly
#   TempMax                     -> is the superior limit of temperature range where the cell works correctly
#   releTh                      -> is the relays threshold in Volt that separate the OFF state from ON state 
#   Nbit                        -> is ideal number of bit of Picolog's analog channel conversions
#   picoVoltageRange            -> is the input range use for Picolog's analog channel 
#   Coeff                       -> is the conversion coefficient to adopt on read data temperature
#   nStep                       -> identify the number of current step

#------ return ---------------------------#
# this function return nothing
    
      
def loop(sockC,sockTTi,infoTest,logFile,GUITable,TempMin,TempMax,releTh,Nbit,picoVoltageRange,Coeff,nStep):  
    global samplesDone
    #global timeBeforeEnd

    #-----init variables --------#
    samplesDone = 0
    byteFromC = 12                          #num of bytes to read from picoLog 
    deltaQ = 0.0                            #it indicates the real-time total charge extracted /inserted from cell under test
    maskFourBytes = 0xFFFFFFFF              #it used to perform a 32bit mask
    totalInfo = 3                           #Number of single data of 32bit to read from Picolog
    controlInfoPico = [0,0,0]               #this variable contains the reading measurements come from Picolog  
    loopCharge = False                      #this label is use to define if we are in a charge step or not
    text = '\n'
    error = False                           #this label is use to understand the errors occurrence
    sched = 0

  
    if infoTest[3] != -1:
        totalSamples = (infoTest[3]/infoTest[2])    #it calculates the total measurement samples for the current step                                             
    else:
        totalSamples = -1            

  
    if infoTest[0] == 'charge':                      #it verifies if we are in a charge step 
        loopCharge = True
   
    #------- Resources initialization ------------#
    
    sched = BackgroundScheduler()                   #scheduler initialization 
    queueGUI = queue.Queue(maxsize = 8)             #share buffer initialization  
    
   
    if infoTest[1] == 1:
        st.sendNewFile(sockC,nStep,infoTest[0])    #if enlog flag is enable it sends a requests of service to C thread which opens a new file 

    
    
    dataAcquisition(sockC,sockTTi,loopCharge,queueGUI,sched,totalSamples,infoTest[2],byteFromC)
    
    while True:
        try:
            SAMPINFO = queueGUI.get(timeout = 10)   #SAMPINFO[] = [<Info_from_picolog>,<voltage>,<current>,<UTC>,<CPUTime>,<remainingTime>,<state>,<samplesDone>]
        except queue.Empty:
            print('loop  -> ErrorNum; 022')
            sched.shutdown(wait = False)            #it stops schedulers without waiting the conclusion of him last statement   
            queueGUI.task_done()                    #it closes the shared buffer
            sys.exit(1)

        
        #------ converting data operations from PicoLog ----------#
            
        #controlInfoPico[] = <temperature,  state of charger relay,  state of load relay>
              
        controlInfoPico[0] = SAMPINFO[0] & maskFourBytes   

        for Bytes in range(totalInfo-1):    
            SAMPINFO[0] = SAMPINFO[0] >> 32
            controlInfoPico[Bytes + 1] = (SAMPINFO[0] & maskFourBytes)

        
        controlInfoPico[0] = controlInfoPico[0]*(picoVoltageRange/(pow(2,(Nbit-1))))*Coeff  #Temperature conversion
        controlInfoPico[1] = controlInfoPico[1]*(picoVoltageRange/(pow(2,(Nbit-1))))        #Charger relay state conversion
        controlInfoPico[2] = controlInfoPico[2]*(picoVoltageRange/(pow(2,(Nbit-1))))        #Load relay state conversion
        deltaQ = deltaQ + (SAMPINFO[2]*infoTest[2])/3600                                    #Charge extracted/inserted in the cell under test in Ah

        
        #----------Updating GUI interfaces ----------------#

        GUI = [str(SAMPINFO[1]),str(SAMPINFO[2]),str(SAMPINFO[3]),str(SAMPINFO[4]),str(SAMPINFO[5]),str(deltaQ),str(controlInfoPico[0])] #it creates a tuple with the information and format need to GUI

        try:
            GUITable[1][9].config(text = GUI[0])    #Voltage
            GUITable[1][10].config(text = GUI[1])   #Current
            GUITable[1][11].config(text = GUI[5])   #totalQ
            GUITable[1][12].config(text = GUI[2])   #UTC  
            GUITable[1][13].config(text = GUI[3])   #CPU_TIME
            GUITable[1][14].config(text = GUI[6])   #Temperature
            GUITable[1][17].config(text = GUI[4])   #remaining time
            GUITable[0].update()
        except:
            sched.remove_job('MEASURE')
            sched.shutdown(wait = False)        #it stops schedulers without waiting the conclusion of him last statement   
            queueGUI.task_done()                #it closes the shared buffer
            sys.exit(1)

        #--------- Writing on textual log file -------------#
        
        if infoTest[1] == 1:
            text = GUI[2] + '\t' + GUI[3] + '\t' + GUI[0] + '\t' + GUI[1] +'\t' + GUI[5] + '\t' + GUI[6] + '\n'
            logFile.write(text)

        #--------- Errors management and Stop conditons ----------------------#
               
        if SAMPINFO[6] == 'stp':                #if state field is 'stp' any error occurs, it stops only scheduler and goes on
            sched.shutdown(wait = False)        #it stops schedulers without waiting the conclusion of him last statement   
            queueGUI.task_done()                #it closes the shared buffer
            break
        elif SAMPINFO[6] == 'err':              #if state field is 'err' an error occur so it stops scheduler and exit
            sched.shutdown(wait = False)        #it stops schedulers without waiting the conclusion of him last statement   
            queueGUI.task_done()                #it closes the shared buffer
            sys.exit(1) 

        
        if (controlInfoPico[0] < TempMin) or (controlInfoPico[0] > TempMax):    #It verifies that the safety temperature range is respect.
            print('loop -> Error num: 024')
            sched.remove_job('MEASURE')
            sched.shutdown(wait = False)        #it stops schedulers without waiting the conclusion of him last statement   
            queueGUI.task_done()                #it closes the shared buffer
            sys.exit(1)

        #------ discharge --------#
            
        if infoTest[0] == 'discharge':

            if (infoTest[2] >= 2):                                                                                  #if samplesTime is bigger than 1.5s Python  waits the first sample  before verifies if there is some issues on relays state
                if (SAMPINFO[7] > 0) and ((controlInfoPico[1] > releTh) or (controlInfoPico[2] < releTh)):          #it verifies the relay state 
                    print('loop (discharge) -> ErrorNum; 25')
                    error = True
            elif (infoTest[2] < 2):                                                         
                if (SAMPINFO[7] > 1) and ((controlInfoPico[1] > releTh) or (controlInfoPico[2] < releTh)):      #if samplesTime is smaller than 2s, Python wait 3 samples before abort the program, 
                    print('loop (discharge) -> ErrorNum; 25')                                                   #to avoid some mistake due to transaction of voltage and current when changing step
                    error = True                                                                                #it verifies the relay state 

            if (error == False) and (infoTest[2] >= 2):
                if (SAMPINFO[7] > 0) and (SAMPINFO[1] > (infoTest[5] + 0.1)) and (SAMPINFO[2] < infoTest[6]):   #if samplesTime is bigger than 1.5s Python  waits the first sample  before verifies if there is some issues on the power line
                    print('loop (discharge) -> ErrorNum 026')
                    error = True
            elif (error == False) and (infoTest[2] < 2):
                if (SAMPINFO[7] > 1) and (SAMPINFO[1] > (infoTest[5] + 0.1)) and (SAMPINFO[2] < infoTest[6]):   #if samplesTime is smaller than 2s, Python wait the first 3samples before abort the program,
                    print('loop (discharge) -> ErrorNum 026')                                                   #to avoid some mistake due to transaction of voltage and current when changing step                            
                    error = True

            if error == True:
                sched.remove_job('MEASURE')
                sched.shutdown(wait = False)        #it stops schedulers without waiting the conclusion of him last statement   
                queueGUI.task_done()                #it closes the shared buffer
                sys.exit(1)
            elif error == False:
                if (SAMPINFO[7] > 1) and (SAMPINFO[1] <= (infoTest[5] + 0.1)) and (SAMPINFO[2] < infoTest[6]): #After the first 3 samples, it verifies the discharge stop condition
                    sched.shutdown(wait = False)
                    queueGUI.task_done()
                    break
                

        #------measure------- #

        elif infoTest[0] == 'measure':
            if (infoTest[2] >= 2):                                                                          #if samplesTime is bigger than 1.5s Python  waits the first sample  before verifies if there are some relay issues                if (SAMPINFO[7] > 0) and ((controlInfoPico[1] > releTh) or (controlInfoPico[2] > releTh)):  #it verifies the relè state in this subcase relè Charger OFF and relè load OFF
                    if (SAMPINFO[7] > 0) and ((controlInfoPico[1] > releTh) or (controlInfoPico[2] > releTh)):
                        print('loop (measure)-> ErrorNum; 25')
                        error = True
            elif (infoTest[2] < 2):                                                                         #if samplesTime is smaller than 2s, Python wait the first 3 samples before abort the program,
                if (SAMPINFO[7] > 1) and ((controlInfoPico[1] > releTh) or (controlInfoPico[2] > releTh)):  #to avoid some mistake due to transaction of voltage and current when changing step
                    print('loop (measure)-> ErrorNum; 25')                                                  #it verifies the relay state 
                    error = True

            if error == True:
                sched.remove_job('MEASURE')
                sched.shutdown(wait = False)        #it stops schedulers without waiting the conclusion of him last statement   
                queueGUI.task_done()                #it closes the shared buffer
                sys.exit(1)

        #----- charge -------#

        elif infoTest[0] == 'charge':
            if (infoTest[2] >= 2):                                                                          #if samplesTime is bigger than 1.5s Python  waits the first sample before verifies  if there is a state relays error
                if (SAMPINFO[7] > 0) and ((controlInfoPico[1] < releTh) or (controlInfoPico[2] > releTh)):  #it verifies the relay state 
                    print('loop (charge) -> ErrorNum; 25')
                    error = True
            elif (infoTest[2] <= 2):
                if (SAMPINFO[7] > 1) and ((controlInfoPico[1] < releTh) or (controlInfoPico[2] > releTh)):  #if samplesTime is smaller than 2s, Python wait the first 3 samples before abort the program,
                    print('loop (charge) -> ErrorNum; 25')                                                  #to avoid some mistake due to transaction of voltage and current when changing step
                    error = True                                                                            #it verifies the relay state

            
            if (infoTest[2] >= 2):
                if (SAMPINFO[7] > 0) and (SAMPINFO[1] < (infoTest[5] - 0.1)) and ((-SAMPINFO[2]) <= infoTest[6]):   #if samplesTime is bigger than 1.5s Python  waits the first sample  before verifies if there is some issues on the power line
                    print('loop (charge) -> ErrorNum 026')
                    error = True
            elif (infoTest[2] < 2):
                if (SAMPINFO[7] > 1) and (SAMPINFO[1] < (infoTest[5] - 0.1)) and ((-SAMPINFO[2]) <= infoTest[6]):   #if samplesTime is smaller than 1.5s Python wait the first 3 samples before abort the program,
                    print('loop (charge) -> ErrorNum 026')                                                          #to avoid some mistake due to transaction of voltage and current when changing step
                    error = True

            if error == True:
                sched.remove_job('MEASURE')
                sched.shutdown(wait = False)        #it stops schedulers without waiting the conclusion of him last statement   
                queueGUI.task_done()                #it closes the shared buffer
                sys.exit(1)
            elif error == False:
                if (SAMPINFO[7] > 2) and (SAMPINFO[1] >= (infoTest[5] - 0.1)) and ((-SAMPINFO[2] ) <= infoTest[6]): #After the first 3 samples, it verifies the charge stop condition
                    sched.shutdown(wait = False)
                    queueGUI.task_done()
                    break
    
    
    #if log is enables it close file and say C that it has to close file log
    if infoTest[1] == 1:
        logFile.close()
        st.sendEndFile(sockC)
                                                                           


#-------------- readAndAckt()-------------------------------------------#                                                                       
# First, This function allows the user to choose the file log's paths where program saves data. Second, the function scans the control raws to understand
# if there are writing mistake in the textual file. Then the program updates the GUI interfaces, writes log-file's header, starts loop() function which perform the periodically data acquisition from instruments.

#Prototype: readAndAckt(ipA,portN,skPi)
#-----Arguments-------#

#   skPi        ->  Picolog's socket identifier
#   ipA         ->  it is a 1x2 tuple ipA = [<charger's ip Address>, <load's ip address>]
#   portN       ->  it is a 1x2 tuple portN = [<charger's port No>, <load's portNo>]
#----return-------#
#   This function doesn't return nothing

def readAndAckt(ipA,portN,skPi):
    #global timeBeforeEnd

    #-------- Init variables -----------#
    numStep = 1
    totalStep = 0
    VerifySamplesTime = 0
    AcctuallysocketTTi = 0

    #-------- Reading Picolog settings -------------------#
    print('Reading technical information about PicoLog.....', end = '.' , flush=True)
    
    with open("../../Setting_File/picologinfo.txt") as picoInfoFile:     #It opens and transfers the picologinfo.txt's content into picoInfo variable and then closes the file
        picoInfo = picoInfoFile.read()
        picoInfoFile.close()

    picoInfoRaw = picoInfo.splitlines()                                 #This function splits the file's raw
    print('DONE')
    
    #-------- Check Writing error -----------------------#
    print('Cheking  insertion errors.....', end = '.' , flush=True)

    for i in range(len(picoInfoRaw)):                                   #it reads and saves in some variables some information about Picolog unit and its connect devices
        if picoInfoRaw[i] != '':
            if picoInfoRaw[i][0] != '#':                                #If it isn't a empty line or a commented line that raw contains some information
                instrumentInfo = picoInfoRaw[i].split()
                if instrumentInfo[0] == 'VoltageRange:':                #it insert the information about analog-channel's input voltage range of Picolog into voltageRange variable
                    voltageRange = float(instrumentInfo[1])
                elif instrumentInfo[0] == 'Nbit:':                      #it insert the information about the number of bit use to conversion in the Picolog's analog channel, into numBit variable
                    if (float(instrumentInfo[1]) < 0):
                        print('readAndAckt -> Error num: 011')
                        sys.exit(1)
                        
                    numBit = float(instrumentInfo[1])                   
                elif instrumentInfo[0] == 'RelèThreshold:':             #it insert the information about the analog relays threshold to separates the ON-state from OFF-state, into threshold variable
                    threshold = float(instrumentInfo[1])
                elif instrumentInfo[0] == 'TempRange:':                 #it insert the limits of safety temperature range where the Li-ion cell work correctly in Tmin,Tmax variables
                    temp = instrumentInfo[1].split(';')
                    if (float(temp[0]) < 0) or (float(temp[1]) < 0):    #the insert values have to be positive
                        print('readAndAckt -> Error num: 012')
                        sys.exit(1)
                    if float(temp[0])  > float(temp[1]):                #The Tmin values have to be smaller than Tmax values
                        print('readAndAckt -> Error num: 013')
                        sys.exit(1)
                        
                    Tmin = float(temp[0])
                    Tmax = float(temp[1])
                elif instrumentInfo[0] == 'Conversion:':
                    conversion = float(instrumentInfo[1])
                    break
    print('DONE')
    
    #------- Open command Textual file --------------------#
    
    print('Please select textual Step-file....', end = '.' , flush=True)

    try:
        with open(ph.pathStepFile()) as stepFile:           #through pathStepFile function, it allows the user to choose the absolute path of textual step-file which contains the step commands
            my_file = stepFile.read()                       #It opens file and transfers it in the my_file variables and than closes file.
            splitrow = my_file.splitlines()                 #It split the file's raw in splitrow variable
            stepFile.close()
    except TypeError:                                       #this exception occurs when operator inserted an inexistent file's path.
        sys.exit(1)
    

    print('DONE')

    #-------Cheking Error ---------------------------------#

    print('Cheking command errors.....',end = '.' , flush=True)
        
    for i in range(len(splitrow)):
        if splitrow[i] != '':
            if splitrow[i][0] != '#':
                if splitrow[i][0] == 'c' or splitrow[i][0] == 'm' or splitrow[i][0] == 'd': #The rows is an information row, only if rows stars with 'c','d','m' character
                        infoTest = splitrow[i].split()                                      #Split command row in infotest variable. infoTest = [<type of measure>,<EnLog>,<samplesTime>,...
                                                                                            #                                                   ...<Duration>,<limit current>,<limit voltage>,...
                                                                                            #                                                   <stop test current>]

                        totalStep = totalStep + 1                                           #At the end of this procedure, totalStep indicates how many step compound the test
                        if len(infoTest) < 7:
                            print('readAndAckt -> Error num: 014'+ '  ' + 'command row = ' + str(totalStep))
                            sys.exit(1)
    
                        if float(infoTest[3]) < 0.5:
                            if infoTest[3] != '-1':
                                print('readAndAckt -> Error num: 015'+ '  ' + 'command row = ' + str(totalStep))
                                sys.exit(1)

                        elif ((float(infoTest[3]) % float(infoTest[2])) != 0):                              #The test's length must be a multiple of 0.5
                            print('readAndAckt -> Error num: 016'+ '  ' + 'command row = ' + str(totalStep))
                            sys.exit(1)

                        elif (float(infoTest[3]) < float(infoTest[2])):                      #the test's length must be bigger than sample time
                            print('readAndAckt -> Error num: 019'+ '  ' + 'command row = ' + str(totalStep))
                            sys.exit(1)
        
                        if (float(infoTest[2]) < 0.5) or (float(infoTest[2]) > 2):                              #Sample time must be between 0.5 s and 2s
                            print('readAndAckt -> Error num: 017'+ '  ' + 'command row = ' + str(totalStep))
                            sys.exit(1)
                            
                        elif (float(infoTest[2]) % 0.5 != 0):                                                   #Sample time must be a multiple of 0.5s
                            print('readAndAckt -> Error num: 018' + '  ' + 'command row = ' + str(totalStep))
                            sys.exit(1)

                        if (infoTest[0] != 'charge') and  (infoTest[0] != 'discharge') and (infoTest[0] != 'measure'):   #it indicates if there are some writing mistakes
                                print('readAndAckt -> Error num: 020' + '  ' + 'command row = ' + str(totalStep))
                                sys.exit(1)

                        if (infoTest[1] != '1') and (infoTest[1] != '0'):                                       #EnLog values have to be 1 or 0
                            print('readAndAckt -> Error num: 021' + '  ' + 'command row = ' + str(totalStep))
                            sys.exit(1)      


                        


    if totalStep == 0:                              #If totalStep is zero it does means that there are some writing error or there aren't command
        print('readAndAckt  -> Error num: 20')
        sys.exit(1)
        
    print('DONE')

    #------------ Choosing absolute path of instruments log file --------------------------#
    try:
        print('Please select the instrument textual log-file....', end = '.' , flush=True)            
        pathLogDir = ph.logDir('Select dir for instrument log', '../../Log_File/Instrument_log')    #it allows user to choose the directory where to save data from charger and load
        print('DONE')
        print('Please select the Picolog textual Step-file....', end = '.' , flush=True)
        pathLogDirPico = ph.logDir('Select dir for Pico log','../../Log_File/Picolog_log')          #it allows user to choose the directory where to save data from Picolog
        print('DONE')
        pathFileInst = pathLogDir + '/Test_description_' + str(numStep) + '.txt'                   #it adds to path the log-file's name
        pathFilePico = pathLogDirPico + '/Test_description_' + str(numStep) + '.txt'               #it adds to path the log-file's name
        ph.sendPath(skPi,pathFilePico)                                                             #it sends the path of picolog's file-log destination to C-thread
    except TypeError:
        sys.exit(1)

    #------------ Ackt phase --------------#
    
    try:
                                
        GUIInfo = it.initGUI()                              #Initializing GUI interface         
        GUIInfo[1][20].config(text = str(totalStep))        #it inserts the total step information to GUI

        for i in range(len(splitrow)):
            if splitrow[i] != '':
                if splitrow[i][0] != '#':
                    if splitrow[i][0] == 'c' or splitrow[i][0] == 'm' or splitrow[i][0] == 'd':                 #The rows is an information row, only if rows stars with 'c','d','m' character
                        command = splitrow[i].split()                                                           #Split command row in infotest variable. infoTest = [<type of measure>,<EnLog>,<samplesTime>,... 
                                                                                                                #                                                   ...<Duration>,<limit current>,<limit voltage>,...
                                                                                                                #                                                   <stop test current>]
                        #--------- Updating GUI interface with current step row information -------#
                                                                                                                
                        GUIInfo[1][19].config(text = str(numStep))
                        GUIInfo[1][0].config(text = str(numStep))
                        GUIInfo[1][1].config(text = command[0])
                        if command[1] == '1':
                            GUIInfo[1][2].itemconfig(GUIInfo[1][3],fill = 'green2')                 #if enLog field is enable, the corresponding led is green
                        elif command[1] == '0':
                           GUIInfo[1][2].itemconfig(GUIInfo[1][3],fill = 'red2')                    #if enLog field is disable, the corresponding led is red                  
                      
                        
                        GUIInfo[1][4].config(text = command[2])
                        GUIInfo[1][5].config(text = command[3])
                        GUIInfo[1][6].config(text = command[4])
                        GUIInfo[1][7].config(text = command[5])
                        GUIInfo[1][8].config(text = command[6])
                        GUIInfo[0].update()          

                        startTest = time.strftime("%d/%b/%Y %H:%M:%S",time.localtime())             #it picks date and time information
                        startTestTime = startTest.split()                                           #startTestTime = <Day>,<Time>
                    
                        GUIInfo[1][15].config(text = startTestTime[1])
                        GUIInfo[1][16].config(text = startTestTime[0])
                        GUIInfo[0].update()

                        
                    
                        #-------- Creating text header file ---------------------------#
                        textHeader = '#Test step:\t' + str(numStep) + '\tType of step: ' + command[0] + '\t\tstarted on:\t' + startTest
                        textHeader = textHeader + '\n#local\t\tinstument\n' + 'timestamp\tclock_tick[s]\tV[V]\tI[A]\tQ[C]\tTemp[°C]\t\n'

                        #-------- Setting instrument phase before the test execution ---------#
                        AcctuallysocketTTi = st.setBeforeStart(ipA,portN,skPi,command)
                        
                        #-------- Looping phase --------------#
                        try:
                            if command[1] == '1':                               #it checks if enLog is ON
                                try:
                                    picoLogFile = open(pathFileInst,'w')        #If yes, it opens a log file and writes the header in it
                                    picoLogFile.write(textHeader)
                                except:
                                    print('Error Opening File!!')
                                    sys.exit(1)
                            else:
                                picoLogFile = 'file_not_open'

                            
                            command = [command[0],float(command[1]),float(command[2]),float(command[3]),float(command[4]),float(command[5]),float(command[6])]      #it converts numeric commands (from 1 to 6) from string to float format

                             
                            if numStep == 1:                            #Only at first step, it sends start request to C-thread to starts picolog sampling
                                st.sendStart(skPi)
                                #timeBeforeEnd = time.perf_counter()    #While start request has been sent, It takes time.
                            
                            
                            loop(skPi,AcctuallysocketTTi,command,picoLogFile,GUIInfo,Tmin,Tmax,threshold,numBit,voltageRange,conversion,numStep)
                            
                             
                           
                        except:                                                                  #At this point one of  charger's, load's is enabling, so if there is an error it may be necessary distinguish what current step type is; Then,
                                                                                                 #program switches off the TTi's output/input. 
                            try:
                                if command[0] == 'charge':
                                    AcctuallysocketTTi.sendall(bytes('OP1 0\n','utf-8'))         #If there is an error, it switches OFF the charger output
                                    AcctuallysocketTTi.close()
                                else:
                                    AcctuallysocketTTi.sendall(bytes('INP 0\n','utf-8'))         #If there is an error, it switches OFF the load input
                                    AcctuallysocketTTi.close()
                            except BrokenPipeError: 
                                AcctuallysocketTTi.close()

                            
                            if command[1] == 1:             #if enLog was active, Python would send the End file request to C-thread to close log-file
                                picoLogFile.close()
                                st.sendEndFile(skPi)
                                
                            sys.exit(1)

                        #--------- Resetting instrument phase after an execution of one step--------#
                        
                        st.resetAfterStop(skPi,AcctuallysocketTTi,command)
                                                                    
                        #-------- Post looping phase -----------------------#
                            
                        numStep = numStep + 1
                        pathFileInst = pathLogDir + '/Test_description_' + str(numStep) + '.txt'      #updating Id of next step on absolute file log path
                       
                                                                                                                                      
    except SystemExit:
        try:
            GUIInfo[1][21].itemconfig(GUIInfo[1][22], fill = 'red2')                #if an exception occur both led in GUI interface come red
            GUIInfo[1][23].itemconfig(GUIInfo[1][24], fill = 'red2')
            GUIInfo[0].update()
        except:
            sys.exit(1)

        sys.exit(1)

  

        
    if totalStep == (numStep-1):
        GUIInfo[1][23].itemconfig(GUIInfo[1][24], fill = 'red2')
        GUIInfo[0].update()

   
        
    

#-------- Mainloop() --------------#  

def main():
    #-------- intialization Variables ---------#

    infopicolog = [0,0]   #it is a tuple that contain some information about child thread. infopicolog = [<pid>,<Picolog's socket>]
    infoCharger = [0,0]   #it is a tuple that contain some information about charge's ip address and port number. infoCharger = [<ip>,<port>]
    infoLoad = [0,0]      #it is a tuple that contain some information about charge's ip address and port number. infoCharger = [<ip>,<port>]

    #------- Initialization phase -----------#

        #---Instrumentation---#
    try:
        
        print('Start instrument...')
        print('Starting Charge (QPX1200SP).....', end = '.', flush=True)
        infoCharger = it.initCharger()                                             #it creates QPX1200SP's socket interface, and resets charger infoCharger = [<ip>,<port>]
        print('DONE')
        print('Starting Load (LD400P).....', end = '.' , flush=True)   
        infoLoad = it.initLoad()                                                   #it creates LD400P's socket interface, and resets load infoLoad = [<ip>,<port>] 
        print('DONE')     
        print('CAUTION: Starting picolog may require 1min 30sec, the first time.')
        print('Starting PicoLog.....',end='.')
        infoPicoLog = it.startPicoLog()                                 #it creates C-thread's socket interface, and Opens the Picolog
        print('DONE')
    
        pidC = infoPicoLog[0]                   #Pid's child information
        skPicoLog = infoPicoLog[1]              #C-thread socket identifier
        ip = [infoCharger[0],infoLoad[0]]       #tuple that contains ip-address of TTi instruments ip = [<charger's ip>,<load's ip>]
        port = [infoCharger[1],infoLoad[1]]     #tuple that contains port-numbers of TTi instruments port = [<charger's port>,<load's port>]

        #-------- external device settings --------#
        try:
            it.initRelè(skPicoLog)                  #Relays initialization
            it.initTemp(skPicoLog)                  #Temperature sensor initialization
        except SystemExit:       
            try:
                st.sendExit(skPicoLog)                              #it sends exit request to C-thread to kill him
                pidC.wait(timeout = 10)	                            #it waits the termination of child thread about 10sec then rising an exception
                skPicoLog.close() 
            except BrokenPipeError:
                skPicoLog.close()                                   #if the program try to Kill th child  while the child isn't on-line anymore, the program close the socket anyway
            except subprocess.TimeoutExpired:
                print('C-thread has been forcing to exit...', end = '.' , flush=True)
                pidC.terminate()                                    #it kills the child thread
                print('DONE')
            sys.exit(1)


    #-------------- Executing phase ---------------------#
            
        try:
            readAndAckt(ip,port,skPicoLog)   
        except SystemExit:
            try:
                st.sendExit(skPicoLog)                          #it sends exit request to C-thread to kill him
                pidC.wait(timeout = 10)	                        #it waits the termination of child thread about 10sec then rising an exception
                skPicoLog.close() 
            except BrokenPipeError:
                skPicoLog.close()              
            except subprocess.TimeoutExpired:
                print('C-thread has been forcing to exit...', end = '.' , flush=True)
                pidC.terminate()                                    #it kills the child thread
                print('DONE')
            sys.exit(1)
    
    #------------- Releasing resurses acquired --------------#
        st.sendExit(skPicoLog)          #it sends Exit request to C-thread          
        skPicoLog.close()               #it close C-thread's socket
        try:
            pidC.wait(timeout = 10)	                        #it waits the termination of child thread about 10sec then rising an exception
        except TimeoutExpired:
            print('C-thread has been forcing to exit...', end = '.' , flush=True)
            pidC.terminate()                                #it kills the child thread
            print('DONE')
        
        print('GOOD NEWS: Test ends correctly.')
        print('\nPlease press q to exit')                   #it is need to avoid lxterminal auto-closing at the end of test execution
        while 'q' != input():
            print('\nPlease press q to exit')
        

    except SystemExit:
        print('\nPlease press q to exit')                   #it is need to avoid lxterminal auto-closing t the end of test execution
        while 'q' != input():
            print('\nPlease press q to exit')


#------------------- STARTING MAIN FUNCTION ------------------------#
 
main()       
         
                



        
      
       
        
  
    

    


    
