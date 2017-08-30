import csv
import codecs
import logging
import datetime

class Utils:
    @staticmethod
    def get_csv_upload_file_reader(uploaded_file):
#        dialect = csv.Sniffer().sniff(codecs.EncodedFile(uploaded_file,"utf-8").read(1024))
        uploaded_file.open() # seek to 0
        return csv.DictReader(codecs.EncodedFile(uploaded_file,"utf-8"), dialect='excel')    
    @staticmethod
    def get_start_of_utc_day():
        logging.debug("get_start_of_utc_day called")
        now = datetime.datetime.utcnow()
        today = datetime.datetime(now.year, now.month, now.day)
        return today
