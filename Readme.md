## ContentDocumentBackup
2 scripts:

### run_backup.py
1. in terminal, navigate inside repository folder
2. command format: `python run_backup.py [date: yyyy-mm-dd] [limit: integer]`
    - date (required): ContentDocument records are queried from before this date.
    - limit (optional): max number of ContentDocument records to process. defaults to 30k.
3. example command: `python run_backup.py 2020-01-01 30`
4. track status in terminal, and view log file generated once script is complete

### retrieve_backup.py
1. in terminal, navigate inside repository folder
2. command format: `python retrieve_backup [LinkedEntityId]`
    - LinkedEntityId (required): Id of either Acc, Opp, User, ... etc you wish to retrieve files for from the backup
3. example command: `python retrieve_backup.py 02sf400000Fj9g8AAB`
4. track status in terminal, and view log file generated once script is complete# ContentDocumentBackup
