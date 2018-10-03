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
#---------------- BUILT-IN Python modules ------------------------#
import tkinter
import tkinter.filedialog
import sys
import socket



#--------------- Setting of absolute path of step-file--------------------#
# pathStepFile() is a function that allows user to choose the path of step-file through a GUI. The function return the select path
# Prototype: pathStepFile()
#----Args------#
#    Any
#----Return----#
#   pathStep -> return the absolute step-file's path

def pathStepFile():
    try:
        root = tkinter.Tk()
        root.withdraw()
        pathStep = tkinter.filedialog.askopenfilename(parent=root, initialdir='../../Step_File', title='Select a step file')
    except:
        sys.exit(1)
        
    return pathStep

#--------------- absolute path of Log-file--------------------#
# pathsLogFile() is a function that allows user to choose the path of log-file through a GUI. The function return the select path
# Prototype: pathsLogFile()
#----Args------#
#    Any
#----Return----#
#   pathLog -> return the absolute step-file's path

def pathsLogFile():
    try:
        root = tkinter.Tk()
        root.withdraw()
        pathLog = tkinter.filedialog.askopenfilename(parent=root, initialdir='../../Log_File', title='Select a step file')
    except:
        sys.exit(1)
        
    return pathLog

#--------------- absolute path of directory where saving Log-file--------------------#
# logDir() is a function that allows user to choose the path of directories where saving Log-file through a GUI. 
# Prototype: logDir()
#----Args------#
#    tktitle    -> Title of Graphical user interfaces,
#    tkDir      -> Starting directory 
#----Return----#
#    pathLog -> return the absolute Log-dir's path

def logDir(tktitle,tkDir):
    try:
        root = tkinter.Tk()
        root.withdraw()
        pathLog = tkinter.filedialog.askdirectory(parent=root, initialdir=tkDir, title=tktitle)
    except:
        sys.exit(1)
        
    return pathLog


#---------------Sending path information to child thread ---------------------------#
# sendPath() function sends path information to child thread. 
#Prototype: sendPath(sockC,path)
#------------ Args -----------------#
#    sockC  ->  child-thread's  Socket identifier
#    path   ->  absolute path to sending
#------------Return-----------------#
#    Any

def sendPath(sockC,path):
    pathCommand = 'Path ' + path +' \r\n'           #Path: <absolute_file_path>
    sockC.sendall(bytes(pathCommand,'utf-8'))

    try:
        recvMessage = str(sockC.recv(100),'utf-8')
    except socket.timeout:
        print('sendPath -> Error num: 001')
        sys.exit(1)

    recvMessage = recvMessage.split('\r\n')
    
    if recvMessage[0] != 'Ack':  
        print('sendPath -> Error num: 006')
        sys.exit(1)



