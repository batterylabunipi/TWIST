EESchema Schematic File Version 2
LIBS:TWIST_tester-rescue
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:morsett_1x02
LIBS:myLib
LIBS:switches
LIBS:TWIST_tester-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 3 3
Title "Conditioning circuit of Li-ion cell voltage measurement "
Date "2018-02-18"
Rev ""
Comp "Dipartimento di Ingegneria dell'Informazione, Università di Pisa, ITALY"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L R R23
U 1 1 59163C6B
P 3950 4000
F 0 "R23" V 4030 4000 50  0000 C CNN
F 1 "990K" V 3850 4000 50  0000 C CNN
F 2 "MYLIB:R_1206" V 3880 4000 50  0001 C CNN
F 3 "" H 3950 4000 50  0001 C CNN
	1    3950 4000
	0    -1   -1   0   
$EndComp
$Comp
L C C9
U 1 1 59163D23
P 5050 4300
F 0 "C9" H 5075 4400 50  0000 L CNN
F 1 "1uF" H 5075 4200 50  0000 L CNN
F 2 "MYLIB:0805" H 5088 4150 50  0001 C CNN
F 3 "" H 5050 4300 50  0001 C CNN
	1    5050 4300
	1    0    0    -1  
$EndComp
Text HLabel 3350 4000 0    60   Input ~ 0
VBATTIN
Text HLabel 7600 3900 2    60   Input ~ 0
VBATTOUT
$Comp
L C C10
U 1 1 59168667
P 6100 3350
F 0 "C10" H 6125 3450 50  0000 L CNN
F 1 "100nF" H 6125 3250 50  0000 L CNN
F 2 "MYLIB:0805" H 6138 3200 50  0001 C CNN
F 3 "" H 6100 3350 50  0001 C CNN
	1    6100 3350
	1    0    0    -1  
$EndComp
$Comp
L TestPoint T17
U 1 1 59249107
P 6900 3800
F 0 "T17" H 7025 4025 60  0000 C CNN
F 1 "TestPoint" H 7150 3925 60  0000 C CNN
F 2 "MYLIB:TSTPOINT" H 6900 3800 60  0001 C CNN
F 3 "" H 6900 3800 60  0001 C CNN
	1    6900 3800
	1    0    0    -1  
$EndComp
$Comp
L GNDA #PWR051
U 1 1 5967C6E7
P 5050 4600
F 0 "#PWR051" H 5050 4350 50  0001 C CNN
F 1 "GNDA" H 5050 4450 50  0000 C CNN
F 2 "" H 5050 4600 50  0001 C CNN
F 3 "" H 5050 4600 50  0001 C CNN
	1    5050 4600
	1    0    0    -1  
$EndComp
$Comp
L GNDA #PWR052
U 1 1 596851E2
P 6100 3600
F 0 "#PWR052" H 6100 3350 50  0001 C CNN
F 1 "GNDA" H 6100 3450 50  0000 C CNN
F 2 "" H 6100 3600 50  0001 C CNN
F 3 "" H 6100 3600 50  0001 C CNN
	1    6100 3600
	1    0    0    -1  
$EndComp
$Comp
L R R24
U 1 1 5A03352D
P 4500 4300
F 0 "R24" V 4580 4300 50  0000 C CNN
F 1 "330K" V 4400 4300 50  0000 C CNN
F 2 "MYLIB:0805" V 4430 4300 50  0001 C CNN
F 3 "" H 4500 4300 50  0001 C CNN
	1    4500 4300
	1    0    0    -1  
$EndComp
$Comp
L GNDA #PWR053
U 1 1 5A033587
P 4500 4600
F 0 "#PWR053" H 4500 4350 50  0001 C CNN
F 1 "GNDA" H 4500 4450 50  0000 C CNN
F 2 "" H 4500 4600 50  0001 C CNN
F 3 "" H 4500 4600 50  0001 C CNN
	1    4500 4600
	1    0    0    -1  
$EndComp
$Comp
L C C11
U 1 1 5A033688
P 6200 4450
F 0 "C11" H 6225 4550 50  0000 L CNN
F 1 "100nF" H 6225 4350 50  0000 L CNN
F 2 "MYLIB:0805" H 6238 4300 50  0001 C CNN
F 3 "" H 6200 4450 50  0001 C CNN
	1    6200 4450
	1    0    0    -1  
$EndComp
$Comp
L GNDA #PWR054
U 1 1 5A033724
P 6200 4800
F 0 "#PWR054" H 6200 4550 50  0001 C CNN
F 1 "GNDA" H 6200 4650 50  0000 C CNN
F 2 "" H 6200 4800 50  0001 C CNN
F 3 "" H 6200 4800 50  0001 C CNN
	1    6200 4800
	1    0    0    -1  
$EndComp
$Comp
L TestPoint T16
U 1 1 5A0350F5
P 4500 3900
F 0 "T16" H 4625 4125 60  0000 C CNN
F 1 "TestPoint" H 4750 4025 60  0000 C CNN
F 2 "MYLIB:TSTPOINT" H 4500 3900 60  0001 C CNN
F 3 "" H 4500 3900 60  0001 C CNN
	1    4500 3900
	1    0    0    -1  
$EndComp
$Comp
L GNDA #PWR055
U 1 1 5A0B3DFD
P 2300 6150
F 0 "#PWR055" H 2300 5900 50  0001 C CNN
F 1 "GNDA" H 2300 6000 50  0000 C CNN
F 2 "" H 2300 6150 50  0001 C CNN
F 3 "" H 2300 6150 50  0001 C CNN
	1    2300 6150
	1    0    0    -1  
$EndComp
$Comp
L R R20
U 1 1 5A0B4155
P 2250 5900
F 0 "R20" V 2330 5900 50  0000 C CNN
F 1 "1M" V 2250 5900 50  0000 C CNN
F 2 "MYLIB:0805" V 2180 5900 50  0001 C CNN
F 3 "" H 2250 5900 50  0001 C CNN
	1    2250 5900
	0    1    1    0   
$EndComp
$Comp
L R R21
U 1 1 5A0B41D4
P 2900 5100
F 0 "R21" V 2800 5100 50  0000 C CNN
F 1 "1M" V 2900 5100 50  0000 C CNN
F 2 "MYLIB:0805" V 2830 5100 50  0001 C CNN
F 3 "" H 2900 5100 50  0001 C CNN
	1    2900 5100
	0    1    1    0   
$EndComp
$Comp
L +2V5 #PWR056
U 1 1 5A0B47F8
P 1850 5800
F 0 "#PWR056" H 1850 5650 50  0001 C CNN
F 1 "+2V5" H 1850 5940 50  0000 C CNN
F 2 "" H 1850 5800 50  0001 C CNN
F 3 "" H 1850 5800 50  0001 C CNN
	1    1850 5800
	1    0    0    -1  
$EndComp
$Comp
L +5V #PWR057
U 1 1 5A0B4A1E
P 2700 6450
F 0 "#PWR057" H 2700 6300 50  0001 C CNN
F 1 "+5V" H 2700 6590 50  0000 C CNN
F 2 "" H 2700 6450 50  0001 C CNN
F 3 "" H 2700 6450 50  0001 C CNN
	1    2700 6450
	-1   0    0    1   
$EndComp
$Comp
L -5V #PWR50
U 1 1 5A0B65E7
P 2700 5600
F 0 "#PWR50" H 2700 5700 50  0001 C CNN
F 1 "-5V" H 2700 5750 50  0000 C CNN
F 2 "" H 2700 5600 50  0001 C CNN
F 3 "" H 2700 5600 50  0001 C CNN
	1    2700 5600
	1    0    0    -1  
$EndComp
$Comp
L +2V5 #PWR058
U 1 1 5A0B6F7E
P 5750 3100
F 0 "#PWR058" H 5750 2950 50  0001 C CNN
F 1 "+2V5" H 5750 3240 50  0000 C CNN
F 2 "" H 5750 3100 50  0001 C CNN
F 3 "" H 5750 3100 50  0001 C CNN
	1    5750 3100
	1    0    0    -1  
$EndComp
$Comp
L ADA4051 U3
U 1 1 5A0B9767
P 5850 3900
F 0 "U3" H 5900 4100 50  0000 C CNN
F 1 "ADA4051" H 5850 3700 50  0000 L CNN
F 2 "MYLIB:SOT-23-5" H 5800 4000 50  0001 C CNN
F 3 "" H 5900 4100 50  0001 C CNN
	1    5850 3900
	1    0    0    -1  
$EndComp
$Comp
L LT6003 U2
U 1 1 5A0C80E1
P 2800 6000
F 0 "U2" H 2850 6200 50  0000 C CNN
F 1 "LT6003" H 2800 5800 50  0000 L CNN
F 2 "MYLIB:SOT-23-5" H 2750 6100 50  0001 C CNN
F 3 "" H 2850 6200 50  0001 C CNN
	1    2800 6000
	1    0    0    1   
$EndComp
$Comp
L C C8
U 1 1 5A0D7A04
P 3700 6200
F 0 "C8" H 3725 6300 50  0000 L CNN
F 1 "1u" H 3725 6100 50  0000 L CNN
F 2 "MYLIB:0805" H 3738 6050 50  0001 C CNN
F 3 "" H 3700 6200 50  0001 C CNN
	1    3700 6200
	1    0    0    -1  
$EndComp
$Comp
L R R22
U 1 1 5A0D7C15
P 3700 6625
F 0 "R22" V 3780 6625 50  0000 C CNN
F 1 "2k" V 3700 6625 50  0000 C CNN
F 2 "MYLIB:0805" V 3630 6625 50  0001 C CNN
F 3 "" H 3700 6625 50  0001 C CNN
	1    3700 6625
	1    0    0    -1  
$EndComp
$Comp
L GNDA #PWR059
U 1 1 5A0D80AC
P 3700 6875
F 0 "#PWR059" H 3700 6625 50  0001 C CNN
F 1 "GNDA" H 3700 6725 50  0000 C CNN
F 2 "" H 3700 6875 50  0001 C CNN
F 3 "" H 3700 6875 50  0001 C CNN
	1    3700 6875
	1    0    0    -1  
$EndComp
$Comp
L TestPoint T15
U 1 1 5A0D8505
P 4250 5975
F 0 "T15" H 4375 6200 60  0000 C CNN
F 1 "TestPoint" H 4500 6100 60  0000 C CNN
F 2 "MYLIB:TSTPOINT" H 4250 5975 60  0001 C CNN
F 3 "" H 4250 5975 60  0001 C CNN
	1    4250 5975
	1    0    0    -1  
$EndComp
$Comp
L C C12
U 1 1 5A16F53D
P 3150 6650
F 0 "C12" H 3175 6750 50  0000 L CNN
F 1 "100nF" H 3175 6550 50  0000 L CNN
F 2 "MYLIB:0805" H 3188 6500 50  0001 C CNN
F 3 "" H 3150 6650 50  0001 C CNN
	1    3150 6650
	1    0    0    -1  
$EndComp
$Comp
L C C13
U 1 1 5A16F88E
P 3200 5500
F 0 "C13" H 3225 5600 50  0000 L CNN
F 1 "100nF" H 3225 5400 50  0000 L CNN
F 2 "MYLIB:0805" H 3238 5350 50  0001 C CNN
F 3 "" H 3200 5500 50  0001 C CNN
	1    3200 5500
	-1   0    0    1   
$EndComp
$Comp
L GNDA #PWR060
U 1 1 5A170527
P 3200 5750
F 0 "#PWR060" H 3200 5500 50  0001 C CNN
F 1 "GNDA" H 3200 5600 50  0000 C CNN
F 2 "" H 3200 5750 50  0001 C CNN
F 3 "" H 3200 5750 50  0001 C CNN
	1    3200 5750
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 4000 5550 4000
Wire Wire Line
	3800 4000 3350 4000
Wire Wire Line
	6150 3900 7600 3900
Wire Wire Line
	6100 3500 6100 3600
Wire Wire Line
	5750 3200 6100 3200
Connection ~ 5750 3200
Wire Wire Line
	5050 4000 5050 4150
Wire Wire Line
	5050 4450 5050 4600
Wire Wire Line
	4500 3900 4500 4150
Connection ~ 4500 4000
Wire Wire Line
	4500 4450 4500 4600
Wire Wire Line
	5750 4250 6200 4250
Wire Wire Line
	6200 4250 6200 4300
Wire Wire Line
	6200 4600 6200 4800
Connection ~ 5050 4000
Wire Wire Line
	2300 6075 2300 6150
Wire Wire Line
	2500 5900 2400 5900
Wire Wire Line
	2450 5100 2450 5900
Connection ~ 2450 5900
Wire Wire Line
	3350 5100 3350 6000
Wire Wire Line
	5750 6000 3100 6000
Connection ~ 3350 6000
Wire Wire Line
	2100 5900 1850 5900
Wire Wire Line
	1850 5900 1850 5800
Wire Wire Line
	2700 6300 2700 6450
Wire Wire Line
	2700 5700 2700 5600
Wire Wire Line
	5550 3800 5050 3800
Wire Wire Line
	6900 3800 6900 3900
Connection ~ 6900 3900
Connection ~ 6600 3900
Wire Wire Line
	5050 2850 6600 2850
Wire Wire Line
	5050 3800 5050 2850
Wire Wire Line
	6600 2850 6600 3900
Wire Wire Line
	5750 3100 5750 3600
Wire Wire Line
	2500 6075 2300 6075
Wire Wire Line
	5750 4200 5750 6000
Connection ~ 5750 4250
Wire Wire Line
	3700 6000 3700 6050
Connection ~ 3700 6000
Wire Wire Line
	3700 6350 3700 6475
Wire Wire Line
	3700 6775 3700 6875
Wire Wire Line
	4250 5975 4250 6000
Connection ~ 4250 6000
Wire Wire Line
	2450 5100 2750 5100
Wire Wire Line
	3050 5100 3350 5100
Wire Wire Line
	2850 5650 2700 5650
Wire Wire Line
	2850 5300 2850 5650
Connection ~ 2700 5650
Wire Wire Line
	3200 5650 3200 5750
Wire Wire Line
	2850 5300 3200 5300
Wire Wire Line
	3200 5300 3200 5350
Wire Wire Line
	2700 6350 3150 6350
Wire Wire Line
	3150 6350 3150 6500
Connection ~ 2700 6350
$Comp
L GNDA #PWR061
U 1 1 5A170D7E
P 3150 6900
F 0 "#PWR061" H 3150 6650 50  0001 C CNN
F 1 "GNDA" H 3150 6750 50  0000 C CNN
F 2 "" H 3150 6900 50  0001 C CNN
F 3 "" H 3150 6900 50  0001 C CNN
	1    3150 6900
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 6800 3150 6900
Text Notes 4000 3450 0    60   ~ 0
Voltage divider
$EndSCHEMATC