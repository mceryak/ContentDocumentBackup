from datetime import datetime
import constants
import os


class Log:
    
    
    def __init__(self, folder, file_name=str(datetime.utcnow()).replace(':', '')+'.txt'):
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.file_path = folder + file_name
        self.num_errors = 0
    
    
    def addInfo(self, info, doPrint=False):
        self._appendToLog(info, 'INFO', doPrint)
        

    def addError(self, err, doPrint=False):
        self._appendToLog(err, 'ERROR', doPrint)
        self.num_errors += 1
    
    
    def _appendToLog(self, text, category, doPrint=False):
        if doPrint:
            print(text)
        with open(self.file_path, 'a') as f:
            f.write('\n' + str(datetime.utcnow()).replace(':', '') + '|' + category + '|' + text)
        
    
    def finishLog(self):
        self._appendToLog('Execution was successful' if self.num_errors == 0 else 'Num Errors during execution: ' + self.num_errors, 'END')
        