/*
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
	
	
	
#This product uses an external not-GPL library (HRDL.h) to control the Picolog ADC-24 DAQ board.
#All information about library and its installation are provided in the TWIST-usermanual.
#For other information consult the web pages: https://www.picotech.com/support/topic14649.html (libusbdrdaq package)
											  https://www.picotech.com/data-logger/adc-20-adc-24/precision-data-acquisition
 
*/

#include "./library/HRDL.h"
#include "./library/init.h"

using namespace std;

/**** 
 * initSocket creates a socket connection at precise address and port
 * the prototype is int initSocket(int* sockfd, const char* address,int portno)
 * ------ arguments ---------
 * 		*sockfd = socket identifier
 * 		*address = IP address
 *  	portno = number of port
 * ------ return -----------
 * 		the function return the connected socket's identifier
 ****/  

int initSocket(int* sockfd, const char* address, int portno){
	
	int newsockfd,ret;
    socklen_t clilen;
    struct sockaddr_in serv_addr, cli_addr;
    
	//cout << "socket\n";
    *sockfd = socket(AF_INET, SOCK_STREAM, 0);   //it creates socket
    if (*sockfd < 0){ 
       //cout << "ERROR opening socket\n";
       pthread_exit(NULL);
    }
    
    //it allows to skip the OS error that rise when we do a bind after a previously one
    int yes=1;
	if (setsockopt(*sockfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes)) == -1) {
		perror("setsockopt");
		pthread_exit(NULL);
	}
	
	 memset(&serv_addr,0,sizeof(serv_addr)); 
	 memset(&cli_addr,0,sizeof(cli_addr));
	 
     serv_addr.sin_family = AF_INET;
     serv_addr.sin_port = htons(portno);
     inet_pton(AF_INET,address, &serv_addr.sin_addr.s_addr); //it convert IPv4 and Ipv6 addresses from text to binary form
     
	 //cout << "bind\n";
     ret = bind(*sockfd, (struct sockaddr*) &serv_addr,sizeof(serv_addr)); //it associates the IP address and port num  to socket
     if(ret == -1){
		//cout << "ERRORE bind\n";
		exit(1);
	 }
	 
	 //cout << "listen\n";
	 ret = listen(*sockfd,LIST_PENDENT_CONNECTIONS); //it listens some possible connections 
	 if(ret == -1){
		//cout << "ERRORE listen\n";
		exit(1);
	 }
     
     clilen = sizeof(cli_addr);
    
     
     //cout << "accept\n";
     newsockfd = accept(*sockfd,(struct sockaddr *) &cli_addr, &clilen); //it accepts a connection
     if (newsockfd < 0){ 
         //cout << "ERROR on accept\n";
		 exit(1);
     }
               
     return newsockfd; //it returns the connected socket
	
	
}


/**** 
 * initPico setup the picolog unit
 * the prototype is int8_t initPico(int16_t* openUnit, int16_t* numberOfChannels)
 * ------ arguments ---------
 * 		*openUnit = identifier of unit
 * 		*numberOfChannels = total number of enable channels
 * ------ return -----------
 * 		the function return "true" is all ok, otherwise "false"
 ****/  

int8_t initPico(int16_t* openUnit, int16_t* numberOfChannels){

	int16_t noiseRejection,stateChannel,enableChannel,activeChannel,range,setDigitalChannel,directionOut,directionOutState,enableDigitIn;
	int8_t flag_fail = false, all_ok = true;
	*numberOfChannels = 0;
	
	
	*openUnit = HRDLOpenUnit();							//it open the unit (the first time it takes 1min and 30sec to open). 
	if(*openUnit <= 0){									//if the first time the picolog fails to open, we try again
		*openUnit = HRDLOpenUnit();						
		if(*openUnit <= 0){								//if picolog still not open the programm exit		
			flag_fail = true;
		}
	}
	
	if(flag_fail == false){		
		noiseRejection = HRDLSetMains(*openUnit,NOISE_REJECTION); //it set noise rejection to 50 Hz
		if(noiseRejection <= 0)
			flag_fail = true;
	}
	
	//it set analog channel n°1
	if(flag_fail == false){
		activeChannel = HRDL_ANALOG_IN_CHANNEL_1; 
		enableChannel = SET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t) SINGMODE);	
		if(stateChannel <= 0)
			flag_fail = true;
	}
	
	//it set analog channel n°2
	if(flag_fail == false){
		activeChannel = HRDL_ANALOG_IN_CHANNEL_2; 
		enableChannel = SET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t) SINGMODE);	
		if(stateChannel <= 0)
			flag_fail = true;
	}
	
	
	//PROCEDURE to set analog channel n°3/4 (diff mode)
	if(flag_fail == false){
		activeChannel = HRDL_ANALOG_IN_CHANNEL_4; 
		enableChannel = RESET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t)DIFFMODE);
		if(stateChannel <= 0)
			flag_fail = true;
	}
   
    
    if(flag_fail == false){
		activeChannel = HRDL_ANALOG_IN_CHANNEL_3; 
		enableChannel = SET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t) DIFFMODE);	
		if(stateChannel <= 0)
			flag_fail = true;
	}
	
	//it set analog channel n°5
	if(flag_fail == false){
		
		activeChannel = HRDL_ANALOG_IN_CHANNEL_5; 
		enableChannel = SET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t) SINGMODE);	
		if(stateChannel <= 0)
			flag_fail = true;
	}
	
	
	//it set analog channel n°6
	if(flag_fail == false){
		activeChannel = HRDL_ANALOG_IN_CHANNEL_6; 
		enableChannel = SET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t) SINGMODE);	
		if(stateChannel <= 0)
			flag_fail = true;
	}

	
	//it set analog channel n°7
	if(flag_fail == false){
		activeChannel = HRDL_ANALOG_IN_CHANNEL_7; 
		enableChannel = SET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t) SINGMODE);	
		if(stateChannel <= 0)
			flag_fail = true;
	}
	
	
	//it set analog channel n°8
	if(flag_fail == false){
		activeChannel = HRDL_ANALOG_IN_CHANNEL_8; 
		enableChannel = SET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t) SINGMODE);	
		if(stateChannel <= 0)
			flag_fail = true;
	}
	
	//it set analog channel n°9
	if(flag_fail == false){
		activeChannel = HRDL_ANALOG_IN_CHANNEL_9; 
		enableChannel = SET_CH; 
		range = HRDL_1250_MV;
		stateChannel = HRDLSetAnalogInChannel(*openUnit,activeChannel,enableChannel,range,(int16_t) SINGMODE);	
		//cout << "Esito impostazone canali analogici: " << stateChannel << "\n\n";
		if(stateChannel <= 0)
			flag_fail = true;
	}
	
	
	
	
	//it sets i/o port
	if(flag_fail == false){
		directionOut = HRDL_DIGITAL_IO_CHANNEL_1 + HRDL_DIGITAL_IO_CHANNEL_2 + HRDL_DIGITAL_IO_CHANNEL_3 + HRDL_DIGITAL_IO_CHANNEL_4;
		directionOutState = 0;
		enableDigitIn = RESET_CH;
		setDigitalChannel = HRDLSetDigitalIOChannel(*openUnit,directionOut,directionOutState,enableDigitIn);
		if(setDigitalChannel <= 0)
			flag_fail = true;
	}
	
	HRDLGetNumberOfEnabledChannels(*openUnit,numberOfChannels);
	
	
	 if(flag_fail == false){
		if(*numberOfChannels == ENABLE_CHANNELS){	//if there isn't errors and the num of channels is correct it set the flag all_ok to true 
			all_ok = true;
		}	
	}
	else{											//otherwise it sets the all_ok flag to false  
		all_ok = false;
	}

	return all_ok;
}	
