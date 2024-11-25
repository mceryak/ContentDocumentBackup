import requests
import credentials
import constants
import variables
from log import Log

class SalesforceApi:

    # authenticates with Salesforce and saves token in instance var
    def __init__(self, username, password, security_token, log):
        self.log = log
        json = {'username': username, 'password': password + security_token,
                'grant_type': 'password',
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret}
        response = requests.post(constants.postToken, json)
        json = response.json()
        print(json)
        try:
            self.unableToDeleteIds = ''        
            self.token = json['access_token']
            self.numApiCalls = 3
            self.remainingApiRequests = int(requests.get(constants.orgStartUrl + 'limits', headers={'Authorization': 'Bearer ' + self.token}).json()['DailyApiRequests']['Remaining'])
            self.recordsToProcess = self._getNumRecordsToProcess()
            print('Salesforce authentication successful')
        except:
            print('authentication error')
            print(json)
            self.log.addError(json['error'] + '\n' + json['error_description'], True)

    # calls salesforce api once authenticated
    def _call(self, endpoint, method='get'):
        response = None
        self.numApiCalls += 1
        self.remainingApiRequests -= 1
        if method == 'get':
            response = requests.get(endpoint, headers={'Authorization': 'Bearer ' + self.token})
        elif method == 'delete':
            response = requests.delete(endpoint, headers={'Authorization': 'Bearer ' + self.token})
        return response
    
    
    def _getNumRecordsToProcess(self):
        query = 'SELECT Count() FROM ContentVersion WHERE Backup__c = TRUE'
        endpoint = constants.orgStartUrl + 'query/?q=' + self._fixQueryForApiCall(query)
        response = self._call(endpoint)
        return int(response.json()['totalSize'])


    # retrieves ContentDocument records from salesforce. beforeDate format: yyyy-mm-dd
    def getContentDocuments(self, limit=1000000):
        # disregard records that are tied to a service report ... they cannot be deleted
        # disregard records that have a contentAssetId ... can't delete this file because it's an asset file being referenced by one or more objects
        # disregard records with unknown file type ... it's possible that these cannot be opened 
        query = '''
            SELECT Id,FileExtension,FileType,Title,LatestPublishedVersionId,CreatedDate, 
                (SELECT Id,VersionNumber,ContentSize,Title FROM ContentVersions), 
                (SELECT LinkedEntityId, ShareType, Visibility FROM ContentDocumentLinks) 
            FROM ContentDocument 
            WHERE LatestPublishedVersion.Backup__c = TRUE'''
        query += (' AND Id NOT IN (' + self.unableToDeleteIds + ')' if len(self.unableToDeleteIds) > 0 else '')
        query += ' LIMIT ' + (str(variables.MAX_BATCH_SIZE) if limit > variables.MAX_BATCH_SIZE else str(limit)) 
        print(query)
                
        endpoint = constants.orgStartUrl + 'query/?q=' + self._fixQueryForApiCall(query)
        response = self._call(endpoint)
        try:
            return response.json()['records']
        except:
            self.log.addError(str(response.json()), True)
            return None
        
    def _fixQueryForApiCall(self, q):
        return q.replace('%', '%25').replace('+', '%2B').replace(' ', '+')

    def getContentVersionData(self, contentVersionId):
        endpoint = constants.orgStartUrl + 'sobjects/ContentVersion/' + contentVersionId + '/VersionData'
        response = self._call(endpoint)
        if response.status_code == 200:
            return response.content
        self.log.addError('Error with ContentVersion id = ' + contentVersionId + ': ' + response.reason)
        return None

    def deleteContentDocuments(self, docs):
        ids = ''
        idArr = []
        for doc in docs:
            ids += doc['Id'] + ','
            idArr.append(doc['Id'])
        response = self._call(constants.orgStartUrl + 'composite/sobjects?ids=' + ids[0:-1], 'delete').json()
        isSuccess = True
        i = 0
        for r in response:
            if not r['success']:
               isSuccess = False
               self.log.addError(idArr[i] + ': ' + str(r['errors']), True)
               self.unableToDeleteIds = self.unableToDeleteIds + ("," if len(self.unableToDeleteIds) > 0 else '') + "'" + idArr[i] + "'"
            i += 1
        print('unable to delete ids = ' + self.unableToDeleteIds)
        return isSuccess
    
    
if __name__ == '__main__':
    sf = SalesforceApi(credentials.username, credentials.password, credentials.security_token, Log(constants.logsPath))
    sf.getNumRecordsToProcess()
