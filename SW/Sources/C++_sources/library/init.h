#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <iostream>
#include <fstream>
#include <string.h>
#include <time.h>
#include <math.h>
#include <errno.h>



#define SINGMODE 1					
#define DIFFMODE 0					//active the differential mode in an analog channel
#define SAMPTIME 500 				//samples time in ms
#define ENABLE_CHANNELS 8			//total number of enables analog channels
#define NUM_SAMPLES_PER_CHANNEL 11  //it sets to 11 because the maximum samples Time is 5s, while picolog sampling at 0,5 sec every time it put 10 samples, so 11 may be at C to recovery another samples due to the jitter  
#define LIST_PENDENT_CONNECTIONS 1	//It identifies the maximum queue length of pendent connection
#define BUFF_SIZE 100				//It defines the length of string buffer used to sends information from client to server 
#define PATH_SIZE 300				//maximum length of string buffer that contained the path information
#define RELEASE_TIME 25000			//The time needs at relays to go at regime
#define ID_FIRST_STEP 1				//step number starts from Id_first_step values
#define	NOISE_REJECTION 0			//use from picolog to set noise rejection to 50Hz
#define SET_CH	1					
#define RESET_CH 0
#define FAULT_THRESHOLD 1			//it indicates the allowed number of consecutive getValues = 0 

#define BIT(x) (1 << (x-1))


int32_t initSocket(int*, const char*, int);
int8_t initPico(int16_t*, int16_t*);
