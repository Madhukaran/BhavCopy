from django.core.management import BaseCommand, CommandError
import requests
from zipfile import ZipFile
from io import BytesIO
from io import TextIOWrapper
import csv
from django.conf import settings
import redis
import datetime
import json
import time


redis_instance = redis.StrictRedis(host="127.0.0.1",
                                  port="6379", db=0)
class Command(BaseCommand):

    help = "load BhavCopy For Every 24 hours!"

    def handle(self, *args, **options):
        try:
            date = datetime.datetime.now().strftime('%d%m%y')
            # Added Custom Header For Non-Blocking Request.
            headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"}
            dowloadable_link = f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date}_CSV.ZIP"
            zipfile_raw = requests.get(dowloadable_link, headers = headers)
            print("file downloaded")
            zip_file = ZipFile(BytesIO(zipfile_raw.content))

            with zip_file.open(zip_file.namelist()[0], 'r') as infile:
                reader = csv.reader(TextIOWrapper(infile, 'utf-8'))
                for data_row in reader:
                    redis_key = data_row[1].strip()
                    value_string = f'{{"date":"{datetime.datetime.date(datetime.datetime.now())}","code":"{data_row[0]}","open":"{data_row[4]}","high":"{data_row[5]}","low":"{data_row[6]}","close":"{data_row[7]}"}}'
                    redis_instance.lpush(redis_key,value_string)
            print("BhavCopy Loaded Successfully")
        except Exception as e:
            print("File Not Found!!!")


