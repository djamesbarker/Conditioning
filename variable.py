"""
 Variable ratio operant conditioning

 Create a GUI window to make user enter parameters
 And implement the actions of presenting reward 
 according to whether the rat has achieved the criterion
 where the criterion for each trial is randomly selected from a certain range

 The circuit:
 * Red LED attached from pin 11 to +5V
 * 560 Ohm resistors attached from pin 11 to GND
 * Servo attached to pin 13
 * Button attached to pin 3

 """

# Import all needed libraries
import tkinter # GUI window
from time import sleep # delay to achieve time sequence
import pyfirmata # Arduino Uno board
import csv # saving information to files
import sys # correctly shut down the program
import time # give the rative time to record actions 
import math # help do calculation when getting ralative time
import random # random select the criterion for each trial


# inital variables
interval = 0 # the interval between receiving input from button and begin feeding
duration = 0 # how long staying feeding
rangemin = 0 # the min of the range
rangemax = 0 # the max of the range
timeslist = [] # the list of times
mode = 0 # range or list
thistimes = 0 # initial the each times parameter


# associate the port
port = 'COM9'
board = pyfirmata.Arduino(port)

# Using iterator thread to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Define pins
buttonpin = board.get_pin('d:3:i')
servoPin = 13
board.digital[servoPin].mode = pyfirmata.SERVO
LEDpin = board.get_pin('d:11:o')

# start time of the experiment
starttime = time.time()

# open the file and save actions during experiment
output = open('output_fix.txt', 'w', newline='')

# main function
def pressbutton():
    global interval
    global duration
    global rangemin
    global rangemax
    global timeslist
    global mode
    global thistimes


    # create a variable to achieve correct detection of the state of button
    # it is initially set to zero, once the button is pressed, it changed to 1, indicating the button is pressed
    # and it will be changed to zero again only when the button is released
    # after it back to zero, another press will be detected and count as active press
    # meanwhile, this variable can count for the rising and falling edge of button    
    upanddown = 0
    
    currenttimes = 0 # the times that the rat already press
    
    # disable the start button to avoid double-click during executing
    startButton.config(state=tkinter.DISABLED)
    
    # If user choose to pre-test
    # automatically start a trial that implement all the hardware
    # in order to check basic settings    
    if preVar.get():
        # get a list to test
        l=input("please enter a list of presses:")
        # convert into list
        strlist = list(l)
        # get the siginificant value in the list and save them into a new list
        # the number in this list is the range that the criterion can be selected from
        for x in range(len(strlist)):
            if strlist[x] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                timeslist.append(math.floor(float(strlist[x])))
        # randomly select the criterion for each trial
        thistimes=random.choice(timeslist)
        # print it out
        print(thistimes)
        while True:
            if buttonpin.read() == 1: # if button is pressed, .read() will return 1
                if upanddown == 0:
                    upanddown = 1
                    LEDpin.write(1)
                    top.update()
                    sleep(0.1)
                    LEDpin.write(0) # make the LED blink once to indicate the press lead to reward
                    currenttimes += 1; # count it into presses that lead to reward
                    # feed
                    if currenttimes == thistimes:
                        print ('press completed')
                        top.update()
                        sleep(1)
                        print ('start feeding')
                        for i in range(0, 180):
                            # well-built function to control servo 
                            # which make the user can directly write the angle of servo
                            board.digital[servoPin].write(i)
                            top.update()
                            sleep(0.01)
                        print ('stay feeding')
                        sleep(2)
                        print ('feeding end')
                        for i in range(180, 1, -1):
                            board.digital[servoPin].write(i)
                            top.update()
                            sleep(0.01)
                        currenttimes = 0 # reset currenttimes for new trials
                if upanddown == 1:
                    if buttonpin.read() == 0:
                        upanddown = 0 
                        
    # implement the experiment                        
    else:
        # whether load the configuration
        # don't read from existing configuration
        if loadVar.get() == 0:
            interval = math.floor(float(intervalEntry.get())) # the value get from GUI window, need to be converted into floating number
            duration = math.floor(float(durationEntry.get()))
            if rangeminEntry.get() != "": # if user enter the value in range
                rangemin = math.floor(float(rangeminEntry.get()))
                rangemax = math.floor(float(rangemaxEntry.get()))
            else: # otherwise, save as None
                rangemin = "NA"
                rangemax = "NA"
            if listEntry.get() != "": # if user enter the value in list
                inputlist = listEntry.get()
                strlist = inputlist.split(" ")
                for x in range(len(strlist)):
                        timeslist.append(math.floor(float(strlist[x])))
            else:
                inputlist = "NA"
            mode = int(modVar.get())
            with open('configuration_variable.csv', 'w', newline='') as f: # save parameters
                w = csv.writer(f)
                w.writerow(["Interval between two times", "Duration of feeding", "Min of range", "Max of range", "Input list", "mode"])
                data = [interval, duration, rangemin, rangemax, timeslist, mode]
                w.writerow(data)

        # read from existing configuration and print them out
        else:
            with open('configuration_variable.csv', 'r', newline='') as f:
                r = csv.reader(f)
                data = None
                count = 0
                for row in r:
                    if count == 1:
                        data = row
                    count += 1
                interval = math.floor(float(data[0]))
                duration= math.floor(float(data[1]))
                print("read result: ")
                print("interval: " + data[0])
                print("duration: " + data[1])
                if data[2] != "NA":
                    rangemin = math.floor(float(data[2]))
                    rangemax = math.floor(float(data[3]))
                    print("min of range: " + data[2])
                    print("max of range: " + data[3])
                if data[4] != "NA":
                    inputlist = data[4]
                    strlist = list(inputlist)
                    for x in range(len(strlist)):
                        if strlist[x] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                            timeslist.append(math.floor(float(strlist[x])))
                    print("list: " + data[4])
                mode = int(data[5])
                print("mode: " + data[5])
                
    # call the function that contains the sub-function    
    run()
    

# create a variable to achieve correct detection of the state of button
# it is initially set to zero, once the button is pressed, it changed to 1, indicating the button is pressed
# and it will be changed to zero again only when the button is released
# after it back to zero, another press will be detected and count as active press
# meanwhile, this variable can count for the rising and falling edge of button
upanddown = 0 
currenttimes = 0 # the times that the rat already press
interval=interval*100
duration=duration*100 # used for delay

def run():
    global interval
    global duration
    global rangemin
    global rangemax
    global timeslist
    global mode
    global currenttimes
    global upanddown
    global thistimes
    
    # range mode, then call the main body for this mode
    if mode == 1:
        thistimes = random.randint(rangemin, rangemax) # initial the criterion for each trial
        print(thistimes)
        rangemode()

    # list mode
    elif mode == 0:
        thistimes=random.choice(timeslist)
        print(thistimes)
        listmode()


def rangemode():
    global interval
    global duration
    global rangemin
    global rangemax
    global timeslist
    global mode
    global currenttimes
    global upanddown
    global thistimes
    if buttonpin.read() == 1: 
        if upanddown == 0:
            upanddown = 1
            print("pressed")
            #calculate the relative time for the press
            processtime = time.time() - starttime # unit in second
            hour = math.floor(processtime // 3600) # calculate hour
            minute = math.floor(processtime // 60 - (60 * hour)) # calculate minute
            second = round(processtime % 60, 2) # calculate seconds containing 2 digit of siginificant figures
            strtime = str(hour) + ":" + str(minute) + ":" + str(second)# time in the form of hh:mm:ss.xx
            outputstr = strtime + " : the rat press the button with RR, falling edge" 
            output.write(outputstr + "\n") # record this action down to the file
            
            LEDpin.write(1)
            top.update()
            sleep(0.1)
            LEDpin.write(0)
            currenttimes += 1; # increase the number of presses that lead to reward
            
            # if the rat achieve the criterion, that actions according to the time sequence
            # during this section, all actions and presses that do not lead to reward are recorded to file as well
            if currenttimes == thistimes:
                #record the time that it achieves the criterion
                processtime = time.time() - starttime
                hour = math.floor(processtime // 3600)
                minute = math.floor(processtime // 60 - (60 * hour))
                second = round(processtime % 60, 2)
                strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                outputstr = strtime + " : enough times are pressed"
                output.write(outputstr + "\n")
                
                # sleep for 'interval' seconds and record the useless presses
                # the reason that break down the delay is in order to update the condition to GUI window 
                # to avoid it fall into 'No responding'
                # also, during this process, useless presses can be detected and recorded
                ud1=0
                m=0
                while m<= interval:
                    m+=1
                    top.update()
                    sleep(0.01)
                    if buttonpin.read() == 1:
                        if ud1 == 0:
                            ud1 = 1
                            processtime = time.time() - starttime
                            hour = math.floor(processtime // 3600)
                            minute = math.floor(processtime // 60 - (60 * hour))
                            second = round(processtime % 60, 2)
                            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                            outputstr = strtime + " : the rat press the button with NR"
                            output.write(outputstr + "\n")
                    if ud1 == 1:
                        if buttonpin.read() == 0:
                            processtime = time.time() - starttime
                            hour = math.floor(processtime // 3600)
                            minute = math.floor(processtime // 60 - (60 * hour))
                            second = round(processtime % 60, 2)
                            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                            outputstr = strtime + " : the rat release the button"
                            output.write(outputstr + "\n")
                            ud1 = 0
                            
                # deliver the food and record the time down
                processtime = time.time() - starttime
                hour = math.floor(processtime // 3600)
                minute = math.floor(processtime // 60 - (60 * hour))
                second = round(processtime % 60, 2)
                strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                outputstr = strtime + " : start feeding"
                output.write(outputstr + "\n")
                for i in range(0, 180):
                    board.digital[servoPin].write(i)
                    top.update()
                    sleep(0.01)
                    
                # stay feeding and record the useless presses
                ud2=0
                m=0
                while m<= interval:
                    m+=1
                    top.update()
                    sleep(0.01)
                    if buttonpin.read() == 1:
                        if ud2 == 0:
                            ud2 = 1
                            processtime = time.time() - starttime
                            hour = math.floor(processtime // 3600)
                            minute = math.floor(processtime // 60 - (60 * hour))
                            second = round(processtime % 60, 2)
                            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                            outputstr = strtime + " : the rat press the button with NR"
                            output.write(outputstr + "\n")
                    if ud2 == 1:
                        if buttonpin.read() == 0:
                            processtime = time.time() - starttime
                            hour = math.floor(processtime // 3600)
                            minute = math.floor(processtime // 60 - (60 * hour))
                            second = round(processtime % 60, 2)
                            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                            outputstr = strtime + " : the rat release the button"
                            output.write(outputstr + "\n")
                            ud2 = 0
                
                # remove the food and record the time down
                processtime = time.time() - starttime
                hour = math.floor(processtime // 3600)
                minute = math.floor(processtime // 60 - (60 * hour))
                second = round(processtime % 60, 2)
                strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                outputstr = strtime + " : stop feeding"
                output.write(outputstr + "\n")
                for i in range(180, 1, -1):
                    board.digital[servoPin].write(i)
                    top.update()
                    sleep(0.01)
                    
                currenttimes = 0 # reset currenttimes for new trials
                
                thistimes = random.randint(rangemin, rangemax) # select another criterion for new trial
                print(thistimes)
                
    if upanddown == 1:
        if buttonpin.read() == 0:
            # record the releasing of the button
            processtime = time.time() - starttime
            hour = math.floor(processtime // 3600)
            minute = math.floor(processtime // 60 - (60 * hour))
            second = round(processtime % 60, 2)
            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
            outputstr = strtime + " : rat releases the button, RR's rising edge"
            output.write(outputstr + "\n")
            upanddown = 0

    # recall itself every 1milisecond in order to keep monitoring the press
    top.after(1,rangemode)

# listmode is similar to range
def listmode():
    global interval
    global duration
    global rangemin
    global rangemax
    global timeslist
    global mode
    global currenttimes
    global upanddown
    global thistimes
    if buttonpin.read() == 1:
        if upanddown == 0:
            upanddown = 1
            print("pressed")
            processtime = time.time() - starttime
            hour = math.floor(processtime // 3600)
            minute = math.floor(processtime // 60 - (60 * hour))
            second = round(processtime % 60, 2)
            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
            outputstr = strtime + " : the rat press the button with RR"
            output.write(outputstr + "\n")
            LEDpin.write(1)
            top.update()
            sleep(0.1)
            LEDpin.write(0)
            currenttimes += 1;
            
            # feed
            if currenttimes == thistimes:
                processtime = time.time() - starttime
                hour = math.floor(processtime // 3600)
                minute = math.floor(processtime // 60 - (60 * hour))
                second = round(processtime % 60, 2)
                strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                outputstr = strtime + " : enough times are pressed"
                output.write(outputstr + "\n")
                # wait before feeding
                ud1=0
                m=0
                while m<= interval:
                    m+=1
                    top.update()
                    sleep(0.01)
                    if buttonpin.read() == 1:
                        if ud1 == 0:
                            ud1 = 1
                            processtime = time.time() - starttime
                            hour = math.floor(processtime // 3600)
                            minute = math.floor(processtime // 60 - (60 * hour))
                            second = round(processtime % 60, 2)
                            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                            outputstr = strtime + " : the rat press the button with NR"
                            output.write(outputstr + "\n")
                    if ud1 == 1:
                        if buttonpin.read() == 0:
                            processtime = time.time() - starttime
                            hour = math.floor(processtime // 3600)
                            minute = math.floor(processtime // 60 - (60 * hour))
                            second = round(processtime % 60, 2)
                            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                            outputstr = strtime + " : the rat release the button"
                            output.write(outputstr + "\n")
                            ud1 = 0
                            
                processtime = time.time() - starttime
                hour = math.floor(processtime // 3600)
                minute = math.floor(processtime // 60 - (60 * hour))
                second = round(processtime % 60, 2)
                strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                outputstr = strtime + " : start feeding"
                output.write(outputstr + "\n")
                # begin giving fodd
                for i in range(0, 180):
                    board.digital[servoPin].write(i)
                    top.update()
                    sleep(0.01)
                    
                # stay feeding
                ud2=0
                m=0
                while m<= interval:
                    m+=1
                    top.update()
                    sleep(0.01)
                    if buttonpin.read() == 1:
                        if ud2 == 0:
                            ud2 = 1
                            processtime = time.time() - starttime
                            hour = math.floor(processtime // 3600)
                            minute = math.floor(processtime // 60 - (60 * hour))
                            second = round(processtime % 60, 2)
                            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                            outputstr = strtime + " : the rat press the button with NR"
                            output.write(outputstr + "\n")
                    if ud2 == 1:
                        if buttonpin.read() == 0:
                            processtime = time.time() - starttime
                            hour = math.floor(processtime // 3600)
                            minute = math.floor(processtime // 60 - (60 * hour))
                            second = round(processtime % 60, 2)
                            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                            outputstr = strtime + " : the rat release the button"
                            output.write(outputstr + "\n")
                            ud2 = 0
                            
                processtime = time.time() - starttime
                hour = math.floor(processtime // 3600)
                minute = math.floor(processtime // 60 - (60 * hour))
                second = round(processtime % 60, 2)
                strtime = str(hour) + ":" + str(minute) + ":" + str(second)
                outputstr = strtime + " : stop feeding"
                output.write(outputstr + "\n")
                # finish feeding
                for i in range(180, 1, -1):
                    board.digital[servoPin].write(i)
                    top.update()
                    sleep(0.01)
                    
                currenttimes = 0 
                thistimes=random.choice(timeslist)
                print(thistimes)
                
    if upanddown == 1:
        if buttonpin.read() == 0:
            processtime = time.time() - starttime
            hour = math.floor(processtime // 3600)
            minute = math.floor(processtime // 60 - (60 * hour))
            second = round(processtime % 60, 2)
            strtime = str(hour) + ":" + str(minute) + ":" + str(second)
            outputstr = strtime + " : rat releases the button, RR's rising edge"
            output.write(outputstr + "\n")
            upanddown = 0
            
    top.after(1,listmode)

# exit button function
def exit():
    board.exit()
    top.destroy()
    sys.exit()


# Initialize main windows with title and size
top = tkinter.Tk()
top.title("Variable Ratio")

#create the checkbox for pre-test
preVar = tkinter.IntVar()
preCheckBox = tkinter.Checkbutton(top,
                                  text="PRE-TEST MODE",
                                  variable=preVar)
preCheckBox.grid(column=2, row=1) # to manage the location on window


# create the checkbox for user to decide whether read previous configuration or not
loadVar = tkinter.IntVar()
loadCheckBox = tkinter.Checkbutton(top, text = "load config?", variable = loadVar)
loadCheckBox.grid(column = 2, row = 2)

# create the checkbox for range or List
modVar = tkinter.IntVar()
modCheckBox = tkinter.Checkbutton(top, text = "check for Range, uncheck for List", variable = modVar)
modCheckBox.grid(column = 2, row = 8)




# get parameters

# the interval between receive and act
tkinter.Label(top, text = "Interval: ").grid(column = 1, row = 3)
intervalEntry = tkinter.Entry(top)
intervalEntry.grid(column = 2, row = 3)
intervalEntry.focus_set()

# how long will the feeding last
tkinter.Label(top, text = "Duration: ").grid(column = 1, row = 4)
durationEntry = tkinter.Entry(top)
durationEntry.grid(column = 2, row = 4)
durationEntry.focus_set()

# range
tkinter.Label(top, text = "Range: ").grid(column = 1, row = 5)
rangeminEntry = tkinter.Entry(top)
rangeminEntry.grid(column = 2, row = 5)
rangeminEntry.focus_set()
tkinter.Label(top, text = " to ").grid(column = 3, row = 5)
rangemaxEntry = tkinter.Entry(top)
rangemaxEntry.grid(column = 4, row = 5)
rangemaxEntry.focus_set()

# list of times
tkinter.Label(top, text = "List of times: ").grid(column = 1, row = 6)
listEntry = tkinter.Entry(top)
listEntry.grid(column = 2, row = 6)
listEntry.focus_set()
tkinter.Label(top, text = " Please separate with blank").grid(column = 3, row = 6)


# Create Start and Exit button

# button for main function
startButton = tkinter.Button(top, text="Start", command=pressbutton)
startButton.grid(column=1, row=7)

# exit button
exitButton = tkinter.Button(top, text="Exit", command=exit)
exitButton.grid(column=2, row=7)

#start and open the window
top.mainloop()