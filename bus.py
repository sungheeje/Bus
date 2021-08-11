from flask import Flask, request
app = Flask(__name__)

import requests
import xml.etree.ElementTree as ET

#key = "KZVJVTS6otUHW1f%2FLlV4d7vi2qrqIeRkLYP0q6tK4TO0vkGh%2FA6scK2EYD8YfDV%2B1LPk86QhLIAuvW0JdNAF4A%3D%3D"
key = "1234567890"
path = "http://openapi.gbis.go.kr/ws/rest/buslocationservice"
routeid = '234000002'

url = "%s?serviceKey=%s&routeId=%s"%(path, key, routeid)
print(url, flush=True)

stop = {}
with open("station20190902.csv", encoding='euckr') as f:
    line = f.readlines()

for x in line:
    d = x.split(',')
    stop[d[0]] = d[1]   # {stationid:name}

route = {"0":{"stationid":0,"name":""}}
with open("routestation20190902.csv", encoding='euckr') as f:
    line = f.readlines()

for x in line:
    d = x.replace('\n','').split(',')
    if d[0] == routeid:
        route[d[3]] = {"stationid":d[1],"name":d[5]}
        #if int(d[3]) < 14: print(d[3], route[d[3]])

@app.errorhandler(404)
def nopage(e):
    return  request.remote_addr, {'Content-Type': 'text/html; charset=utf8'}


@app.route("/")
def bus():
    print('got /', flush=True)
    count = request.args.get('count', '')
    if count == "": count = 1
    else: count = int(count) + 1

    line = request.args.get('line', '')
    if line == "": line = 15
    else: line = int(line)

    begin = request.args.get('begin', '')
    if begin == "": begin = 1
    else: begin = int(begin)

    r = requests.get(url)
    root = ET.fromstring(r.text)
    bus = {}
    ret = ""
    for child in root.findall('msgBody/busLocationList'):
        bus[child.find('stationSeq').text] = {"seat":child.find('remainSeatCnt').text, "stationid":child.find('stationId').text}

    if len(bus) == 0:
        ret = '<body style="font-size:110%">'
        ret += "일시적 에러입니다<p>"+r.text
        return ret, {'Content-Type': 'text/html; charset=utf8'}
    else:
        found = 0
        more = 0
        for i in range(begin,len(route)):
            no = str(i)
            mark = " "
            if no in bus:
                mark = "<b>BUS *"
                found += 1
            else: mark = "</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            if i == 13:
                ret += "<br><font color=blue>%s %d %s</font>"%(mark, i, route[no]["name"])
            elif i == 7:
                ret += "<br><font color=red>%s %d %s</font>"%(mark, i, route[no]["name"])
            else:
                ret += "<br>%s %d %s"%(mark, i, route[no]["name"])
            if more > 1 and found > 1 and i > 15: break
            if found > 1: more += 1

        with open("page.html") as f: page = f.read()
        retstr = page.replace('<%DATA%>', ret)
        retstr = retstr.replace('<%COUNT%>', str(count))
        if count < 20:
            retstr = retstr.replace('<%CONTINUE%>', 'var myVar3 = setTimeout(reload, 60000);');
            retstr = retstr.replace('<%STOP%>', '');
        else:
            retstr = retstr.replace('<%CONTINUE%>', '');
            retstr = retstr.replace('<%STOP%>', '<font color=red><b>***** STOPPED *****</b></font>');
        return retstr, {'Content-Type': 'text/html; charset=utf8'}

 if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5500)
