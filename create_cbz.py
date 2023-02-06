# -*- coding: utf-8 -*-

import os
import shutil
import sys
import zipfile

def zipdir(dirPath=None, zipFilePath=None, zipFileExtension='zip', includeDirInZip=True):
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


def main() -> None:
    '''Main create CBZ function'''

    if len(sys.argv) < 1:
        print("Please specify the path where the folders to cbz are located")
        sys.exit()

    parent_dir = sys.argv[1]

    for sub_dir in get_immediate_subdirectories(parent_dir):
        sub_full_path = os.path.join(os.path.abspath(parent_dir), sub_dir)
        sub_dir_entries = os.listdir(sub_full_path)
        invalid_entries = False
        for curr_sub_entry in sub_dir_entries:
            entry_path = os.path.join(sub_full_path, curr_sub_entry)
            if os.path.isdir(entry_path):
                print("Found sub directory")
                invalid_entries = True
                break

            _, f_ext = curr_sub_entry.rsplit('.',maxsplit=1)
            f_ext = f_ext.lower()
            if f_ext not in ['jpg','jpeg','png','txt']:
                print(f"Found unwanted file type: {curr_sub_entry}")
                invalid_entries = True
                break

        if invalid_entries:
            print(f"Skipping dir: {sub_dir}")
            continue

        print(f"Dir: '{sub_dir}'", end=' ')
        zipdir(sub_dir, zipFileExtension = 'cbz')
        shutil.rmtree(sub_full_path)
        print("Done")

if __name__ == '__main__':
    main()
