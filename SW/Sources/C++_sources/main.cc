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

#include "./library/init.h"
#include "./library/HRDL.h"

using namespace std;


struct settingPicoChannels{ 	//Structure that contain some info about picolog
	char dataPath[PATH_SIZE];	//the path of Log File of PicoLog
	int16_t picoID;				//Picolog unit ID
	int16_t numOfChannels;		//Num of enabled channel 
	int8_t  tempChannel;		//pos of analog channel where the temperature sensor is reads
	int8_t  chargeRele;			//pos of digital pin that control the charger relay
	int8_t  loadRele;			//pos of digital pin that control the load relay
	int8_t  checkReleLoad;		//analog channel where the state of load's relay is reads
	int8_t  checkReleCharge;	//analog channel where the state of charger's relay is reads
	int8_t  acquireLoop;		//it defines if the picolog is putting data samples
};

/*******
 *  Main() function creates a client that serves the request from python server at the socket address <127.0.0.1> and port <1234>
 *  and return 0 if all is ok 1 if there is some issues
 *******/

int main(){
	int8_t fakeFault = 0,retPico,acquireLoop = false;
    int16_t onOff,directionOut,directionOutState,enableDigitIn,overflow = 0,setInterval = 0;
    int32_t getValues = 0, python[3],error,sockPico,connSockPico,samples[ENABLE_CHANNELS*NUM_SAMPLES_PER_CHANNEL],samplesTime = 0,numConversions,ret,countWait,step;
    char writeMessage[BUFF_SIZE],readMessage[BUFF_SIZE];
    char *select = NULL, *token = NULL, *typeStep;
 
    
    
	ofstream fileLog;
	time_t rawtime;
	struct tm* timeInfo;
	char calendar[80];
	
	
	struct settingPicoChannels infoPico;
	
    connSockPico = initSocket(&sockPico,(const char*) "127.0.0.1",1234);	//socket initialization to Python script <127.0.0.1>,<1234>
     
    retPico = initPico(&infoPico.picoID,&infoPico.numOfChannels); //Initialization of PicoLog
    
    //if the picolog initialization is goes true it sends an Ack to the server, otherwise it sends a Nack to the server that aborts the execution of program
	if (retPico == true){
		memset(writeMessage,0,BUFF_SIZE);
		strncpy(writeMessage,"Ack\r\n",strlen("Ack\r\n"));
		ret = write(connSockPico, writeMessage, BUFF_SIZE);
		if(ret <= 0){
			close(connSockPico);
			close(sockPico);
			HRDLCloseUnit(infoPico.picoID);	
			exit(1);
		}
	}	
	else{											
		memset(writeMessage,0,BUFF_SIZE);
		strncpy(writeMessage,"nAck\r\n",strlen("nAck\r\n"));
		ret = write(connSockPico, writeMessage, BUFF_SIZE);
		if(ret <= 0){
			close(connSockPico);
			close(sockPico);
			HRDLCloseUnit(infoPico.picoID);	
			exit(1);
		}
	}

	infoPico.acquireLoop = false;  //Picolog is not in acquisition state
    samplesTime = SAMPTIME;			//it set the picolog sampling time
    directionOut = HRDL_DIGITAL_IO_CHANNEL_1 + HRDL_DIGITAL_IO_CHANNEL_2 + HRDL_DIGITAL_IO_CHANNEL_3 + HRDL_DIGITAL_IO_CHANNEL_4; //it set in output mode all the I/O port of picolog
    directionOutState = 0; 
    enableDigitIn = 0;				//All input of I/O port is disables
    python[0] = 0;					//Python[] is a vector that contain some information to sends to Python script like temperature, and relay's state
    python[1] = 0;
    python[2] = 0;
         
      
    while(true){  
		
		//cout << "Attesa comando...\n";																												
		memset(readMessage,0,BUFF_SIZE); 
		ret = read(connSockPico,readMessage,BUFF_SIZE); //it wait a request from python script
		if (ret <= 0){
			//cout << "ERROR reading from socket.\n";
			close(connSockPico);					//it close connected socket
			close(sockPico);						//it close socket
			directionOutState = 0; 					//Every I/O pin set to zero 
			HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
			if(infoPico.acquireLoop == true){	
				fileLog.close();					//it closes file
				HRDLStop(infoPico.picoID);			//It stops Picolog sampling
			}
				
			HRDLCloseUnit(infoPico.picoID);			//It closes pico
			exit(1);
		}
		
		//cout << readMessage << "\n";
	    
																																									
		if(strncmp(readMessage,"Relè",strlen("Relè")) == 0){  //This service set the relay's state (example request: <Relè 00> both relay off)
			error = false;
			select = strchr(readMessage,' '); 	//it searches the first ' ' character
			select++; 						  	//it increases of one the position of pointer, now it point the state of first relay
			onOff = *select - '0'; 				
			onOff = onOff << 1;					
			select++;
			onOff |= *select - '0';
			
			switch(onOff){
					case 0: //both relay off
							directionOutState = directionOutState & (~BIT(infoPico.chargeRele)); //it sets to OFF charger relay state 
							directionOutState = directionOutState & (~BIT(infoPico.loadRele)); 	 //it sets to OFF the load relay state
							ret = HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn); 							
							if(ret == 0){
								error = true;
							}
													
							if(error == false){
								usleep(RELEASE_TIME); 						//it wait the time that is need to relay to go in regime state
								memset(writeMessage,0,BUFF_SIZE);
								strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n"));	//it sends an Ack
								ret = write(connSockPico,writeMessage,BUFF_SIZE);
								if (ret <= 0){ 
									//cout << "ERROR writing to socket\n";
									close(connSockPico);
									close(sockPico);
									directionOutState = 0; 
									HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
									if(infoPico.acquireLoop == true){
										fileLog.close();
										HRDLStop(infoPico.picoID);			//it Stops picolog sampling 
									}
				
									HRDLCloseUnit(infoPico.picoID);			//it closes Picolog
									exit(1);	
								}
							}
							else{											//if there is an error it sends a Nack response to python script
								memset(writeMessage,0,BUFF_SIZE);
								strncpy(writeMessage,(const char*) "nAck\r\n",strlen("nAck\r\n"));
								ret = write(connSockPico,writeMessage, BUFF_SIZE);
								if (ret <= 0){ 
									//cout << "ERROR writing to socket\n";
									close(connSockPico);
									close(sockPico);
									directionOutState = 0; 
									HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
									if(infoPico.acquireLoop == true){
										fileLog.close();
										HRDLStop(infoPico.picoID);			//it Stops picolog sampling 
									}				
									HRDLCloseUnit(infoPico.picoID);			//it closes Picolog
									exit(1);
								}
							}
							
							
							break;
							
					case 1: //charger relay On load relay Off
							
							directionOutState = directionOutState & (~BIT(infoPico.chargeRele));
							directionOutState = directionOutState | (BIT(infoPico.loadRele)); 
							ret = HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);
														
							if(ret == 0){
								error = true;
							}
							
							if(error == false){
								usleep(RELEASE_TIME); 
								memset(writeMessage,0,BUFF_SIZE);
								strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n"));
								ret = write(connSockPico,writeMessage, BUFF_SIZE);
								if (ret <= 0){ 
									//cout << "ERROR writing to socket\n";
									close(connSockPico);
									close(sockPico);
									directionOutState = 0; 
									HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
									if(infoPico.acquireLoop == true){
										fileLog.close();
										HRDLStop(infoPico.picoID);			
									}
				
									HRDLCloseUnit(infoPico.picoID);			
									exit(1);
								}
							}
							else{
								memset(writeMessage,0,BUFF_SIZE);
								strncpy(writeMessage,(const char*) "nAck\r\n",strlen("nAck\r\n"));
								ret = write(connSockPico,writeMessage, BUFF_SIZE);
								if (ret <= 0){ 
									//cout << "ERROR writing to socket\n";
									close(connSockPico);
									close(sockPico);
									directionOutState = 0; 
									HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
									if(infoPico.acquireLoop == true){
										fileLog.close();
										HRDLStop(infoPico.picoID);			//Stops the sampling of Picolog
									}
				
									HRDLCloseUnit(infoPico.picoID);			//closing Picolog 
									exit(1);
								}
							}
							
							break;
							
					case 2: //charger relay Off load relay On
							directionOutState = directionOutState | (BIT(infoPico.chargeRele)); 
							directionOutState = directionOutState & (~BIT(infoPico.loadRele)); 
							ret = HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);
							
							if(ret == 0){
								error = true;
							}
							
							if(error == false){
								usleep(RELEASE_TIME); 
								memset(writeMessage,0,BUFF_SIZE);
								strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n"));
								ret = write(connSockPico,writeMessage, BUFF_SIZE);
								if (ret <= 0){ 
									//cout << "ERROR writing to socket\n";
									close(connSockPico);
									close(sockPico);
									directionOutState = 0; 
									HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
									if(infoPico.acquireLoop == true){
										fileLog.close();
										HRDLStop(infoPico.picoID);			
									}
				
									HRDLCloseUnit(infoPico.picoID);			
									exit(1);
								}
							}
							else{
								memset(writeMessage,0,BUFF_SIZE);
								strncpy(writeMessage,(const char*) "nAck\r\n",strlen("nAck\r\n"));
								ret = write(connSockPico,writeMessage, BUFF_SIZE);
								if (ret <= 0){ 
									//cout << "ERROR writing to socket\n";
									close(connSockPico);
									close(sockPico);
									directionOutState = 0; 
									HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
									if(infoPico.acquireLoop == true){
										fileLog.close();
										HRDLStop(infoPico.picoID);			
									}
				
									HRDLCloseUnit(infoPico.picoID);			
									exit(1);
								}
							}
							
							break;
					
					default: //if the request is <Relè 11> it sends a NAck response to server because  both relay can't be in the on state 
							//cout << "Default\n";
							memset(writeMessage,0,BUFF_SIZE);
							strncpy(writeMessage,(const char*) "nAck\r\n",strlen("nAck\r\n"));
							ret = write(connSockPico,writeMessage, BUFF_SIZE);
							if (ret <= 0){ 
									//cout << "ERROR writing to socket\n";
									close(connSockPico);
									close(sockPico);
									directionOutState = 0; 
									HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
									if(infoPico.acquireLoop == true){
										fileLog.close();
										HRDLStop(infoPico.picoID);			
									}
				
									HRDLCloseUnit(infoPico.picoID);			
									exit(1);
							}
							//Caution: it doesn't close the C program  because python will do it
											
			}//END switch statement
				
		}	
		else if(strncmp(readMessage,"SetRelè",strlen("SetRelè")) == 0){ //This service set the position of relays in two pin of picolog's I/O port
																		//request = <SetRelè posChargerelay posCheckChargerrelay posLoadrelay posCheckloadrelay>
																		
			select = strchr(readMessage,' '); //it found the first occurrence of character ' '
			select++; 						  //it increases of one the pointer position, now it point to posChargerrelay
			infoPico.chargeRele = *select - '0'; //it put and convert from char to int the pos of digital pin 
			select = select + 2; 			  //it increases of two the pointer position, now it point to posChargerrelay
			infoPico.checkReleCharge = *select - '0'; //it put and convert from char to int the pos of analog ch that control the state of charger relay
			select = select + 2; 
			infoPico.loadRele = *select - '0'; 		//it put and convert from char to int the pos of digital pin that control load relay
			select = select + 2; 
			infoPico.checkReleLoad = *select - '0'; //it put and convert from char to int the pos of analog ch that control the state of load relay
		
			
			memset(writeMessage,0,BUFF_SIZE);
			strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n")); //it sends an Ack to python script
			ret = write(connSockPico,writeMessage, BUFF_SIZE);
			if (ret <= 0){ 
				//cout << "ERROR writing to socket\n";
				close(connSockPico);
				close(sockPico);
				directionOutState = 0; 
				HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
				HRDLCloseUnit(infoPico.picoID);			//closing Picolog
				exit(1);
			}
			
		}//END SET RELE service
		else if(strncmp(readMessage,"SetTempCh",strlen("SetTempCh")) == 0){	//This service set the picolog's analog channel position where the temperature sensor is positioned																
			select = strchr(readMessage,' '); //it finds the first occurrence of ' '
			select++; 						  //Now the pointer select the info of analog channel where is the temperature sensor
			infoPico.tempChannel = *select - '0'; //conversion from char to integer
			
			memset(writeMessage,0,BUFF_SIZE);
			strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n")); //it send an Ack to python script
			ret = write(connSockPico,writeMessage, BUFF_SIZE);
			if (ret <= 0){ 
				//cout << "ERROR writing to socket\n";
				close(connSockPico);
				close(sockPico);
				directionOutState = 0; 
				HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
				HRDLCloseUnit(infoPico.picoID);			
				exit(1);
			}
		}
		else if(strncmp(readMessage,"Samples?\r\n",strlen("Samples?\r\n")) == 0){ //This service puts from Picolog's data buffer the samples of analog enable channel that have to insert in a log file. Request format <Samples?>
			
			
			//reading picoLog's samples from data buffer
			getValues = HRDLGetValues(infoPico.picoID,samples,&overflow, numConversions);
			//cout << getValues << "\n";
			
			//if getValues is > 0 is all ok, otherwise if the situation getValues = 0 presents consecutively for two time  program starts the exit procedure
			if(getValues == 0){
				fakeFault++; //in this case any data information are report on log file
				if(fakeFault > FAULT_THRESHOLD){
					//cout << "GetValues = 0\n";
					fileLog << "Picolog Error: Any Values are pick from buffer.\n";
					fileLog.close();
					close(connSockPico);
					close(sockPico);
					directionOutState = 0; 
					HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
					HRDLStop(infoPico.picoID);			
					HRDLCloseUnit(infoPico.picoID);		
					exit(1);
				}
				
			}
			else{
				fakeFault = 0; //it resets the fakeFault flag
				//time information 					
				time (&rawtime);					
				timeInfo = localtime(&rawtime); 			//it gets the local time
				strftime (calendar,80,"%H:%M:%S",timeInfo); //it gets the time format 
				fileLog << calendar << "\t" ;				//it prints the time in the fileLog
				
				//python is three dimensional vector that contain some info fo python 
				python[0] = samples[(infoPico.tempChannel-1) + (getValues-1)*(infoPico.numOfChannels)];			//Temperature
				python[1] = samples[(infoPico.checkReleCharge-1) + (getValues-1)*(infoPico.numOfChannels)];		//State relay of charger
				python[2] = samples[(infoPico.checkReleLoad-1) + (getValues-1)*(infoPico.numOfChannels)];		//state relay of load
				
				//cout << python[0]*(1.25/pow(2,23))*100 << "\n";
				//cout << python[1]*(1.25/pow(2,23)) << "\n";
				//cout << python[2]*(1.25/pow(2,23)) << "\n";
			
	
					
				//cout  << "acquisizione di passo: " << getValues << "\n";
				for(int i = 0; i<getValues*(infoPico.numOfChannels); i = i+(infoPico.numOfChannels)){ //it takes and writes data from data buffer to log file
					if(i != 0)
						fileLog << calendar << "\t";
					for(int b = 0; b < (infoPico.numOfChannels); b++)						
						fileLog << samples[b+i] <<  "\t";
				
					fileLog << getValues << "\t";
					fileLog << overflow << "\n";
				}
			}	
			
			ret = write(connSockPico,python, sizeof(python)); //sending of info to Python thread
			if (ret <= 0){ 
				//cout << "ERROR writing to socket\n";
				fileLog.close();
				close(connSockPico);
			    close(sockPico);
			    directionOutState = 0; 
			    HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
				HRDLStop(infoPico.picoID);			
				HRDLCloseUnit(infoPico.picoID);			
				exit(1);
			}
		}
		else if(strncmp(readMessage,"Path",strlen("Path")) == 0){ //This service fixes the log file's path. The request format is <Path log_file_path> 																					//Assegno il percorso di destinazione del File log
			error = false;
			token = strtok(readMessage, " "); 				//Path:
			token = strtok(NULL, " ");						//real path of log file
			memset(infoPico.dataPath,0,PATH_SIZE);			
			strncpy(infoPico.dataPath,token,strlen(token)); //it saves the path into infoPico structure
			select = strrchr(token,'_'); 					//it finds the last occurrence of character '_'
			if(select == NULL){
				error = true;
			}
						
			if(error == false){ 							//if there isn't errors it sends an Ack else it sends a Nack to Python script
				select++;
				step = ID_FIRST_STEP;
				memset(writeMessage,0,BUFF_SIZE);
				strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n"));
				ret = write(connSockPico,writeMessage, BUFF_SIZE);
				if (ret <= 0){ 
					//cout << "ERROR writing to socket\n";
					close(connSockPico);
					close(sockPico);
					directionOutState = 0; 
					HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
					HRDLCloseUnit(infoPico.picoID);		
					exit(1);
				}
			}
			else{
				memset(writeMessage,0,BUFF_SIZE);
				strncpy(writeMessage,(const char*) "nAck\r\n",strlen("nAck\r\n"));
				ret = write(connSockPico,writeMessage, BUFF_SIZE);
				if (ret <= 0){ 
					//cout << "ERROR writing to socket\n";
					close(connSockPico);
					close(sockPico);
					directionOutState = 0; 
					HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
					HRDLCloseUnit(infoPico.picoID);		
					exit(1);
				}
				
			}
		}				
		else if(strncmp(readMessage,"Start\r\n",strlen("Start\r\n")) == 0){	 //This service starts the acquisition phase of picolog. the Request format is <Start\r\n> 
				error = false;			
				setInterval = HRDLSetInterval(infoPico.picoID,(int32_t) samplesTime,HRDL_60MS); //It sets the sampling time and the conversion time of Picolog
				//cout << "Esito impostazione intervallo: " << setInterval << "\n\n";
				
				if(setInterval == 0){
					error = true;
				}
				
				numConversions = NUM_SAMPLES_PER_CHANNEL; //it sets the number of conversion for channel
					
				//cout << "Procedura di avvio campionamento in corso...\n";
				ret = HRDLRun(infoPico.picoID,numConversions,HRDL_BM_STREAM); //it starts sampling of data logger 
			    if(ret == 0)
					error = true;
				else
					acquireLoop = true;
					
				//cout << "Attesa dato valido...\n";
				countWait = 0;
				while(true){  
					ret = HRDLReady(infoPico.picoID); 	//it waits the ready state of picolog. In this way C program doesn't block over HRDLReady.
					if(ret == 1)
						break;
					countWait++;
					usleep(100000);
					if(countWait == 10){				//if after 10 times picolog is not yet ready it set the flag error to true state
						error = true;
						break;
					}			
				}
			
				if(error == false){ //if there isn't error sends an ack to python script, otherwise sends a Nack
					memset(writeMessage,0,BUFF_SIZE);
					strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n"));	
					ret = write(connSockPico,writeMessage, BUFF_SIZE);
					if (ret <= 0){ 
						//cout << "ERROR writing to socket\n";
						close(connSockPico);
						close(sockPico);
						directionOutState = 0; 
						HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
						if(acquireLoop == true){
							fileLog.close();
							HRDLStop(infoPico.picoID);
						}
						HRDLCloseUnit(infoPico.picoID);		
						exit(1);
					}
				}
				else{
					memset(writeMessage,0,BUFF_SIZE);
					strncpy(writeMessage,(const char*) "nAck\r\n",strlen("nAck\r\n"));	
					ret = write(connSockPico,writeMessage, BUFF_SIZE);
					if (ret <= 0){ 
						//cout << "ERROR writing to socket\n";
						close(connSockPico);
						close(sockPico);
						if(acquireLoop == true){
							fileLog.close();
							directionOutState = 0; 
							HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
							HRDLStop(infoPico.picoID);
						}
						HRDLCloseUnit(infoPico.picoID);		
						exit(1);
					}
					
				}
		}//End Start
		else if(strncmp(readMessage,"New",strlen("New")) == 0){ //This service open a New file Log to insert data of next test step. Request format is <New_IdStep\r\n>
			token = strtok(readMessage, "_\r\n"); 		//it divides string to token where delimiter are '_' and '\r\n' characters
			token = strtok(NULL, "_\r\n");			  	//it is the current step
			step = atoi(token);					  		//it converts ID_step string to a integer
			typeStep = strtok(NULL,"_\r\n");			//it contains type of step 'M' or 'C' or 'D'
			
			select = strrchr(infoPico.dataPath,'_');	//in dataPath variable, it finds the last occurrence of character '_'
			if(select == NULL)
				error = true;
			
			select++;									//now select point the step id in file log's path								
			if(sprintf(select, "%d.txt", step) < 0)		//it overwrites the last id step with the update step id
				error = true;
			
			fileLog.open(infoPico.dataPath,ios::out); 	//it opens file whose path is in dataPath variable
			if(fileLog.is_open() && (error == false)){
				
				//It writes the header file that contains some information like time, step id, etc.	
				time (&rawtime);
				timeInfo = localtime(&rawtime);
				strftime (calendar,80,"%d %b %Y %H:%M:%S",timeInfo);
				
				fileLog << "#CAUTION: The time lapsing between two adjacent samples has to be always consider 0.5s\n#The time format hh:mm:ss is only an indicative time, so don't consider it inside matlab elaboration.\n";
				fileLog << "\n#Test step:\t" << step << "\tType of step: " << typeStep << "\t\tstarted on:\t" << calendar << "\n\n\t";
				
				for(int c = 1; c <= 8; c++){  //it prints the raw that contain the id number of each channel
					fileLog << "C " << c << "\t";
				}
				fileLog << "number of data block\t";
				fileLog << "overflow\n"; 
				
				memset(writeMessage,0,BUFF_SIZE);
				strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n"));	//if there isn't errors it sends an Ack to python script 
				ret = write(connSockPico,writeMessage, BUFF_SIZE);
				if (ret <= 0){ 
					//cout << "ERROR writing to socket\n";
					close(connSockPico);
					close(sockPico);
					fileLog.close();
					directionOutState = 0; 
					HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
					HRDLStop(infoPico.picoID);
					HRDLCloseUnit(infoPico.picoID);	
					exit(1);
				}
			}	
			else{
				memset(writeMessage,0,BUFF_SIZE);
				strncpy(writeMessage,(const char*) "nAck\r\n",strlen("nAck\r\n"));	//if there is some error it sends a nack to python script
				ret = write(connSockPico,writeMessage, BUFF_SIZE);
				if (ret <= 0){ 
					//cout << "ERROR writing to socket\n";
					close(connSockPico);
					close(sockPico);
					fileLog.close();
					directionOutState = 0; 
					HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
					HRDLStop(infoPico.picoID);
					HRDLCloseUnit(infoPico.picoID);		
					exit(1);
				}
			}				
		}
		else if(strncmp(readMessage,"End\r\n",strlen("End\r\n")) == 0){ //This service close the log file that was open previously. Request format is <End\r\n>
			fileLog.close();
			memset(writeMessage,0,BUFF_SIZE);
			strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n"));	//it sends an Ack to python
			ret = write(connSockPico,writeMessage, BUFF_SIZE);
			if (ret <= 0){ 
				//cout << "ERROR writing to socket\n";
				close(connSockPico);
				close(sockPico);
				fileLog.close();
				directionOutState = 0; 
				HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);	
				HRDLStop(infoPico.picoID);
				HRDLCloseUnit(infoPico.picoID);		
				exit(1);
			}
		}	
		else if(strncmp(readMessage,"Exit\r\n",strlen("Exit\r\n")) == 0){ //This service close all opened socket, resets the I/O pin state, stops sampling and closes the pico unit. Request format is <Exit\r\n>
			directionOutState = 0;	//it resets the I/O port's state
			HRDLSetDigitalIOChannel(infoPico.picoID,directionOut,directionOutState,enableDigitIn);
			HRDLStop(infoPico.picoID);			//it stops sampling
			HRDLCloseUnit(infoPico.picoID);		//it closes picolog
			
			memset(writeMessage,0,BUFF_SIZE);
			strncpy(writeMessage,(const char*) "Ack\r\n",strlen("Ack\r\n"));	//it sends an Ack to python
			ret = write(connSockPico,writeMessage, BUFF_SIZE);
			if (ret <= 0){ 
				//cout << "ERROR writing to socket\n";
				close(connSockPico);
				close(sockPico);	
				exit(1);
			}
			
			close(connSockPico);	//it closes the connected socket
			close(sockPico);		//it closes the socket
			break; 								//it exits from while statement 
		 
		}
	}	
		
	return 0; //Main deads
}

