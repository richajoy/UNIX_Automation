#./bkupscript.py

from mybackup import MyBackup
import logging
import zipfile

#satart the mail
if __name__ == "__main__":
#start logging
    logging.basicConfig(filename='backup.log',
                        format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
#create the backup object
    logging.info("Creating the backup object")
    bkobj = MyBackup()
#set the backup directory
    logging.info("Setting the directory to backup")
    bkobj.dir_to_backup = '/home/user/pylabs/backup'
#set the zipfile
    logging.info("Setting the zipfile")
    myzip = zipfile.ZipFile('bkup.zip', 'w')
    bkobj.backup_file = myzip
    logging.info("Backing up the directory")
    bkobj.zip_directory()
    myzip.close()
