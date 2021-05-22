from django.http import HttpResponse, response
import datetime
from django.shortcuts import get_object_or_404, render
import redis
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
import json
import time

redis_instance = redis.StrictRedis(host="127.0.0.1",
                                  port="6379", db=0)

def current_datetime():
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return now

def getTopFifty():
    result=[]
    all_scrips = redis_instance.keys("*")
    scrip_keys = [name.decode('utf-8') for name in all_scrips]
    for scrip_name in all_scrips[:50]:
        stored_data = redis_instance.lrange(scrip_name,0,redis_instance.llen(scrip_name))
        data = json.loads(stored_data[0])
        data['name'] = scrip_name.decode("utf-8")
        result.append(data)
    return result

def getTopEight():
    result=[]
    all_scrips = redis_instance.keys("*")
    scrip_keys = [name.decode('utf-8') for name in all_scrips]
    for scrip_name in all_scrips[:8]:
        stored_data = redis_instance.lrange(scrip_name,0,redis_instance.llen(scrip_name))
        data = json.loads(stored_data[0])
        data['name'] = scrip_name.decode("utf-8")
        result.append(data)
    return result

@api_view(["GET"])
def getTopEightApi(request):
    try:
        result=[]
        all_scrips = redis_instance.keys("*")
        scrip_keys = [name.decode('utf-8') for name in all_scrips]
        for scrip_name in all_scrips[:8]:
            stored_data = redis_instance.lrange(scrip_name,0,redis_instance.llen(scrip_name))
            data = json.loads(stored_data[0])
            data['name'] = scrip_name.decode("utf-8")
            result.append(data)  
        return Response({"status":1,"data":result})
    except:
        return Response({"status":0,"data":[]})

@api_view(["GET"])
def getSingleStock(request,scrip_name):
    result = {}
    stored_data = redis_instance.lrange(scrip_name,0,redis_instance.llen(scrip_name))
    if not len(stored_data):
        return Response({
                         "status":"0", # O status indictes error
                         "message":"Scrip Name Does Not Exist"
        })
    result[scrip_name] = []
    for data in stored_data:
        result[scrip_name].append(json.loads(data))
    response = {
            "status": 1,
            "result":result
    }
    return Response(response)


def index(request):
    try:
        now = datetime.datetime.now()
        result = getTopFifty()
        topEight = getTopEight()
        return render(request, 'index.html',{'datetime':now,'result':result,'topEight':topEight})
    except:
        return HttpResponse("404 Page Not Found!")