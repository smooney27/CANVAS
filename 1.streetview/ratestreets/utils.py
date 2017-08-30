import csv
import codecs

class Utils:
    @staticmethod
    def get_csv_upload_file_reader(uploaded_file):
#        dialect = csv.Sniffer().sniff(codecs.EncodedFile(uploaded_file,"utf-8").read(1024))
        uploaded_file.open() # seek to 0
        return csv.reader(codecs.EncodedFile(uploaded_file,"utf-8"), dialect='excel')
