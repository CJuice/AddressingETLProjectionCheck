"""
Check the projection of every feature class in the Submitted Data Geodatabase. Helps avoid errors in the
Project Tool when the main Preprocessing script is run.
Created by CJuice on 20171208
"""
# IMPORTS
from os import path
from arcpy import ListFeatureClasses
from arcpy import env
from arcpy import GetMessages
from arcpy import Describe
import logging
import datetime

# VARIABLES
strPSAGeoprocessingError = "GP Error: {}"
lsFeatureClassesInMasterGDB = None
# strRootGeodatabasePath = r"D:\ETL\Addresses\Data\SubmittedData.gdb"
strRootGeodatabasePath = r"E:\Addressing_FMEProject\Raw data\ConsolidatedAddressData_Summer2017.gdb" #TESTING
    # Projection/GCS expectations for datasets as provided by Jeyan 20171211
    # tuple format is (WKID aka Factory Code, Projected Coord Sys Name)
tupNAD83_SPMD1900_feet = (2248,"NAD_1983_StatePlane_Maryland_FIPS_1900_Feet")
tupNAD83_SPMD1900_meters = (26985,"NAD_1983_StatePlane_Maryland_FIPS_1900")
tupNAD83HARN_SPMD1900_feet = (2893,"NAD_1983_HARN_StatePlane_Maryland_FIPS_1900_Feet")
tupNAD83HARN_SPMD1900_meters = (2804,"NAD_1983_HARN_StatePlane_Maryland_FIPS_1900")
tupWGS84_GCS = (4326, "GCS_WGS_1984") # At time of creation noone was presently using this. Charles once did.
tupAnneArundelCustom = (0, "NAD_1983_HARN_StatePlane_Maryland_FIPS_1900") # Jeyan says AA Cnty is custom, no FactCode
lsCoordSysTuples = [tupNAD83_SPMD1900_feet, tupNAD83_SPMD1900_meters, tupNAD83HARN_SPMD1900_feet
    , tupNAD83HARN_SPMD1900_meters, tupWGS84_GCS, tupAnneArundelCustom]
dictExpectedWKID_FactoryCode = {
    "Allegany" : lsCoordSysTuples[0]
    , "AnneArundel" : lsCoordSysTuples[5]
    , "BaltimoreCity" : lsCoordSysTuples[0]
    , "BaltimoreCounty" : lsCoordSysTuples[2]
    , "Calvert": lsCoordSysTuples[0]
    , "Caroline": lsCoordSysTuples[1]
    , "Carroll": lsCoordSysTuples[2]
    , "Cecil": lsCoordSysTuples[1]
    , "Charles" : lsCoordSysTuples[1]
    , "Dorchester" : lsCoordSysTuples[0]
    , "Frederick" : lsCoordSysTuples[0]
    , "Garrett" : lsCoordSysTuples[0]
    , "Harford" : lsCoordSysTuples[0]
    , "Howard": lsCoordSysTuples[0]
    , "Kent": lsCoordSysTuples[1]
    , "Montgomery" : lsCoordSysTuples[0]
    , "PrinceGeorges" : lsCoordSysTuples[0]
    , "QueenAnnes" : lsCoordSysTuples[0]
    , "Somerset" : lsCoordSysTuples[1]
    , "StMarys": lsCoordSysTuples[0]
    , "Talbot" : lsCoordSysTuples[0]
    , "Washington" : lsCoordSysTuples[0]
    , "Wicomico" : lsCoordSysTuples[1]
    , "Worcester" : lsCoordSysTuples[1]}

    # Logging setup
strInfo = "info"
strWarning = "warning"
strError = "error"
strLogFileName = r"E:\Addressing_FMEProject\Scripts\LogFiles\ProjectionCheck.log"
tupTodayDateTime = datetime.datetime.utcnow().timetuple()
strTodayDateTimeForLogging = "{}/{}/{} UTC[{}:{}:{}]".format(tupTodayDateTime[0]
                                                          , tupTodayDateTime[1]
                                                          , tupTodayDateTime[2]
                                                          , tupTodayDateTime[3]
                                                          , tupTodayDateTime[4]
                                                          , tupTodayDateTime[5])
logging.basicConfig(filename=strLogFileName,level=logging.INFO)
strPSAForLogging_ScriptInitiated = " {} - Projection Check Initiated".format(strTodayDateTimeForLogging)

# FUNCTIONS
def printAndLog(strMessage, strLogLevel):
    strMessage = strMessage.strip("\n")
    if strLogLevel is strInfo:
        logging.info(strMessage)
    elif strLogLevel is strWarning:
        logging.warning(strMessage)
    elif strLogLevel is strError:
        logging.warning(strMessage)
    print(strMessage)
    return

# FUNCTIONALITY
printAndLog(strPSAForLogging_ScriptInitiated, strInfo)

    # Is the gdb path valid
if not path.exists(strRootGeodatabasePath):
    printAndLog("Path {} does not exist.\n".format(strRootGeodatabasePath), strError)
    exit()
else:
    # Set the workspace for ESRI tools
    env.workspace = strRootGeodatabasePath

    # Make a list of the feature classes and check the projection (spatial reference)
lsFeatureClassesInMasterGDB = sorted(ListFeatureClasses(wild_card=None,feature_type="Point",feature_dataset=None))
for fc in lsFeatureClassesInMasterGDB:
    boolExpectedFactoryCode = False

    # Get the spatial reference and attributes
    try:
        spatrefProjectionName = Describe(fc).spatialReference
        intFactoryCode = spatrefProjectionName.factoryCode
        strPCSName = spatrefProjectionName.PCSName
        if (intFactoryCode == dictExpectedWKID_FactoryCode[fc][0]) and (strPCSName == dictExpectedWKID_FactoryCode[fc][1]):
            boolExpectedFactoryCode = True
        else:
            boolExpectedFactoryCode = False
    except:
        printAndLog(strPSAGeoprocessingError.format((GetMessages(2))), strError)
    strPaddingForPrintOutput = str(20 - len(fc))
    strMessage = " {} {:>" + strPaddingForPrintOutput + "}"
    strMessage = strMessage.format(fc, str(boolExpectedFactoryCode))
    printAndLog(strMessage,strInfo)
printAndLog("Complete",strInfo)