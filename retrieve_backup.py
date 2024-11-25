import sys
import os
import shutil
import constants
from database import Database
from log import Log


def getValidFileName(originalFileName):
        return ''.join(i for i in originalFileName if i not in "\/:*?<>|\"")

# copies ContentDocument folders related to LinkedEntityId into folder named 'out' for easy retrieval
def retrieveBackup(linkedEntityId, db):
    
    rows = db.get_files(linkedEntityId)
    if rows is None or len(rows) == 0:
        print('Nothing found for LinkedEntityId: ' + linkedEntityId)
        return
    print('Found ' + str(len(rows)) + ' files')
        
    resetOutDirectory(linkedEntityId)
    for row in rows:
        # get values from db query
        versionNum = row[0]
        title = getValidFileName(row[3])
        fileName =  title + '.' + row[1]
        contentDocumentId = row[4]
        versionData = row[5]
        
        # make folder for each content document
        docFolder = constants.outPath + title + '_' + contentDocumentId + '/'
        if not os.path.exists(docFolder):
            os.makedirs(docFolder)
        versionFolder = docFolder + 'v' + str(versionNum) + '/'
        os.makedirs(versionFolder)
        with open(versionFolder + fileName, 'wb') as f:
            f.write(versionData)
    print('Files successfully retrieved and accessible at: ' + constants.outPath)


# deletes Out directory and re-creates it
def resetOutDirectory(lId):
    p = constants.outPath
    if os.path.exists(p):
        shutil.rmtree(p)
    os.makedirs(p)
    with open(p + 'info.txt', 'w+') as f:
        f.write('This folder contains files related to LinkedEntityId: ' + lId)


if __name__ == '__main__':
    id = None
    if len(sys.argv) == 1:
        id = input('Paste the 18-character Id of the entity you wish to retrieve files for: ')
    try:
        id = sys.argv[1] if id is None else id # first arg is always class name
        assert(len(id) == 18)
    except:
        print('\n   Invalid command. This function accepts one argument: the LinkedEntityId (must be 18 characters)')
        print('   Ex: \'python retrieve_backup.py 001f400001DgpD1AAJ\'\n')
        sys.exit()
    db = Database(constants.dbPath, log=Log(folder=constants.logsPath))
    print('Retrieving files...')
    retrieveBackup(id, db)
