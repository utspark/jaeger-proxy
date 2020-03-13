#!/usr/bin/env python3
import logging
from jaeger_client import Config
from opentracing.ext import tags
from opentracing.propagation import Format
import requests
import sys
import time
from flask_bootstrap import Bootstrap
from flask import Flask, request, session, render_template, redirect, url_for
from flask import _request_ctx_stack as stack
import simplejson as json
import http.client as http_client
import os

http_client.HTTPConnection.debuglevel = 1

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

MAX = 4096
dst_server = "127.0.0.1"
proxy_port = os.environ['PROXY_PORT']
dst_port = os.environ['DST_PORT']

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
    app.run(host='::', port=proxy_port, threaded=True)

@app.route('/<path:u_path>')
def proxy_process(u_path):
    #Should surround in try catch to get good error codes
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
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
        try:
            span = tracer.active_span
            span.set_tag(tags.HTTP_METHOD, 'GET')
            headers = modify_http(request, span, child_ctx)
            url = 'http://'+dst_server+':'+dst_port+'/'+u_path+'?'+request.query_string.decode('utf-8')
            span.set_tag(tags.HTTP_URL, request.url)
            res = requests.get(url, headers=headers, timeout=3.0)
        except BaseException:
            res.status_code = 500
            res.content = {'error': 'BaseException'}

        #if res and res.status_code == 200:
            #print('success'+str(res.content))
        return res.content, res.status_code, {'Content-Type': res.headers.get('Content-Type')}
        #else:
            #status = res.status_code if res is not None and res.status_code else 500
            #return json.dumps({'error':'500'}), status, {'Content-Type': 'application/json'}

def modify_http(request, span, child):
    carrier = {}
    tracer.inject(span_context=span.context, format=Format.HTTP_HEADERS, carrier=carrier)
    print(carrier)
    headers = {}
    for header in request.headers:
        headers[header[0]]=header[1]
    #if not child:
    headers['uber-trace-id']=carrier.get('uber-trace-id')
    print(headers)
    return headers

if __name__ == "__main__":
    main()
