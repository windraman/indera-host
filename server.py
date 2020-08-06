import http.server
import socketserver
import cgi
import json
import sqlite3
from urllib.parse import urlparse, unquote_plus
import time
import requests
import re
import db_handler
import os
app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

PORT = 8080
url = "http://wahyu.top/public/api/sensor_value"

def wpids(f,s):
    file = open(app_path+ "pids/" + f,"w")

    file.write(str(s))
     
    file.close()

class GetHandler(http.server.CGIHTTPRequestHandler):
    def getQuery(self):
        query = urlparse(unquote_plus(self.path)).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        #for qcs in query_components:            
            #print(quote_plus(qcs))
        return query_components
    
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header(
            'Last-Modified',
            self.date_time_string(time.time())
        )
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/readme":
            self.params = self.getQuery()
            if self.params['content'] == "raspindera":
                self.response = db_handler.readme(True)
                self.response['api_status'] = 1
                self.response['ip_address'] = db_handler.getWlan()
                
                self._set_headers()
                self.wfile.write(json.dumps(self.response).encode('utf-8'))
            
        if path == "/get_modul":
            self.params = self.getQuery()
            self.response = db_handler.get_modul(self.params['slug'],True)
            self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
        
        if path == "/get_grups":
            self.params = self.getQuery()
            self.response = db_handler.get_modul(self.params['slug'],True)
            self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/get_sensors":
            self.params = self.getQuery()
            self.response = db_handler.get_sensors(self.params['slug'],self.params['get_grup'],True)
            self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/get_sensor_value":
            self.params = self.getQuery()
            self.response = db_handler.get_sensor_value(self.params['slug'],self.params['batas'],True)
            self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
        
        if path == "/send_sensor_value":
            self.params = self.getQuery()
            self.response = db_handler.send_sensor_value(self.params['slug'],self.params['nilai'],self.params['ovrd'],self.params['is_read'])
            self._set_headers()
            resp =json.dumps(self.response)
            print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/update_sensor":
            self.params = self.getQuery()
            self.response = db_handler.update_sensor(self.params['slug'],self.params['name'],self.params['pin'],self.params['pin2'],self.params['tipe_sensor_id'],self.params['parentslug'])
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/update_grup":
            self.params = self.getQuery()
            self.response = db_handler.update_grup(self.params['slug'],self.params['name'],self.params['parentslug'])
            self._set_headers()
            resp =json.dumps(self.response)
            print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/update_modul":
            self.params = self.getQuery()
            self.response = db_handler.update_modul(self.params['slug'],self.params['name'],self.params['lokasi'],self.params['latitude'],self.params['longitude'])
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/set_service":
            self.params = self.getQuery()
            self.response = db_handler.set_service(self.params['slug'],self.params['status_service'])
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/get_logic":
            self.params = self.getQuery()
            self.response = db_handler.get_logic(self.params['slug'],self.params['logicslug'],True)
            self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/rem_logic":
            self.params = self.getQuery()
            self.response = db_handler.rem_logic(self.params['slug'])
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/sync_modul":
            self.params = self.getQuery()
            self.response = db_handler.sync_modul(self.params['slug'],True)
            self._set_headers()
            resp =json.dumps(self.response)
            #resp=self.response
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/new_grup":
            self.params = self.getQuery()
            self.response = db_handler.new_grup(self.params['slug'],self.params['name'])
            self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)            
            self.wfile.write(resp.encode('utf-8'))
        
        if path == "/rem_grup":
            self.params = self.getQuery()
            self.response = db_handler.rem_grup(self.params['slug'])
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
        
        if path == "/new_sensor":
            self.params = self.getQuery()
            self.response = db_handler.new_sensor(self.params['slug'],self.params['name'],self.params['pin'],self.params['pin2'],self.params['tipe_sensor_id'])
            self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/rem_sensor":
            self.params = self.getQuery()
            self.response = db_handler.rem_sensor(self.params['slug'])
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/empty_logic":
            self.response = db_handler.empty_logic()
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        
        
    def do_POST(self):
        path = urlparse(self.path).path
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        #print (str(self.rfile.read(length)))
        message = json.loads(self.rfile.read(length))
        
        # add a property to the object, just to mess with data
        #message['received'] = message["cmd"]
        #slug = message['slug']
        if path == "/edit_sensor":
            self.response = db_handler.set_noc(message['id'],message['noc'])
            self.response['edited_id'] = message['id']
            #self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
        
        if path == "/update_logic":
            print("jika=" + unquote_plus(message['jika']).replace('"', "'") + ",maka=" + unquote_plus(message['maka']).replace('"', "'"))
            self.response = db_handler.update_logic(message['id'],message['name'],unquote_plus(message['jika']).replace('"', "'"),unquote_plus(message['maka']).replace('"', "'"))
            self.response['edited_id'] = message['id']
            #self.response['api_status'] = 1
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
            
        if path == "/add_logic":
            print("jika=" + unquote_plus(message['jika']).replace('"', "'") + ",maka=" + unquote_plus(message['maka']).replace('"', "'"))
            self.response = db_handler.add_logic(message['name'],unquote_plus(message['jika']).replace('"', "'"),unquote_plus(message['maka']).replace('"', "'"))
            self._set_headers()
            resp =json.dumps(self.response)
            #print(resp)
            self.wfile.write(resp.encode('utf-8'))
    
    


Handler =  GetHandler

if __name__ == "__main__":
    pid = os.getpid()
    wpids("server.pid",pid)
    
    Handler.cgi_directories = ['/cgi-bin', '/htbin']
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
        
    
