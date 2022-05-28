# -*- coding: utf-8 -*-

import os
import shutil
import sys
import zipfile

def zipdir(dirPath=None, zipFilePath=None, zipFileExtension = 'zip', includeDirInZip=True):
    '''

    Examples:
    zipdir("foo") #Just give it a dir and get a .zip file
    zipdir("foo", "foo2.zip") #Get a .zip file with a specific file name
    zipdir("foo", "foo3nodir.zip", False) #Omit the top level directory
    zipdir("../test1/foo", "foo4nopardirs.zip")
    '''
    if not zipFilePath:
        zipFilePath = dirPath + "." + zipFileExtension
    if not os.path.isdir(dirPath):
        raise OSError("dirPath argument must point to a directory. "
                      u"'{0}' does not.".format(dirPath))
    parentDir, dirToZip = os.path.split(dirPath)
    #Little nested function to prepare the proper archive path
    def trimPath(path):
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not includeDirInZip:
            archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)

    outFile = zipfile.ZipFile(zipFilePath, "w",
        compression=zipfile.ZIP_DEFLATED)
    for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
        for fileName in fileNames:
            if fileName in ['Thumbs.db']:
                continue
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trimPath(filePath))
        #Make sure we get empty directories as well
        if not fileNames and not dirNames:
            zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
            #some web sites suggest doing
            #zipInfo.external_attr = 16
            #or
            #zipInfo.external_attr = 48
            #Here to allow for inserting an empty directory.  Still TBD/TODO.
            outFile.writestr(zipInfo, "")
    outFile.close()

def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print("Please specify the path where the folders to cbz are located")
        sys.exit()
        
    for currDir in get_immediate_subdirectories(sys.argv[1]):
        print(u"Dir: '{0}'".format(currDir), end=' ')
        zipdir(currDir, zipFileExtension='cbz')
        shutil.rmtree(os.path.join(os.path.abspath(sys.argv[1]), currDir))
        print("Done")

