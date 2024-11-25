import os
import sys
import constants
import credentials
import variables
from log import Log
from salesforce_api import SalesforceApi
from database import Database


# Backs up ContentDocuments, ContentDocumentLinks, and ContentVersions in local SQLite3 database
# Total Number of API callouts = 1 + numBatches * 2 + limit 
def runBackup(api, db, log, limit):
    totalDocsProcessed = 0
    while totalDocsProcessed < limit:
        if api.remainingApiRequests < variables.MIN_API_REQUESTS_REMAINING_TO_RUN:
            # stop running
            log.addError('Hit pre-defined Api Request Limit', True)
            break
        # get records from SF
        docs = api.getContentDocuments(limit=limit - totalDocsProcessed)
        if docs is None or len(docs) == 0:
            print('no more docs found')
            break
        print('got ' + str(len(docs)) + ' documents of remaining ' + str(limit - totalDocsProcessed))
        curDoc = totalDocsProcessed + 1
        totalDocsProcessed += len(docs)
        for doc in docs:
            db.save_content_document(doc)
            db.save_content_document_links(doc['ContentDocumentLinks']['records'], doc['Id'])
            for version in doc['ContentVersions']['records']:
                data = api.getContentVersionData(version['Id'])
                if data is None:
                    log.addError('ERROR: could not get version data from salesforce of versionId: ' + version['Id'], True)
                    continue
                db.save_content_version(version, data, doc['Id'])
            print(str(curDoc) + ' of ' + str(limit) + ' backed up')
            curDoc += 1
        # delete them so the next query doesn't retrieve the same documents
        success = api.deleteContentDocuments(docs)
        print('Successfully deleted records in SF' if success else 'Error deleting record(s) in SF. Check log file for details.')
    log.addInfo('Total MB downloaded: ' + str(db.mb_saved))
    log.addInfo('Total API Requests made: ' + str(api.numApiCalls))
    

def prep_backup(limit=500000):
    log = Log(folder=constants.logsPath)
    sf = SalesforceApi(credentials.username, credentials.password, credentials.security_token, log)
    limit = min(limit, sf.recordsToProcess)
    if sf.token is not None:
        db = Database(constants.dbPath, log)
        db.initialize_db()
        runBackup(sf, db, log, limit)
        db.close_connection()
        log.finishLog()
    

if __name__ == '__main__':
    args = sys.argv[1:]
    limit = 500000
    try:
        limit = int(args[0]) if len(args) > 0 else limit
    except Exception:
        print('\n  arguments: limit (optional)')
        print('  limit: max # of records to process during execution. default - 1m')
        print('  example command: python run_backup.py 7\n') 
    prep_backup(limit)
