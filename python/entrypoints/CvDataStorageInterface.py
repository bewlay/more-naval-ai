# CvDataStorageInterface

from CvPythonExtensions import *
import CvUtil
import _winreg
import traceback
import os
import copy
import types
import cPickle as pickle

gc = CyGlobalContext()

class dataStorage:

	def __init__(self):
                self.ffhFolderName = "Fall from Heaven 2"

                # data Structure : each component data must be a dict and have a key "description"
                self.data = {}

                # Trophy data structure and defaults
                defaultConfig = {
                        "description" : "register current user trophy file" ,
                        "user_file" : "Trophy.cfg"
                        }
                defaultData = {
                        "description" : "store trophies value"
                        }

                dictTrophy = {
                        "folder" : "Trophy" ,
                        "config" : "_config.cfg" ,
                        "file" : "Trophy.cfg" ,
                        "default_config" : copy.deepcopy(defaultConfig) ,
                        "default_data" : copy.deepcopy(defaultData)
                        }
                self.data["Trophy"] = copy.deepcopy(dictTrophy)

                # init globals
                for sKey in self.data.keys() :
                        self.data[sKey]["folder_path"] = ""
                        self.data[sKey]["config_path"] = ""
                        self.data[sKey]["file_path"] = ""
                        self.data[sKey]["file_data"] = copy.deepcopy(self.data[sKey]["default_data"])

                self.folderPath = self.get_FfH_FolderPath()
                if not self.folderPath : return

                # init data folders, files and values
                for sKey in self.data.keys() :
                        folder = os.path.join(self.folderPath, self.data[sKey]["folder"])
                        if not self.createFolder(folder) : continue
                        self.data[sKey]["folder_path"] = copy.copy(folder)

                        config = os.path.join(folder, self.data[sKey]["config"])
                        bValid = False
                        if os.path.isfile(config) :
                                dictData = self.readFile(config)
                                if dictData :
                                        if dictData.has_key("user_file") :
                                                userFile = dictData["user_file"]
                                                filePath = os.path.join(folder, userFile)
                                                if os.path.isfile(filePath) :
                                                        dictFile = self.readFile(filePath)
                                                        if dictFile :
                                                                self.data[sKey]["config_path"] = copy.copy(config)
                                                                self.data[sKey]["config_data"] = copy.deepcopy(dictData)
                                                                self.data[sKey]["file"] = copy.copy(userFile)
                                                                self.data[sKey]["file_path"] = copy.copy(filePath)
                                                                self.data[sKey]["file_data"] = copy.deepcopy(dictFile)
                                                                bValid = True
                        if not bValid :
                                if self.writeFile(config, self.data[sKey]["default_config"]) :
                                        self.data[sKey]["config_path"] = copy.copy(config)
                                        self.data[sKey]["config_data"] = copy.deepcopy(self.data[sKey]["default_config"])

                                        userFile = self.data[sKey]["config_data"]["user_file"]
                                        filePath = os.path.join(folder, userFile)

                                        bDefaultFileValid = False
                                        if os.path.isfile(filePath) :
                                                dictFile = self.readFile(filePath)
                                                if dictFile :
                                                        self.data[sKey]["file"] = copy.copy(userFile)
                                                        self.data[sKey]["file_path"] = copy.copy(filePath)
                                                        self.data[sKey]["file_data"] = copy.deepcopy(dictFile)
                                                        bDefaultFileValid = True

                                        if not bDefaultFileValid :
                                                if self.writeFile(filePath, self.data[sKey]["default_data"]) :
                                                        self.data[sKey]["file"] = copy.deepcopy(userFile)
                                                        self.data[sKey]["file_path"] = copy.copy(filePath)

        # Files management
        def readFile(self, path):
                try :
                        Sfile = open(path, "r")
                        loadDict = pickle.load(Sfile)
                        Sfile.close()

                        if type(loadDict) is types.DictType :
                                if loadDict.has_key("description") :
                                        return loadDict
                except :
                        print " FfH2 -> can t read file " + repr(path)
                        print traceback.format_exc()
                return {}

        def writeFile(self, path, dictData):
                try:
                        Sfile = open(path, "w")
                        pickle.dump(dictData, Sfile)
                        Sfile.close()
                        return True
                except :
                        print " FfH2 -> can t write file " + repr(path)
                        print traceback.format_exc()
                        return False

        def get_FfH_FolderPath(self):
                folder = self.getDocFolder()
                if not folder :
                        return ""
                if not os.path.isdir(folder) :
                        if not self.createFolder(folder) :
                                return ""
                return folder

        def createFolder(self, path):
                try :
                        if os.path.isdir(path) : return True

                        os.mkdir(path)
                        return True
                except :
                        print " FfH2 -> can t create folder " + repr(path)
                        print traceback.format_exc()
                        return False

        def getDocFolder(self):
                try:
                        userFolder = self.regRead(_winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders", "Personal")
                        if not userFolder : return ""
                        finalFolder =  os.path.join(userFolder, "My Games", self.ffhFolderName)
                        return finalFolder
                except:
                        print " FfH2 -> can t join FfH doc Folders :"
                        print traceback.format_exc()
                        return ""

        def regRead(self, registry, path, field):
                pathKey = _winreg.OpenKey(registry, path)
                docPath = ""
                try:
                        docPath = _winreg.QueryValueEx(pathKey, field)[0]
                except:
                        print " FfH2 -> can t get doc path :"
                        print traceback.format_exc()
                pathKey.Close()
                return docPath

        # Data management
        def getValue(self, lTags):
                try :
                        if len(lTags) <= 1 : return False, -1

                        sDataType = lTags[0]
                        if not self.data.has_key(sDataType) : return False, -1
                        if not self.data[sDataType].has_key("file_data") : return False, -1

                        d = self.data[sDataType]["file_data"]
                        for sTag in lTags[1:] :
                                if not d.has_key(sTag) : return False, -1
                                d = d[sTag]

                        return True, copy.deepcopy(d)
                except:
                        print " FfH2 -> can t get value : " + repr(lTags)
                        print traceback.format_exc()
                        return False, -1

        def setValue(self, lTags, value):
                try :
                        if len(lTags) <= 1 : return

                        sDataType = lTags[0]
                        if not self.data.has_key(sDataType) : return
                        if not self.data[sDataType].has_key("file_data") : return

                        d = self.data[sDataType]["file_data"]
                        for sTag in lTags[1: -1] :
                                if not d.has_key(sTag) : return
                                d = d[sTag]

                        d[lTags[-1]] = copy.deepcopy(value)

                        if self.data[sDataType]["file_path"] :
                                self.writeFile(self.data[sDataType]["file_path"], self.data[sDataType]["file_data"])
                except:
                        print " FfH2 -> can t set value : " + repr(lTags)
                        print traceback.format_exc()

# all use in another python module for data storage must call this variable. ie :
##import CvDataStorageInterface
##ds = CvDataStorageInterface.ds
# or create a function in this module to call.
ds = dataStorage()

# called from dll
def getTrophyValue(argsList):
        szName = argsList[0]
        bRead, val = ds.getValue(["Trophy", szName])
        if not bRead : return 0
        return val

# called from dll
def setTrophyValue(argsList):
        szName, iValue = argsList
        ds.setValue(["Trophy", szName], iValue)


