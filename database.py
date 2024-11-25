import os
import sqlite3
from sqlite3 import Error as dbError
from log import Log
import constants


class Database:
     
    # creates new database connection and stores # MB of data saved
    def __init__(self, dbPath, log):
        try:
            self.dbPath = dbPath
            self.log = log
            self.connection = sqlite3.connect(dbPath)
            self.mb_saved = 0
            print("Connected to Database")
        except dbError as e:
            print(f'Error connection to database: {e}')


    # creates new tables for local database if they do not exist
    def initialize_db(self):
        cur = self.connection.cursor()
        if not self._table_exists(cur, 'ContentDocuments'):
            cur.execute('CREATE TABLE ContentDocuments(Id TEXT PRIMARY KEY, Title TEXT, LatestPublishedVersionId TEXT, FileExtension TEXT, FileType TEXT)')
        if not self._table_exists(cur, 'ContentVersions'):
            cur.execute('CREATE TABLE ContentVersions(Id TEXT PRIMARY KEY, ContentDocumentId TEXT, VersionNumber INT, ContentSize INT, Title TEXT, VersionData BLOB, FOREIGN KEY (ContentDocumentId) REFERENCES ContentDocuments (Id))')
        if not self._table_exists(cur, 'ContentDocumentLinks'):
            cur.execute('CREATE TABLE ContentDocumentLinks(Id TEXT PRIMARY KEY, LinkedEntityId TEXT, ContentDocumentId TEXT, ShareType TEXT, Visibility TEXT)')
        cur.close()
        print('tables existing at path: ' + self.dbPath)
        
     
    # checks local database to see if table already exists   
    def _table_exists(self, cur, tableName):
        cur.execute("SELECT count(' + tableName + ') FROM sqlite_master WHERE type = 'table' AND name = '" + tableName + "'")
        return cur.fetchone()[0] == 1
        
        
    # pass in a query string and a tuple of data to cmmit to the database
    def _commit_to_db(self, query, dataList):
        try:
            cursor = self.connection.cursor()
            for dataTuple in dataList:
                cursor.execute(query, dataTuple)
            self.connection.commit()
            cursor.close()
        except dbError as e:
            self.log.addError('Failed to save content document with error: ' + e + '\ndata = ' + str(dataList), True)
            
            
    # pass in a SELECT query string to retrieve records from the database
    def _get_from_db(self, query):
        rows = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        except dbError as e:
            self.log.addError('Failed to get records with error: ' + str(e.args), True)
        return rows
    

    # Inserts the ContentDocument into the database from the doc JSON
    def save_content_document(self, doc):
        query = 'INSERT OR IGNORE INTO ContentDocuments (Id, Title, LatestPublishedVersionId, FileExtension, FileType) VALUES (?, ?, ?, ?, ?)'
        data = (doc['Id'], doc['Title'], doc['LatestPublishedVersionId'], doc['FileExtension'], doc['FileType'])
        self._commit_to_db(query, [data])
    
    
    # Inserts ContentDocumentLink records into database
    def save_content_document_links(self, links, contentDocumentId):
        query = 'INSERT OR IGNORE INTO ContentDocumentLinks (Id, LinkedEntityId, ContentDocumentId, ShareType, Visibility) VALUES (?, ?, ?, ?, ?)'
        dataList = []
        for link in links:
            dataList.append( (contentDocumentId + '_' + link['LinkedEntityId'], link['LinkedEntityId'], contentDocumentId, link['ShareType'], link['Visibility']) )
        self._commit_to_db(query, dataList)
        
        
    # Inserts ContentVersion records into database (including blob data)
    def save_content_version(self, cv, versionData, contentDocumentId):
        query = 'INSERT OR IGNORE INTO ContentVersions (Id, ContentDocumentId, VersionNumber, ContentSize, Title, VersionData) VALUES (?, ?, ?, ?, ?, ?)'
        data = (cv['Id'], contentDocumentId, cv['VersionNumber'], cv['ContentSize'], cv['Title'], versionData)
        self._commit_to_db(query, [data])
        self.mb_saved += float(cv['ContentSize']) / 1000000
        
        
    # returns all ContentVersion records from the local database linked to the passed in Id
    def get_files(self, linkedEntityId):
        query = f'''
            SELECT ContentVersions.VersionNumber, 
                ContentDocuments.FileExtension,
                ContentDocuments.FileType,
                ContentVersions.Title,
                ContentDocuments.Id,
                ContentVersions.VersionData
            FROM ContentVersions
            INNER JOIN ContentDocuments ON ContentVersions.ContentDocumentId = ContentDocuments.Id
            WHERE ContentDocumentId IN (
                SELECT ContentDocumentId
                FROM ContentDocumentLinks
                WHERE LinkedEntityId = '{linkedEntityId}'
            )
        '''
        return self._get_from_db(query)
        
    
    # terminate database connection. call at end.
    def close_connection(self):
        if self.connection:
            self.connection.close()
            print('database connection closed')
        else:
            print('database connection already closed') 


if __name__ == '__main__':
    db = Database(constants.dbPath)
    db.initialize_db()
    db.close_connection()
    