# Trafikverket example
#
# Author: Net-Time 2019
#
#
"""
<plugin key="STV" name="Trafikverket API" author="Net-Time" version="0.2.9" wikilink="https://github.com/Net-time" externallink="https://api.trafikinfo.trafikverket.se/">
    <description>
        <h2>Trafikverket weather example</h2><br/>
        Polls a road weather station every 10 minutes.<br/>
        
        Get your personal API-Key at https://api.trafikinfo.trafikverket.se/Account/Register
    </description>
    <params>
        <param field="Address" label="Trafikverket API" width="200px" required="true" default="api.trafikinfo.trafikverket.se"/>
        <param field="Mode1" label="Data Format" width="200px" required="true" default="/v1.1/data.json"/>
        <param field="Mode2" label="Road Station" width="200px" required="true" default="Högakustenbron Topp"/>
        <param field="Mode3" label="API-Key" width="250px" required="true" default=""/>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json

beats = 0
minutes = 0
rain= 0.0

from collections import deque

rainHistory = deque([0.0]*6)

class BasePlugin:
    httpConn = None
    runAgain = 6
    disconnectCount = 0
    apiRequest= """<REQUEST><LOGIN authenticationkey="LoGiN-KeY"/><QUERY objecttype="WeatherStation" schemaversion="1"><FILTER><EQ name="Name" value="Överboda" /></FILTER><INCLUDE>Measurement.Air.Temp</INCLUDE><INCLUDE>Measurement.MeasureTime</INCLUDE><INCLUDE>Measurement.Wind.Force</INCLUDE><INCLUDE>Measurement.Air.RelativeHumidity</INCLUDE><INCLUDE>Measurement.Wind.Direction</INCLUDE><INCLUDE>Measurement.Wind.ForceMax</INCLUDE><INCLUDE>Measurement.Precipitation.Amount</INCLUDE></QUERY></REQUEST>"""

    def __init__(self):
        return

    def onStart(self):
        global url, apiData
        Domoticz.Log("OnStart")
        Domoticz.Heartbeat(20)
        self.apiRequest = self.apiRequest.replace("LoGiN-KeY",Parameters["Mode3"])
        #Address=Parameters["Address"]

        self.sProtocol = "HTTPS"
        self.httpConn = Domoticz.Connection(Name=self.sProtocol+" Test",
                                            Transport="TCP/IP", Protocol= "HTTPS",
                                            Address= Parameters["Address"], Port ="443")
        self.httpConn.Connect()
        if 1==1: #(Parameters["Mode4"] == "True"):
            if len(Devices)==0:
                    Domoticz.Device("STV", Unit=1, Type= 84, Subtype=16).Create()
                    Domoticz.Device("STV2", Unit=2, Type= 86, Subtype=1).Create()
                    #Domoticz.Device("STV3", Unit=3, Type= 85, Subtype=1).Create()
                    Domoticz.Log("Created device: ")

    def onStop(self):
        Domoticz.Log("onStop - Plugin is stopping.")

    def onConnect(self, Connection, Status, Description):
        global apiData,url2
        data3= self.apiRequest
        Domoticz.Log("onConnect")
        data4 = data3.encode('utf-8')
        if (Status == 0):
            Domoticz.Log("Connected successfully to Trafikverket.")
            sendData = { 'Verb' : 'POST','URL'  : Parameters["Mode1"], 'Data' : data4 ,
                         'Headers' : { 'Content-Type': 'text/xml',
                                       'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                       'Host': Parameters["Address"] +":443", \
                                       'User-Agent':'Domoticz/1.0' }
                        }
            VerBose(str(sendData))
            Connection.Send(sendData)
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Mode1"]+" with error: "+Description)

    def onMessage(self, Connection, Data):
        global rain
        Status = int(Data["Status"])
        directions =['N','NNE','NE','ENE','E','ESE','SE','SSE',
                     'S','SSW','SW','WSW','W','WNW','NW','NNW','N']
        #Domoticz.Log("Data: "+str(Data))
        if (Status == 200):
            data = json.loads( Data["Data"].decode("ascii", "ignore")) 
            reply=(data["RESPONSE"]["RESULT"][0] ["WeatherStation"] [0]["Measurement"])
            Domoticz.Log("Reply: " + str(reply))
            airTemp=str(reply["Air"]["Temp"])
            try:
                airHumidity=str(reply["Air"]["RelativeHumidity"])
            except:
                airHumidity="0"
                Domoticz.Log("Air Humidity missing!")
            windForce=str(reply["Wind"]["Force"]*10)
            windForceMax=str(reply["Wind"]["ForceMax"]*10)            
            windDirection=reply["Wind"]["Direction"]
            windDirectionCardinal=directions[(int(windDirection/22.5))]
            windDirectionStr=str(windDirection)
            try:
                currentRain = reply["Precipitation"]["Amount"]
                precipitationAmount = str((currentRain*100))
                raintemp = rain + (currentRain/6)
                rain =raintemp
                rainData= precipitationAmount+";"+ str(round(float(rain),1))
                Domoticz.Log("rain5 "+ rainData)                
                Devices[3].Update(nValue=0, sValue= rainData)
            except:
                Domoticz.Log("Rain data missing!")
            Devices[1].Update(nValue=0, sValue=str(airTemp+";"+airHumidity+";0;0;0"))
            Devices[2].Update(nValue=0, sValue=str(windDirectionStr+";"+windDirectionCardinal+";"+windForce+";"+windForceMax+";"+airTemp+";0"))

            
            #Domoticz.Log("Good Response received from Trafikverket")
        elif (Status == 302):
            Domoticz.Log("Trafikverket returned a Page Moved Error.")
        elif (Status == 400):
            Domoticz.Error("Trafikverket returned a Bad Request Error.")
        elif (Status == 500):
            Domoticz.Error("Trafikverket returned a Server Error.")
        elif (Status == 503):
            Domoticz.Error("Trafikverket returned a Bad Request Error.")
        else:
            Domoticz.Error("Trafikverket returned a status: "+str(Status))

            #self.httpConn = None #domoticz Async Secure Read Exception: 1, stream truncated 

        
    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onDisconnect(self, Connection):
        return
        #Domoticz.Log("onDisconnect called for connection to: "+Connection.Address+":"+Connection.Port)

    def onHeartbeat(self):
        global beats,minutes
        beats +=1
        if beats >= 3:
            minutes +=1 ; beats = 0
        VerBose('Heartbeat: '+ str(beats)+ ", Minutes: "+ str(minutes))
        if (self.httpConn != None and (self.httpConn.Connecting() or self.httpConn.Connected())):
            VerBose("onHeartbeat called, Connection is alive.")          
        else:
            if minutes >= 10:
                if (self.httpConn == None):
                    self.httpConn = Domoticz.Connection(Name=self.sProtocol+" Test",
                                                        Transport="TCP/IP", Protocol= "HTTPS",
                                                        Address= Parameters["Address"], Port ="443")
                self.httpConn.Connect()
                minutes = 0
            else:
                Domoticz.Debug("onHeartbeat called, run again in "+str(self.runAgain)+" heartbeats.")    
        if minutes >= 10: #failsafe
            minutes=0
            
def UpdateDevice(Unit, nValue, sValue, TimedOut):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (Devices[Unit].TimedOut != TimedOut):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
    
def VerBose(text):
    if Parameters["Mode6"] != "0":
        Domoticz.Log(text)
    return