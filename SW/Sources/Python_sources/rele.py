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
#---------------- BUILT-IN Python modules -----------------------#
import sys
import socket
import instrument as st

#-------------------- Switching OFF relays -------------------------#
# switchOff() function switches OFF relays. It sends a switching OFF relay request to Child thread and waits Ack response.
# Prototype: switchOff(sockC)
#------Args--------------#
#   sockC       -> Child-thread's identifier
#------Return------------#
#    any

def switchOff(sockC):
    
    message = 'Relè 00\r\n'                     #Format request is: Relè <state_relay_charger,state_relay_load>\r\n
    try:
        sockC.sendall(bytes(message,'utf-8'))
        recvMessage = str(sockC.recv(100),'utf-8')
    except socket.timeout:
        print('switchOff -> Error num: 001')
        sys.exit(1)
    except:
        print('switchOff -> Error num: 002')
        sys.exit(1)
    
    Crisp = recvMessage.split('\r\n')
    if Crisp[0] != 'Ack':
        print('switchOff -> Error num: 006')
        sys.exit(1)

#-------------------- Switching ON relays -------------------------#
# switchOn() function switches ON relays.If the current test is a charge step. it switches ON the charge relay; if the current step is a discharge step, it switches ON the load relay .
#First it sends a switching ON relay request to Child thread and waits Ack response.
# Prototype: switchOff(sockC,stepMode)
#------Args--------------#
#   sockC       -> Child-thread's identifier
#   stepMode    -> it indicates the type of current step
#------Return------------#
#    any

def switchOn(sockC,stepMode):
   
    if stepMode == 'charge':                            
        message = 'Relè 10\r\n'                              #Format request is: Relè <state_relay_charger,state_relay_load>\r\n   
        try:
            sockC.sendall(bytes(message,'utf-8'))
            recvMessage = str(sockC.recv(100),'utf-8')
        except socket.timeout:
            print('switchOn -> Error num: 001')
            sys.exit(1)
        except:
            print('switchOn -> Error num: 002')
            sys.exit(1)

        Crisp = recvMessage.split('\r\n')
        if Crisp[0] != 'Ack':
            print('switchOn -> Error num: 006')
            sys.exit(1)
            
    elif stepMode == 'discharge':
        message = 'Relè 01\r\n'                             #Format request is: Relè <state_relay_charger,state_relay_load>\r\n
        try:
            sockC.sendall(bytes(message,'utf-8'))
            recvMessage = str(sockC.recv(100),'utf-8')
        except socket.timeout:
            print('switchOn -> Error num: 001')
            sys.exit(1)
        except:
            print('switchOn -> Error num: 002')
            sys.exit(1)

        Crisp = recvMessage.split('\r\n')
        if Crisp[0] != 'Ack':
            print('switchOn -> Error num: 006')
            sys.exit(1)


    
    
