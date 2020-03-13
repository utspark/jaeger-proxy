#!/usr/bin/env python3
from multiprocessing import Process
import socket 
import logging
from jaeger_client import Config
from opentracing.ext import tags
from opentracing.propagation import Format
#import requests
import sys
import time
import os

MAX = 4096
dst_server = "127.0.0.1"
proxy_port = int(os.environ['PROXY_PORT']) #8000
#proxy_port = 44040
dst_port = int(os.environ['DST_PORT']) #80
#dst_port = 80

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

tracer = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
        'reporter_batch_size': 1,
    },
    service_name=os.environ['SERVICE'],
).initialize_tracer()

def main():

    #in the pod everything is localhost
    host = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host,proxy_port))
        s.listen(5)
    except socket.error as message:
        if s:
            s.close()
        print(f"Could not open socket {message}")
        exit(1)

    while 1:
        #listen loop for port 8000
        #open socker on port 8000
        con,clint_addr = s.accept()
        p = Process(target=proxy_process, args=(con,clint_addr,tracer))
        p.start()
        #listen to socket and receive any connection
    s.close()

def proxy_process(connection, clint_address, tracer):
    #Should surround in try catch to get good error codes
    try:
        #recieve the data from the incoming socket
        request = connection.recv(MAX)
        print('modifying request')
        data, headers = get_http_headers(request)
        #print(data)
        #print(headers)
        span_ctx = tracer.extract(Format.HTTP_HEADERS, headers)
        op_name = ''
        span_tags = {}
        child_ctx = 0
        if span_ctx is None:
            op_name = 'get1'
            span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_CLIENT}
        else:
            op_name = 'get2'
            span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
            child_ctx = 1
        with tracer.start_active_span(op_name, child_of=span_ctx, tags=span_tags) as scope:
        #with scope = 1:
            span = tracer.active_span
            span.set_tag(tags.HTTP_METHOD, 'GET')
            modify_http(data, headers, span, tracer, child_ctx)
            #make a new socket to forward the data
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((dst_server, dst_port))
            s.send(request)

            #receive on the new port
        while 1:
            # get the data sent to the container
            data = s.recv(MAX)
            if len(data) > 0:
                #send data received back to sender
                # data = modify_http(data)
                connection.send(data)
            else:
                break
        s.close()
        connection.close()
    except socket.error as message:
        #tie up loose ends
        if s:
            s.close()
        if connection:
            connection.close()
        print(f"Runtime error {message}")
        exit(1)

def modify_http(data, headers, span, tracer, child):
    #do what you want to the packet here
    carrier = {}
    tracer.inject(span_context=span.context, format=Format.HTTP_HEADERS, carrier=carrier)
    print(carrier)
    d = data.split(b"\r\n")
    pos = 0
    #print(headers)
    headers['uber-trace-id'] = carrier.get('uber-trace-id')
    #print(headers)
    d1 = [(str(t)+': '+str(headers.get(t))).encode('utf-8') for t in headers]
    #print(d)
    #print(d1)
    d = d1 + d
    #print(d)
    #after you modify the line you need
    #put the data back together again
    data = b"\r\n".join(d)
    return data

def get_http_headers(data):
    #do what you want to the packet here
    d = data.split(b"\r\n")
    headers = {}
    pos = 0
    for i in d:
        if(i == b''):
            break
        if(b': ' not in i):
            print(i)
            continue
        i_str = i.decode('utf-8').split(": ")
        headers[i_str[0]] = i_str[1]
        pos=pos+1
    #after you modify the line you need
    #put the data back together again
    data = b"\r\n".join(d[pos:])
    return data, headers

if __name__ == "__main__":
    main()
