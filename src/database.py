#!/usr/bin/env python

from stream import *
from absolutes import *
from transfer import *

import MySQLdb

DATAINFOKEYLIST = ['DataID','SensorID','StationID','ColumnContents','ColumnUnits','DataFormat',
			'DataSamplingFilter','DataDigitalSampling','DataComponents','DataSamplingRate',
			'DataType','DataDeltaX','DataDeltaY','DataDeltaZ','DataDeltaF',
			'DataDeltaReferencePier','DataDeltaReferenceEpoch','DataScaleX',
			'DataScaleY','DataScaleZ','DataScaleUsed','DataCompensationX',
			'DataCompensationY','DataCompensationZ','DataSensorOrientation',
			'DataSensorAzimuth','DataSensorTilt','DataAngularUnit','DataPier',
			'DataAcquisitionLatitude','DataAcquisitionLongitude','DataLocationReference',
			'DataElevation','DataElevationRef','DataFlagModification','DataAbsFunc',
			'DataAbsDegree','DataAbsKnots','DataAbsMinTime','DataAbsMaxTime','DataAbsDate',
			'DataRating','DataComments']

SENSORSKEYLIST = ['SensorID','SensorName','SensorType','SensorSerialNum','SensorGroup','SensorDataLogger',
			'SensorDataLoggerSerNum','SensorDataLoggerRevision','SensorDataLoggerRevisionComment',
			'SensorDescription','SensorElements','SensorKeys','SensorModule','SensorDate',
			'SensorRevision','SensorRevisionComment','SensorRevisionDate']

STATIONSKEYLIST = ['StationID','StationName','StationIAGAcode','StationInstitution','StationStreet',
			'StationCity','StationPostalCode','StationCountry','StationWebInfo',
			'StationEmail','StationDescription']

"""
Standardtables:


SENSOR:
	SensorID: a combination of name, serialnumber and revision
	SensorName: a name defined by the observers to refer to the instrument
	SensorType: type of sensor (e.g. fluxgate, overhauzer, temperature ...)
        SensorSerialNum: its serial number
	SensorGroup: Geophysical group (e.g. Magnetism, Gravity, Environment, Meteorology, Seismology, Radiometry, ...) 
	SensorDataLogger: type of any electronics connected to the sensor 
	SensorDataLoggerSerNum: its serial number
        SensorDataLoggerRevision: 4 digit revision id '0001'
        SensorDataLoggerRevisionComment: description of revision
	SensorDescription: Description of the sensor
        SensorElements: Measured components e.g. x,y,z,t_sensor,t_electonics
        SensorKeys: the keys to be used for the elements in MagPy e.g. 'x,y,z,t1,t2', should have the same number as Elements (check MagPy Manual for this)
        SensorModule: type of sensor connection
        SensorDate: Date of Sensor construction/buy  
        SensorRevision: 4 digit number defining a revision ID
        SensorRevisionComment: Comment for current revision - changes to previous number (e.g. calibration)
        SensorRevisionDate: Date of revision - for 0001 this equals the SensorDate 
STATION:
        StationID: unique ID of the station e.g. IAGA code
        StationIAGAcode: 
        StationName: e.g. Cobenzl
        StationStreet: Stations address
        StationCity: Vienna
        StationEmail: 'ramon.egli@zamg.ac.at',
        StationPostalCode: '1190',
        StationCountry: 'Austria',
        StationInstitution: 'Zentralanstalt fuer Meteorologie und Geodynamik',
        StationWebInfo: 'http://www.zamg.ac.at',
        StationDescription: 'Running since 1951.'
DATAINFO:
	DataID: 
"""


def dbalter(db):
    """
    Use KEYLISTS and alter the Columns of tables DATAINFO, SENSORS, and STATIONS
    Can be used for changing (adding) contents to tables
    """
    if not db:
        loggerdatabase.error("dbalter: No database connected - aborting -- please create an empty database first")
        return
    cursor = db.cursor ()

    try:
        checksql = 'SELECT SensorID FROM SENSORS'
        cursor.execute(checksql)
        for key in SENSORSKEYLIST:
            try:
                checksql = 'SELECT ' + key+ ' FROM SENSORS'
                print "Checking key: ", key
                cursor.execute(checksql)
                print "Found key: ", key
            except:
                print "Missing key: ", key
                addstr = 'ALTER TABLE SENSORS ADD ' + key + ' CHAR(100)'
                cursor.execute(addstr)
                print "Key added: ", key
    except:
        print "Table SENSORS not existing"

    try:
        checksql = 'SELECT StationID FROM STATIONS'
        cursor.execute(checksql)
        for key in STATIONSKEYLIST:
            try:
                checksql = 'SELECT ' + key+ ' FROM STATIONS'
                print "Checking key: ", key
                cursor.execute(checksql)
                print "Found key: ", key
            except:
                print "Missing key: ", key
                addstr = 'ALTER TABLE STATIONS ADD ' + key + ' CHAR(100)'
                cursor.execute(addstr)
                print "Key added: ", key
    except:
        print "Table STATIONS not existing"

    try:
        checksql = 'SELECT DataID FROM DATAINFO'
        cursor.execute(checksql)
        for key in DATAINFOKEYLIST:
            try:
                checksql = 'SELECT ' + key+ ' FROM DATAINFO'
                print "Checking key: ", key
                cursor.execute(checksql)
                print "Found key: ", key
            except:
                print "Missing key: ", key
                addstr = 'ALTER TABLE DATAINFO ADD ' + key + ' CHAR(100)'
                cursor.execute(addstr)
                print "Key added: ", key
    except:
        print "Table DATAINFO not existing"

    db.commit()
    cursor.close ()


def dbsensorinfo(db,sensorid,sensorkeydict=None,sensorrevision = '0001'):
    """
    checks whether sensorinfo is already available in SENSORS tab
    if not, it creates a new line for the provided sensorid in the selected database db
    Keywords are all database fields provided as dictionary


    returns sensorid with revision number e.g. DIDD_235178_0001
    """

    sensorhead,sensorvalue,numlst = [],[],[]

    cursor = db.cursor()
   
    if sensorkeydict:
        for key in sensorkeydict:
            if key in SENSORSKEYLIST: 
                sensorhead.append(key)
                sensorvalue.append(sensorkeydict[key])

    print "sensor: ", sensorhead, sensorvalue

    check = 'SELECT SensorID, SensorRevision, SensorName, SensorSerialNum FROM SENSORS WHERE SensorID LIKE "'+sensorid+'%"'
    try:
        cursor.execute(check)
        rows = cursor.fetchall()
    except:
        print "sensorinfo: Could not access table SENSORS in database - creating table SENSORS"
        headstr = ' CHAR(100), '.join(SENSORSKEYLIST) + ' CHAR(100)'
        headstr = headstr.replace('SensorID CHAR(100)', 'SensorID CHAR(50) NOT NULL PRIMARY KEY')
        createsensortablesql = "CREATE TABLE IF NOT EXISTS SENSORS (%s)" % headstr
        cursor.execute(createsensortablesql)

    if len(rows) > 0: 
        # SensorID is existing in Table
        print "sensorinfo: Sensorid already existing in SENSORS"
        print "sensorinfo: rows: ", rows
        # Get the maximum revision number
        for i in range(len(rows)):
            rowval = rows[i][1]
            try:
                numlst.append(int(rowval))
            except:
                pass
        try:
            maxnum = max(numlst)
        except:
            maxnum = None
        if isinstance(maxnum, int):
            index = numlst.index(maxnum)
            sensorid = rows[index][0]
        else:
            print maxnum
            print 'dbsensorinfo: SensorRevision not set - changing to ', sensorrevision
            if rows[0][2] == None:
                sensoridsplit = sensorid.split('_')
                if len(sensoridsplit) == 2:
                    sensorserialnum = sensoridsplit[1]
                else:
                    sensorserialnum = sensorid
            else:
                sensorserialnum = rows[0][2]
            oldsensorid = sensorid
            sensorid = sensorid+'_'+sensorrevision
            updatesensorsql = 'UPDATE SENSORS SET SensorID = "' + sensorid + '", SensorRevision = "' + sensorrevision + '", SensorSerialNum = "' + sensorserialnum + '" WHERE SensorID = "' + oldsensorid + '"'
            cursor.execute(updatesensorsql)
    else:
        # SensorID is not existing in Table
        print "sensorinfo: Sensorid not yet existing in SENSORS"
        # Check whether given sensorid is incomplete e.g. revision number is missing
        print "sensor: ", sensorid
        if not 'SensorSerialNum' in sensorhead:
            sensoridsplit = sensorid.split('_')
            if len(sensoridsplit) == 2:
                sensorserialnum = sensoridsplit[1]
            elif len(sensoridsplit) == 3:
                sensorserialnum = sensoridsplit[1]
                if not 'SensorRevision' in sensorhead:
                    sensorhead.append('SensorRevision')
                    sensorvalue.append(sensoridsplit[2])
                index = sensorhead.index('SensorID')
                sensorvalue[index] = sensorid
            else:
                sensorserialnum = sensorid
            sensorhead.append('SensorSerialNum')
            sensorvalue.append(sensorserialnum)
        print "sensor: ", sensoridsplit, sensorserialnum
        if not 'SensorRevision' in sensorhead:
            sensorhead.append('SensorRevision')
            sensorvalue.append(sensorrevision)
            if not 'SensorID' in sensorhead:
                sensorhead.append('SensorID')
                sensorvalue.append(sensorid+'_'+sensorrevision)
            else:
                index = sensorhead.index('SensorID')
                sensorvalue[index] = sensorid+'_'+sensorrevision
            sensorid = sensorid+'_'+sensorrevision
        ### create an input for the new sensor
        sensorsql = "INSERT INTO SENSORS(%s) VALUES (%s)" % (', '.join(sensorhead), '"'+'", "'.join(sensorvalue)+'"')
        #print "Adding the following info to SENSORS: ", sensorsql
        cursor.execute(sensorsql)

    db.commit()
    cursor.close ()

    return sensorid


def dbdatainfo(db,sensorid,datakeydict=None,tablenum=None,defaultstation='WIC'):
    """
    provide sensorid and any relevant meta information for datainfo tab
    returns the full datainfoid

    If tablenum is specified, the corresponding table is selected and DATAINFO is updated with the provided datakeydict
    If tablenum = 'new', a new number is generated e.g. 0006 if no DATAINFO matching the provided info is found 
    If no tablenum is selected all data including all Datainfo is appended to the latest numbe if no DATAINFO matching the provided info is found and no conflict with the existing DATAINFO is found 

    An important keyword is the StationID. Please make sure to provide it. Otherwise the defaultvalue 'WIC' is used 

    Keywords are all database fields provided as dictionary
    
    Example:
    xxx = datainfo(db,'DIDD_3121331_S_01',{'DataDeltaX':0})

    Returns:
    DIDD_3121331_S_01_0001


    Application:

    1. read a datastream: stream = read(file)
    2. add additional header info: stream.header['StationID'] = 'WIC'
    3. Open a mysql database
    4. write stream2db
    5. check DATAINFO table: num = dbdatainfo(db,steam.header['SensorID'],stream.header,None,None)
          case 1: new sensor - not yet existing
                  tablenum = 0001
          case 2: sensor existing
                  default: select fitting datainfo (compare only provided fields - not in DATAINFO existing) and get highest number matching the info
                  tablenum=new: add new number, disregarding any previous matching DATAINFO 
                  tablenum=0003: returns 0003 if case 1 is satisfied 

    Not changeable are:
    DataMinTime CHAR(50)
    DataMaxTime CHAR(50)
    """

    searchlst = ' '
    datainfohead,datainfovalue=[],[]
    if datakeydict:
        for key in datakeydict:
            if key in DATAINFOKEYLIST: 
                datainfohead.append(key)
                datainfovalue.append(str(datakeydict[key]))
                searchlst += 'AND ' + key + ' = "'+ str(datakeydict[key]) +'" '

    datainfonum = '0001'
    numlst,intnumlst = [],[]

    cursor = db.cursor()
    
    # check for appropriate sensorid
    print "dbdatainfo: Reselecting SensorID" 
    sensorid = dbsensorinfo(db,sensorid,datakeydict)
    if 'SensorID' in datainfohead:
        index = datainfohead.index('SensorID') 
        datainfovalue[index] = sensorid
    print "-- SensorID is now ", sensorid 

    checkinput = 'SELECT StationID FROM DATAINFO WHERE sensorid = "'+sensorid+'"'
    try:
        cursor.execute(checkinput)
        rows = cursor.fetchall()
    except:
        print "datainfo: Column StationID not yet existing in table DATAINFO (very old magpy version) - creating it ..."
        stationaddstr = 'ALTER TABLE DATAINFO ADD StationID CHAR(50) AFTER SensorID'
        cursor.execute(stationaddstr)

    checkinput = 'SELECT DataID FROM DATAINFO WHERE sensorid = "'+sensorid+'"'
    print 'dbdatainfo: ', checkinput 
    try:
        cursor.execute(checkinput)
        rows = cursor.fetchall()
        print "Number of existing DATAINFO lines: ", rows
    except:
        print "datainfo: Could not access table DATAINFO in database"
        datainfostr = 'DataID CHAR(50) NOT NULL PRIMARY KEY, SensorID CHAR(50), ColumnContents TEXT, ColumnUnits TEXT, DataFormat CHAR(20),DataMinTime CHAR(50), DataMaxTime CHAR(50), DataSamplingFilter CHAR(100), DataDigitalSampling CHAR(100), DataComponents CHAR(10), DataSamplingRate CHAR(100), DataType CHAR(100), DataDeltaX DECIMAL(20,9), DataDeltaY DECIMAL(20,9), DataDeltaZ DECIMAL(20,9),DataDeltaF DECIMAL(20,9),DataDeltaReferencePier CHAR(20),DataDeltaReferenceEpoch CHAR(50),DataScaleX DECIMAL(20,9),DataScaleY DECIMAL(20,9),DataScaleZ DECIMAL(20,9),DataScaleUsed CHAR(2),DataSensorOrientation CHAR(10),DataSensorAzimuth DECIMAL(20,9),DataSensorTilt DECIMAL(20,9), DataAngularUnit CHAR(5),DataPier CHAR(20),DataAcquisitionLatitude DECIMAL(20,9), DataAcquisitionLongitude DECIMAL(20,9), DataLocationReference CHAR(20), DataElevation DECIMAL(20,9), DataElevationRef CHAR(10), DataFlagModification CHAR(50), DataAbsFunc CHAR(20), DataAbsDegree INT, DataAbsKnots DECIMAL(20,9), DataAbsMinTime CHAR(50), DataAbsMaxTime CHAR(50), DataAbsDate CHAR(50), DataRating CHAR(10), DataComments TEXT'
        createdatainfotablesql = "CREATE TABLE IF NOT EXISTS DATAINFO (%s)" % datainfostr
        cursor.execute(createdatainfotablesql)

    # check whether input in DATAINFO with sensorid is existing already
    if len(rows) > 0:
        # Get maximum number
        for i in range(len(rows)):
            rowval = rows[i][0].replace(sensorid + '_','')
            try:
                numlst.append(int(rowval))
            except:
                pass
        maxnum = max(numlst)
        print "dbdatainfo Maxnum: ", maxnum
        # Perform intensive search using any given meta info
        intensivesearch = 'SELECT DataID FROM DATAINFO WHERE SensorID = "'+sensorid+'"' + searchlst
        print "dbdatainfo Searchlist: ", intensivesearch
        cursor.execute(intensivesearch)
        intensiverows = cursor.fetchall()
        print "dbdatainfo intensiverows: ", len(intensiverows)
        if len(intensiverows) > 0:
            for i in range(len(intensiverows)):
                # if more than one record is existing select the latest (highest) number
                introwval = intensiverows[i][0].replace(sensorid + '_','')
                try:
                    intnumlst.append(int(introwval))
                except:
                    pass
            intmaxnum = max(intnumlst)
            datainfonum = '{0:04}'.format(intmaxnum)
        else:
            datainfonum = '{0:04}'.format(maxnum+1)
            # select maximum number + 1
            if 'DataID' in datainfohead:
                index = datainfohead.index('DataID') 
                datainfovalue[index] = sensorid + '_' + datainfonum
            else:
                datainfohead.append('DataID')
                datainfovalue.append(sensorid + '_' + datainfonum)
            datainfosql = 'INSERT INTO DATAINFO(%s) VALUES (%s)' % (', '.join(datainfohead), '"'+'", "'.join(datainfovalue)+'"')
            print datainfosql
            cursor.execute(datainfosql)
        datainfoid = sensorid + '_' + datainfonum
    else:
        # return 0001
        datainfoid = sensorid + '_' + datainfonum
        datainfohead.append('DataID')
        datainfovalue.append(datainfoid)
        # and create datainfo input
        print datainfohead, datainfovalue
        datainfosql = 'INSERT INTO DATAINFO(%s) VALUES (%s)' % (', '.join(datainfohead), '"'+'", "'.join(datainfovalue)+'"')
        cursor.execute(datainfosql)

    db.commit()
    cursor.close ()

    return datainfoid


def stream2db(db, datastream, noheader=None, mode=None, tablename=None):
    """
    Method to write datastreams to a mysql database
    mode: replace -- replaces existing table contents with new one, also replaces informations from sensors and station table
    mode: delete -- deletes existing tables and writes new ones -- remove (or make it extremeley difficult to use) this method after initializing of tables
    mode: extend -- only add new data points with unique ids (default)
    mode: insert -- ??

    New Header informations are created with modes 'replace' and 'delete'.
    If mode = 'extend' then check for the existence of sensorid and datainfo first -> if not available then request mode = 'insert'
    Mode 'extend' requires an existing input in sensor, station and datainfo tables: tablename needs to be given.
    Mode 'insert' checks for the existance of existing inputs in sensor, station and datainfo, and eventually adds a new datainfo tab.
    Mode 'replace' checks for the existance of existing inputs in sensor, station and datainfo, and replaces the stored information: optional tablename can be given.
         if tablename is given, then data from this table is replaced - otherwise only data from station and sensor are replaced
    Mode 'delete' completely deletes all tables and creates new ones. 

    TODO:
    - add all data automatically to the datatable with identical info 
    - create additional ids only if datainfo not existing 
    - make it possible to create spezial tables by defining an extension (e.g. _sp2013min) where sp indicates special        

    Example:
    """

    if not mode:
        mode = 'insert'

    if not db:
        print "No database connected - aborting -- please create an empty database first"
        return
    cursor = db.cursor ()

    headdict = datastream.header
    head, line = [],[]
    sensorhead, sensorvalue = [],[]
    datainfohead, datainfovalue = [],[]
    stationhead, stationvalue = [],[]
    collst, unitlst = [],[]
    datacolumn = []
    datakeys, dataheads = [],[]
    datavals = []

    if not noheader:
        pass

    print "### Writing stream to database ###"
    print "--- Starting header extraction ..."

    if len(datastream) < 1:
        print "--- stream2DB: Empty datastream. Aborting ..."
        return

    # check SENSORS information
    print "--- Checking SENSORS table ..."
    sensorid = dbsensorinfo(db,headdict['SensorID'],headdict)
    print "Working with: ", sensorid
    # updating dict
    headdict['SensorID'] = sensorid
    # HEADER INFO - TABLE
    # read Header information
    for key in headdict:
        if key.startswith('Sensor'):
            if key == "SensorID":
                #sensorid = headdict[key]
                sensorhead.append(key)
                sensorvalue.append(sensorid)
            else:
                sensorhead.append(key)
                sensorvalue.append(headdict[key])
        elif key.startswith('Data'):
            if not key == 'DataInterval': 
                datainfohead.append(key)
                datainfovalue.append(headdict[key])
        elif key.startswith('Station'):
            if key == "StationID":
                stationid = headdict[key]
                stationhead.append(key)
            else:
                if not key == "Station": 
                    stationhead.append(key)
            if not key == "Station": 
                stationvalue.append(headdict[key].replace('http://',''))
        elif key.startswith('col'):
            pass            
        elif key.startswith('unit'):
            pass
        else:
            #key not transferred to DB
            print "--- Something: ", key, headdict[key]

    # If no sensorid is available then report error and return:
    if not sensorid:
        print "--- stream2DB: no SensorID specified in stream header. Cannot proceed ..."
        return
    if not stationid:
        print "--- stream2DB: no StationID specified in stream header. Cannot proceed ..."
        return

    #if 'SensorID' in sensorhead:
    #    index = sensorhead.index('SensorID')


    print "--- Checking column contents ..."
    # HEADER INFO - DATA TABLE
    # select only columss which contain data and get units and column contents
    for key in KEYLIST:
       #print key
       colstr = '-'
       unitstr = '-'
       if not key == 'time':
           ind = KEYLIST.index(key)
           try:
               keylst = np.asarray([row[ind] for row in datastream if not isnan(row[ind])])
               if len(keylst) > 0:
                   dataheads.append(key + ' FLOAT')
                   datakeys.append(key)
           except:
               keylst = np.asarray([row[ind] for row in datastream if not row[ind]=='-'])
               if len(keylst) > 0:
                   dataheads.append(key + ' CHAR(100)')
                   datakeys.append(key)
       for hkey in headdict:
           if key == hkey.replace('col-',''):
               colstr = headdict[hkey]            
           elif key == hkey.replace('unit-col-',''):
               unitstr = headdict[hkey]            
       collst.append(colstr)            
       unitlst.append(unitstr)            

    colstr =  '_'.join(collst)
    unitstr = '_'.join(unitlst)

    # Update the column data at the end together with time

    st = datetime.strftime(num2date(datastream[0].time).replace(tzinfo=None),'%Y-%m-%d %H:%M:%S.%f')
    et = datetime.strftime(num2date(datastream[-1].time).replace(tzinfo=None),'%Y-%m-%d %H:%M:%S.%f')

    print "--- Checking/Updating existing tables ..."
    
    if mode=='extend':
        if not tablename:
            print "stream2DB: tablename must be specified for mode 'extend'" 
            return
        # Check for the existance of data base contents and sufficient header information
        searchstation = 'SELECT * FROM STATIONS WHERE StationID = "'+stationid+'"' 
        searchsensor = 'SELECT * FROM SENSORS WHERE SensorID = "'+sensorid+'"'
        searchdatainfo = 'SHOW TABLES LIKE "'+tablename+'"'

        try:
            cursor.execute(searchstation)
        except:
            print "--- stream2DB: Station table not existing - use mode 'insert' - aborting with error"
            raise

        rows = cursor.fetchall()
        if not len(rows) > 0:
            print "--- stream2DB: Station is not yet existing - use mode 'insert' - aborting with error"
            raise
            #return

        cursor.execute(searchsensor)
        rows = cursor.fetchall()
        if not len(rows) > 0:
            print "stream2DB: Sensor is not yet existing - use mode 'insert'"
            raise
        cursor.execute(searchdatainfo)
        rows = cursor.fetchall()
        if not len(rows) > 0:
            print "stream2DB: Selected data table is not yet existing - check tablename"
            raise
        print "Check finished"
    else:
        # SENSOR TABLE
        # Create sensor table input
        headstr = ' CHAR(100), '.join(SENSORSKEYLIST) + ' CHAR(100)'
        headstr = headstr.replace('SensorID CHAR(100)', 'SensorID CHAR(50) NOT NULL PRIMARY KEY')
        headstr = headstr.replace('SensorDescription CHAR(100)', 'SsensorDescription TEXT')
        createsensortablesql = "CREATE TABLE IF NOT EXISTS SENSORS (%s)" % headstr
        sensorsql = "INSERT INTO SENSORS(%s) VALUES (%s)" % (', '.join(sensorhead), '"'+'", "'.join(sensorvalue)+'"')

        # STATION TABLE
        # Create station table input
        stationstr = ' CHAR(100), '.join(STATIONSKEYLIST) + ' CHAR(100)'
        stationstr = stationstr.replace('StationID CHAR(100)', 'StationID CHAR(50) NOT NULL PRIMARY KEY')
        stationstr = stationstr.replace('StationDescription CHAR(100)', 'StationDescription TEXT')
        stationstr = 'StationID CHAR(50) NOT NULL PRIMARY KEY, StationName CHAR(100), StationIAGAcode CHAR(10), StationInstitution CHAR(100), StationStreet CHAR(50), StationCity CHAR(50), StationPostalCode CHAR(20), StationCountry CHAR(50), StationWebInfo CHAR(100), StationEmail CHAR(100), StationDescription TEXT'
        createstationtablesql = "CREATE TABLE IF NOT EXISTS STATIONS (%s)" % stationstr
        stationsql = "INSERT INTO STATIONS(%s) VALUES (%s)" % (', '.join(stationhead), '"'+'", "'.join(stationvalue)+'"')

        # DATAINFO TABLE
        # Create datainfo table
        datainfostr = 'DataID CHAR(50) NOT NULL PRIMARY KEY, SensorID CHAR(50), StationID CHAR(50), ColumnContents TEXT, ColumnUnits TEXT, DataFormat CHAR(20),DataMinTime CHAR(50), DataMaxTime CHAR(50), DataSamplingFilter CHAR(100), DataDigitalSampling CHAR(100), DataComponents CHAR(10), DataSamplingRate CHAR(100), DataType CHAR(100), DataDeltaX DECIMAL(20,9), DataDeltaY DECIMAL(20,9), DataDeltaZ DECIMAL(20,9),DataDeltaF DECIMAL(20,9),DataDeltaReferencePier CHAR(20),DataDeltaReferenceEpoch CHAR(50),DataScaleX DECIMAL(20,9),DataScaleY DECIMAL(20,9),DataScaleZ DECIMAL(20,9),DataScaleUsed CHAR(2),DataSensorOrientation CHAR(10),DataSensorAzimuth DECIMAL(20,9),DataSensorTilt DECIMAL(20,9), DataAngularUnit CHAR(5),DataPier CHAR(20),DataAcquisitionLatitude DECIMAL(20,9), DataAcquisitionLongitude DECIMAL(20,9), DataLocationReference CHAR(20), DataElevation DECIMAL(20,9), DataElevationRef CHAR(10), DataFlagModification CHAR(50), DataAbsFunc CHAR(20), DataAbsDegree INT, DataAbsKnots DECIMAL(20,9), DataAbsMinTime CHAR(50), DataAbsMaxTime CHAR(50), DataAbsDate CHAR(50), DataRating CHAR(10), DataComments TEXT'
        createdatainfotablesql = "CREATE TABLE IF NOT EXISTS DATAINFO (%s)" % datainfostr

        #print createsensortablesql
        #print sensorsql
        #print createstationtablesql
        #print stationsql
        #print createdatainfotablesql

        if mode == "delete":
            cursor.execute("DROP TABLE IF EXISTS SENSORS") 
            cursor.execute("DROP TABLE IF EXISTS STATIONS") 
            cursor.execute("DROP TABLE IF EXISTS DATAINFO") 

        cursor.execute(createsensortablesql)
        cursor.execute(createstationtablesql)
        cursor.execute(createdatainfotablesql)

        if mode == "replace":
            try:
                cursor.execute(sensorsql.replace("INSERT","REPLACE"))
                cursor.execute(stationsql.replace("INSERT","REPLACE"))
            except:
                print "Write MySQL: Replace failed"
        else:
            try:
                print "executing: ", sensorsql
                cursor.execute(sensorsql)
            except:
                print "Sensor data already existing: use mode 'replace' to overwrite"
                print "Eventually a field is not existing"
                pass
            try:
                cursor.execute(stationsql)
            except:
                print "Station data already existing: use mode 'replace' to overwrite"
                print "Eventually a field is not existing"
                pass



        # check whether an identical datainfo table is already existing (use modifiactiondate of flags)
        # if not get last running revision number of sensorid and add 1 - add datainfo and sensordata
        # if yes do not write table

        # DATAINFO TABLE
        # check whether contents exists

        tablename = dbdatainfo(db,sensorid,headdict,None,stationid)


    print "Creating/updating data table " + tablename

    createdatatablesql = "CREATE TABLE IF NOT EXISTS %s (time CHAR(40) NOT NULL PRIMARY KEY, %s)" % (tablename,', '.join(dataheads))
    cursor.execute(createdatatablesql)

    for elem in datastream:
        for el in datakeys:
            if datastream._is_number(eval('elem.'+el)):
                val = str(eval('elem.'+el))
            else:
                val = '"'+str(eval('elem.'+el))+'"'
            if val=='nan':
                val = 'null'
            datavals.append(val)
        ct = datetime.strftime(num2date(elem.time).replace(tzinfo=None),'%Y-%m-%d %H:%M:%S.%f')
        insertdatasql = "INSERT INTO %s(time, %s) VALUES (%s, %s)" % (tablename, ', '.join(datakeys), '"'+ct+'"', ', '.join(datavals))
        if mode == "replace":
            try:
                cursor.execute(insertdatasql.replace("INSERT","REPLACE"))
            except:
                try:
                    cursor.execute(insertdatasql)
                except:
                    print "Write MySQL: Replace failed"
        else:
            try:
                cursor.execute(insertdatasql)
            except:
                print "Record at %s already existing: use mode replace to overwrite" % ct
        datavals  = []

    # Select MinTime and MaxTime from datatable and eventually update datainfo
    getminmaxtimesql = "Select MIN(time),MAX(time) FROM " + tablename
    cursor.execute(getminmaxtimesql)
    rows = cursor.fetchall()
    print "Table now covering a time range from ", rows[0][0], " to ", rows[0][1]
    updatedatainfotimesql = 'UPDATE DATAINFO SET DataMinTime = "' + rows[0][0] + '", DataMaxTime = "' + rows[0][1] +'", ColumnContents = "' + colstr +'", ColumnUnits = "' + unitstr +'" WHERE DataID = "'+ tablename + '"'
    #print updatedatainfotimesql
    cursor.execute(updatedatainfotimesql)
    
    db.commit()
    cursor.close ()


def db2stream(db,sensorid=None, begin=None, end=None, tableext=None, sql=None):
    """
    extract data streams from the data base
    sql: provide any additional search criteria
        example: sql = "DataSamplingRate=60 AND DataType='variation'"
    """
    wherelist = []
    stream = DataStream()

    if not db:
        print "No database connected - aborting"
        return stream

    cursor = db.cursor ()
    
    if not tableext and not sensorid:
        print "Aborting ... either sensorid or table must be specified"
        return
    if begin:
        wherelist.append('time >= "' + begin + '"')
    if end:
        wherelist.append('time <= "' + end + '"')
    if len(wherelist) > 0:
        whereclause = ' AND '.join(wherelist)
    else:
        whereclause = ''
    if sql:
        if len(whereclause) > 0:
            whereclause = whereclause + ' AND ' + sql
        else:
            whereclause = sql

    print whereclause

    if not tableext:
        getdatainfo = 'SELECT DataID FROM DATAINFO WHERE SensorID = "' + sensorid + '"'
        cursor.execute(getdatainfo)
        rows = cursor.fetchall()
        for table in rows:
            print "Extracting field values from table ", table[0]
            if len(whereclause) > 0:
                getdatasql = 'SELECT * FROM ' + table[0] + ' WHERE ' + whereclause
            else:
                getdatasql = 'SELECT * FROM ' + table[0]
            getcolumnnames = 'SHOW COLUMNS FROM ' + table[0]
            # sqlquery to get column names of table - store that in keylst
            keylst = []
            cursor.execute(getcolumnnames)
            rows = cursor.fetchall()
            for line in rows:
                keylst.append(line[0])
            # sqlquery to extract data
            cursor.execute(getdatasql)
            rows = cursor.fetchall()
            for line in rows:
                row = LineStruct()
                for i, elem in enumerate(line):
                    if keylst[i]=='time':
                        exec('row.'+keylst[i]+' = date2num(stream._testtime(elem))')
                    else:
                        exec('row.'+keylst[i]+' = elem')
                    #print elem
                stream.add(row)
    else:
        if len(whereclause) > 0:
            getdatasql = 'SELECT * FROM ' + tableext + ' WHERE ' + whereclause
        else:
            getdatasql = 'SELECT * FROM ' + tableext
        getcolumnnames = 'SHOW COLUMNS FROM ' + tableext
        # sqlquery to get column names of table - store that in keylst
        keylst = []
        cursor.execute(getcolumnnames)
        rows = cursor.fetchall()
        for line in rows:
            keylst.append(line[0])
        # sqlquery to extract data
        cursor.execute(getdatasql)
        rows = cursor.fetchall()
        for line in rows:
            row = LineStruct()
            for i, elem in enumerate(line):
                if keylst[i]=='time':
                    exec('row.'+keylst[i]+' = date2num(stream._testtime(elem))')
                else:
                    if elem == None:
                        elem = float(NaN)
                        #print "found"
                        #if keylst[i]=='x':
                        #    elem = float(NaN)
                    exec('row.'+keylst[i]+' = elem')
            stream.add(row)

    cursor.close ()
    return stream


def getBaselineProperties(db,datastream,distream=None):
    """
    method to extract baseline properties from a DB for a given time
    reads starttime, endtime, and baseline properties (like function, degree, knots etc) from DB
    if no information is provided then the baseline method has to be used
    The method creates database inputs for each analyzed segment using the 'replace' mode
    ideally 
    """
    stream = DataStream()
    basecorr = DataStream()
    streamdat = []
    flist = []

    if not db:
        print "No database connected - aborting"
        return stream

    cursor = db.cursor ()

    sensid = datastream.header['SensorID']

    if not sensid or len(sensid) < 1:
        print "No Sensor specified in datastream header - aborting"
        return stream

    # Remove flagged data
    #datastream = datastream.remove_flagged()
        
    # Test whether table "Baseline" exists
    testsql = 'SHOW TABLES LIKE "BASELINE"'
    cursor.execute(testsql)
    rows = cursor.fetchall()
    if len(rows) < 1:
        print "No Baselinetable existing - creating an empty table in the selected database and aborting then"
        baseheadstr = 'SensorID CHAR(50) NOT NULL, MinTime DATETIME, MaxTime DATETIME, TmpMaxTime DATETIME, BaseFunction CHAR(50), BaseDegree INT, BaseKnots FLOAT, BaseComment TEXT'
        createbasetablesql = "CREATE TABLE IF NOT EXISTS BASELINE (%s)" % baseheadstr
        cursor.execute (createbasetablesql)
        # TmpMaxTime is used to store current date if MaxTime is Emtpy
        #basesql = "INSERT INTO BASELINE(%s) VALUES (%s)" % (', '.join(sensorhead), '"'+'", "'.join(sensorvalue)+'"')
        # Insert code here for creating empty table
        return

    # get starttime
    starttime = datastream._testtime(datastream[0].time)
    endtime = datastream._testtime(datastream[-1].time)

    # get the appropriate basedatatable database input
    #absstream = ...
    # Test whether table "SENSORID_Basedata" exists
    testsql = 'SHOW TABLES LIKE "%s_BASEDATA"' % sensid
    cursor.execute(testsql)
    rows = cursor.fetchall()
    if len(rows) < 1:
        print "No Basedatatable existing - trying to create one from file"
        if not distream:
            print "No DI data provided - aborting"
            return
        stream2db(db,distream,mode='replace',tablename=sensid+'_BASEDATA')
    else:
        if distream:
            print "Resetting basedata table from file"
            stream2db(db,distream,mode='replace',tablename=sensid+'_BASEDATA')
            distream = distream.remove_flagged()            
        else:
            table = sensid+'_BASEDATA' 
            distream = db2stream(db,tableext=table)
            distream = distream.remove_flagged()
            
    #print sensid


    # update TmpMaxTime column with current time in empty MaxTime Column
    currenttime = datetime.strftime(datetime.utcnow(),'%Y-%m-%d %H:%M:%S')
    copy2tmp = "UPDATE BASELINE SET TmpMaxTime = MaxTime"
    insertdatesql = "UPDATE BASELINE SET TmpMaxTime = '%s' WHERE TmpMaxTime IS NULL" % (currenttime)

    cursor.execute(copy2tmp)
    cursor.execute(insertdatesql)
    #
    select = 'MinTime, TmpMaxTime, BaseFunction, BaseDegree, BaseKnots'
    # start before and end within datastream time range
    where1 = '"%s" < MinTime AND "%s" <= TmpMaxTime AND "%s" > MinTime' % (starttime,endtime,endtime)
    # start within and end after datastream time range
    where2 = '"%s" >= MinTime AND "%s" < TmpMaxTime AND "%s" > MaxTime' % (starttime,starttime,endtime)
    # start and end within datastream time range
    where3 = '"%s" > MinTime AND "%s" < TmpMaxTime AND "%s" > MinTime AND "%s" < MaxTime' % (starttime,starttime,endtime,endtime)
    # if where1 to where3 unsuccessfull then use where4
    where4 = '"%s" <= MinTime AND "%s" >= TmpMaxTime' % (starttime,endtime)

    where = 'SensorID = "%s" AND ((%s) OR (%s) OR (%s) OR (%s))' % (sensid,where1,where2,where3,where4)
    
    getbaselineinfo = 'SELECT %s FROM BASELINE WHERE %s' % (select, where)
    cursor.execute(getbaselineinfo)
    rows = cursor.fetchall()
    print rows
    for line in rows:
        # Get stream between min and maxtime and do the baseline fit
        start = date2num(line[0])
        stop = date2num(line[1])
        datalist = [row for row in datastream if start <= row.time <= stop]
        #To do: if MinTime << starttime then distart = start - 30 Tage
        if line[0] < starttime-timedelta(days=30):
            distart = date2num(starttime-timedelta(days=30))
        else:
            distart = start
        #To do: if MaxTime >> endtime then distop = stop + 30 Tage 
        if line[0] > endtime+timedelta(days=30):
            distop = date2num(endtime+timedelta(days=30))
        else:
            distop = stop
        print start,distart, stop,distop
        dilist = [row for row in distream if start <= row.time <= stop]
        part = DataStream(datalist,datastream.header)
        abspart =  DataStream(dilist,distream.header)
        fitfunc = line[2]
        try:
            fitdegree=float(line[3])
        except:
            fitdegree=5
        try:
            fitknots=float(line[4])
        except:
            fitknots=0.05

        # return baseline function as well
        basecorr,func = part.baseline(abspart,fitfunc=fitfunc,fitdegree=fitdegree,knotstep=fitknots,plotbaseline=True,returnfunction=True)
        flist.append(func)
        dat = [row for row in basecorr]
        deltaf = abspart.mean('df',meanfunction='median',percentage=1)
        # Update header information
        part.header['DataDeltaF'] = deltaf
        part.header['DataAbsMinTime'] = datetime.strftime(num2date(dat[0].time),"%Y-%m-%d %H:%M:%S")
        part.header['DataAbsMaxTime'] = datetime.strftime(num2date(dat[-1].time),"%Y-%m-%d %H:%M:%S")
        part.header['DataAbsKnots'] = str(fitknots)
        part.header['DataAbsDegree'] = str(fitdegree)
        part.header['DataAbsFunc'] = fitfunc
        part.header['DataType'] = 'preliminary'
        streamdat.extend(dat)
        print "Stream: ", len(streamdat), len(basecorr)
        stream2db(db,DataStream(dat,part.header),mode='replace')

    print flist
    for elem in flist:
        for key in KEYLIST:
            fkey = 'f'+key
            if fkey in elem[0]:
                ttmp = arange(0,1,0.0001)# Get the minimum and maximum relative times
                #ax.plot_date(self._denormalize(ttmp,function[1],function[2]),function[0][fkey](ttmp),'r-')
            
    return DataStream(streamdat,datastream.header)
    
    db.commit()

