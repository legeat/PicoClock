import busio
import board
import adafruit_ds3231
import adafruit_bus_device
import adafruit_register
import adafruit_display_text.label
import math
import time


days = ("Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота","Неділя")

i2c = busio.I2C(board.GP7,board.GP6)  # uses board.SCL and board.SDA
rtc = adafruit_ds3231.DS3231(i2c)

firstEnteringPageFlag = 1
_DAYS_IN_MONTH = (None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
_DAYS_BEFORE_MONTH = (None, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)

def _is_leap(year):
    "year -> 1 if leap year, else 0."
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def _days_in_month(year, month):
    "year, month -> number of days in that month in that year."
    assert 1 <= month <= 12, month
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month]

def _days_before_month(year, month):
    "year, month -> number of days in year preceding first day of month."
    assert 1 <= month <= 12, "month must be in 1..12"
    return _DAYS_BEFORE_MONTH[month] + (month > 2 and _is_leap(year))


def _days_before_year(year):
    "year -> number of days before January 1st of year."
    year = year - 1
    return year * 365 + year // 4 - year // 100 + year // 400


def _ymd2ord(year, month, day):
    "year, month, day -> ordinal, considering 01-Jan-0001 as day 1."
    assert 1 <= month <= 12, "month must be in 1..12"
    dim = _days_in_month(year, month)
    assert 1 <= day <= dim, "day must be in 1..%d" % dim
    return _days_before_year(year) + _days_before_month(year, month) + day

#DateTime Display
class DISPLAYSUBSYSTEM:
    def showDateTimePage(self,line1,line2,line3):
        while True:
            t = rtc.datetime  
            date =  "%02d" % t.tm_mday + '-' + "%02d" % t.tm_mon + '-' + "%04d" % t.tm_year
            dayOfTime = "%02d" % t.tm_hour + ':' + "%02d" % t.tm_min + ':' + "%02d" % t.tm_sec
            line1.text = date
            line2.text = dayOfTime
            line3.text=days[int(t.tm_wday)]
            line1.x = 0
            line1.y = 4
            line2.x = 0
            line2.y = 13
            line3.x = 0
            line3.y = 22

#List of pages
    def showSetListPage(self,line1,line2,_selectSettingOptions):
        global firstEnteringPageFlag
        line1.x = 0
        line1.y = 4
        line2.x = 0
        line2.y = 13
        line1.text = "шо по"
        if _selectSettingOptions == 0:
            line2.text = "часу?"
        if _selectSettingOptions == 1:
            line2.text = "даті?"
        if _selectSettingOptions == 2:
            line2.text = "підсвітці?"
        if firstEnteringPageFlag == 0:
            firstEnteringPageFlag = 1
            
#Time set page
    def timeSettingPage(self,line2,line3,_timeSettingLabel,_timeTemp):
        global firstEnteringPageFlag
        if firstEnteringPageFlag == 1:
            line2.x = 0
            line2.y = 13
            currentT = rtc.datetime
            _timeTemp[0] = currentT.tm_hour
            _timeTemp[1] = currentT.tm_min
            _timeTemp[2] = currentT.tm_sec
            firstEnteringPageFlag = 0
        currentTime = "%02d" % _timeTemp[0] + ':' + "%02d" % _timeTemp[1] + ':' + "%02d" % _timeTemp[2]
        line2.text = currentTime
        line3.text = "^"
        if _timeSettingLabel == 0:
            line3.x = 4
            line3.y = 22
        elif _timeSettingLabel == 1:
            line3.x = 21
            line3.y = 22
        else:
            line3.x = 38
            line3.y = 22
            
#Date set page
    def dateSettingPage(self,line2,line3,_timeSettingLabel,_dateTemp):
        global firstEnteringPageFlag
        if firstEnteringPageFlag == 1:
            line2.x = 0
            line2.y = 13
            currentD = rtc.datetime
            _dateTemp[0] = currentD.tm_year
            _dateTemp[1] = currentD.tm_mon
            _dateTemp[2] = currentD.tm_mday
            firstEnteringPageFlag = 0
        currentDate = "%02d" % _dateTemp[0] + '-' + "%02d" % _dateTemp[1] + '-' + "%02d" % _dateTemp[2]
        line2.text = currentDate
        line3.text = "^"
        if _timeSettingLabel == 0:
            line3.x = 9
            line3.y = 22
        elif _timeSettingLabel == 1:
            line3.x = 33
            line3.y = 22
        else:
            line3.x = 51
            line3.y = 22

    def onOffPage(self, line2, line3, _selectSettingOptions,_autoLightFlag):
        line2.x = 4
        line2.y = 13
        line3.x = 4
        line3.y = 22
        if _selectSettingOptions == 2:
            if _autoLightFlag:
                line2.text = "> on"
                line3.text = "  off"
                autoLightFlag = 1

            else:
                line2.text = "  on"
                line3.text = "> off"
                autoLightFlag = 0

        
    def setDateTime(self,_selectSettingOptions,_dateTemp,_timeTemp):
        getTime = rtc.datetime
        if _selectSettingOptions == 0:
            t = time.struct_time((getTime.tm_year, getTime.tm_mon, getTime.tm_mday, _timeTemp[0], _timeTemp[1], _timeTemp[2], getTime.tm_wday, -1, -1))
            rtc.datetime = t
        if _selectSettingOptions == 1:
            w = (_ymd2ord(_dateTemp[0],_dateTemp[1], _dateTemp[2]) + 6) % 7
            t = time.struct_time((_dateTemp[0], _dateTemp[1], _dateTemp[2], getTime.tm_hour, getTime.tm_min, getTime.tm_sec, w, -1, -1))
            rtc.datetime = t
            
