import adafruit_display_text.label
from adafruit_bitmap_font import bitmap_font
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import time
import displaySubsystem
import keyInput
from dirver_lightSensor import *

#Clock
fontUA = bitmap_font.load_font("fonts/PixelUA+EN_v1.2-17.bdf")

MaxDays = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

KEY_MENU = 0
KEY_DOWN = 1
KEY_UP = 2

autoLightFlag = 0

selectSettingOptions = 0
pageID = 0

timeSettingLabel = 0
timeTemp = [0, 0, 0]
dateTemp = [0, 0, 0]

keyMenuValue = 0
keyDownValue = 0
keyUpValue = 0

bit_depth_value = 1
base_width = 64
base_height = 32
chain_across = 1
tile_down = 1
serpentine_value = True

width_value = base_width * chain_across
height_value = base_height * tile_down

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=width_value,height=height_value,bit_depth=bit_depth_value,
    rgb_pins=[board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9],
    addr_pins=[board.GP10, board.GP16, board.GP18, board.GP20],
    clock_pin=board.GP11,latch_pin=board.GP12,output_enable_pin=board.GP13,
    tile=tile_down,serpentine=serpentine_value,
    doublebuffer=True,
)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)
display.rotation = 0
line1 = adafruit_display_text.label.Label(fontUA, color=0x0057B7)
line2 = adafruit_display_text.label.Label(fontUA, color=0xFFDD00)
line3 = adafruit_display_text.label.Label(fontUA, color=0x00057B7)

g = displayio.Group()
g.append(line1)
g.append(line2)
g.append(line3)
display.show(g)

keyInput.keyInit()

showSystem = displaySubsystem.DISPLAYSUBSYSTEM()

#only 1 and 0 working as of 11.08.23
def checkLightSensor():
    if autoLightFlag == 1:
        lightSensorValue = get_voltage()
        if lightSensorValue > 2800:
            display.brightness = 1
        else:
            display.brightness = 1

def isLeapYear(year): 
    if year % 4 == 0 and year % 100 != 0:
        return True
    if year % 400 == 0:
        return True
    return False


def getMaxDay(month, year):
    if month < 1 or month > 12:
        print("error month")
        return -1
    maxDay = MaxDays[month]
    if year != -1 and month == 2:
        if isLeapYear(year):
            maxDay += 1
    return maxDay


def keyMenuProcessingFunction():
    global pageID, timeSettingLabel
    if pageID == 2 and selectSettingOptions <= 1:
        timeSettingLabel += 1
        if timeSettingLabel > 2:
            timeSettingLabel = 0
    pageID += 1
    if pageID > 2:
        pageID = 1


def keyDownProcessingFunction():
    global selectSettingOptions, timeTemp, dateTemp, autoLightFlag
    if pageID == 1:
        selectSettingOptions -= 1
        if selectSettingOptions == -1:
            selectSettingOptions = 2
    if pageID == 2:
        if selectSettingOptions == 0:
            if timeSettingLabel == 0:
                timeTemp[0] -= 1
                if timeTemp[0] < 0:
                    timeTemp[0] = 23
            elif timeSettingLabel == 1:
                timeTemp[1] -= 1
                if timeTemp[1] < 0:
                    timeTemp[1] = 59
            else:
                timeTemp[2] -= 1
                if timeTemp[2] < 0:
                    timeTemp[2] = 59
        if selectSettingOptions == 1:
            if timeSettingLabel == 0:
                dateTemp[0] -= 1
                if dateTemp[0] < 2000:
                    dateTemp[0] = 2099
            elif timeSettingLabel == 1:
                dateTemp[1] -= 1
                if dateTemp[1] < 1:
                    dateTemp[1] = 12
            else:
                dateTemp[2] -= 1
                if dateTemp[2] < 1:
                    dateTemp[2] = getMaxDay(dateTemp[1], dateTemp[0])
        if selectSettingOptions == 2:
            if autoLightFlag:
                autoLightFlag = 0
            else:
                autoLightFlag = 1


def keyUpProcessingFunction():
    global pageID, selectSettingOptions, timeTemp, dateTemp, autoLightFlag
    if pageID == 1:
        selectSettingOptions += 1
        if selectSettingOptions == 3:
            selectSettingOptions = 0
    if pageID == 2:
        if selectSettingOptions == 0:
            if timeSettingLabel == 0:
                timeTemp[0] += 1
                if timeTemp[0] == 24:
                    timeTemp[0] = 0
            elif timeSettingLabel == 1:
                timeTemp[1] += 1
                if timeTemp[1] == 60:
                    timeTemp[1] = 0
            else:
                timeTemp[2] += 1
                if timeTemp[2] == 60:
                    timeTemp[2] = 0
        if selectSettingOptions == 1:
            if timeSettingLabel == 0:
                dateTemp[0] += 1
                if dateTemp[0] > 2099:
                    dateTemp[0] = 2000
            elif timeSettingLabel == 1:
                dateTemp[1] += 1
                if dateTemp[1] > 12:
                    dateTemp[1] = 1
            else:
                dateTemp[2] += 1
                if dateTemp[2] > getMaxDay(dateTemp[1], dateTemp[0]):
                    dateTemp[2] = 1
        if selectSettingOptions == 2:
            if autoLightFlag:
                autoLightFlag = 0
            else:
                autoLightFlag = 1

def keyExitProcessingFunction():
    global pageID, timeSettingLabel
    if pageID == 2 and selectSettingOptions <= 1:
        showSystem.setDateTime(selectSettingOptions, dateTemp, timeTemp)
        timeSettingLabel = 0
    pageID -= 1
    if pageID < 0:
        pageID = 1
        #firstEnteringPageFlag = 1


def keyProcessing(keyValue):
    global keyMenuValue, keyDownValue, keyUpValue
    if keyValue == KEY_MENU:
        keyMenuValue += 1
    if keyValue == KEY_DOWN:
        keyDownValue += 1
    if keyValue == KEY_UP:
        keyUpValue += 1

    if keyMenuValue > 0 and keyMenuValue < 20 and keyValue == None:
        keyMenuProcessingFunction()
        keyMenuValue = 0
    elif keyMenuValue >= 20 and keyValue == None:
        keyMenuValue = 0

    if keyDownValue > 0 and keyDownValue < 20 and keyValue == None:
        keyDownProcessingFunction()
        keyDownValue = 0
    elif keyDownValue >= 20 and keyValue == None:
        keyDownValue = 0

    if keyUpValue > 0 and keyUpValue < 20 and keyValue == None:
        keyUpProcessingFunction()
        keyUpValue = 0
        
    elif keyUpValue >= 20 and keyValue == None:
        keyExitProcessingFunction()
        keyUpValue = 0

while True:
    checkLightSensor()
    key_value = keyInput.getKeyValue()
    keyProcessing(key_value)
    if pageID == 0:
        showSystem.showDateTimePage(line1, line2, line3)
        line1.x = 0
        line1.y = 4
        line2.x = 0
        line2.y = 13
        line3.x = 0
        line3.y = 22
    if pageID == 1:
        line3.x = 0
        line3.y = 22
        line3.text = ""
        showSystem.showSetListPage(line1, line2, selectSettingOptions)
    if pageID == 2 and selectSettingOptions == 0:
        line1.x = 0
        line1.y = 4
        line1.text = ""
        showSystem.timeSettingPage(line2, line3, timeSettingLabel, timeTemp)
    if pageID == 2 and selectSettingOptions == 1:
        line1.x = 0
        line1.y = 4
        line1.text = ""
        showSystem.dateSettingPage(line2, line3, timeSettingLabel, dateTemp)
    if pageID == 2 and selectSettingOptions > 1:
        line1.x = 0
        line1.y = 4
        line1.text = ""
        showSystem.onOffPage(line2, line3, selectSettingOptions, autoLightFlag)

        
