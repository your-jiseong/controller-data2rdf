# -*- coding: utf-8 -*-

import sys, json
import urllib, urllib2

from bottle import route, run, template, request, response, post
import ipfinder

from operator import itemgetter
import langdetect

host_ip = ipfinder.get_ip_address('eth0')
port = '7401'

def service(i_json, conf):
	o_json = None

	# Service routine -------------------------------------
	log = []

	# module: datatype detection
	dtype = 'text'

	# module: language detection
	lang = langdetect.detect(i_json['input'])

	# module: ner
	try:
		if lang != 'ko':
			ner_input = i_json
			ner_input['type'] = dtype
			ner_input['lang'] = lang

			ner_output = send_postrequest(conf['address']['ner'][lang], json.dumps(ner_input))
			ner_output = json.loads(ner_output)

			log = write_log({'NER input': ner_input}, log)
			log = write_log({'NER output': ner_output}, log)
	except Exception as e:
		write_log({'NER error': {'exception message': str(e), 'NER output': ner_output}}, log)
		o_json = {'output': '', 'log': log}
		return o_json

	# module: ned
	try:
		if lang == 'ko':
			ned_input = i_json
			ned_input['type'] = dtype
			ned_input['lang'] = lang

			ned_output = send_postrequest(conf['address']['ned'][lang], json.dumps(ned_input))
			ned_output = json.loads(ned_output)
		else:
			ned_input = i_json
			ned_input['lang'] = lang

			for o in sorted(ner_output['output'], key=itemgetter('beginIndex'), reverse=True):
				ned_input['input'] = replace_by_index(ned_input['input'], '<entity>' + o['body'] + '</entity>', o['beginIndex'], o['endIndex'])
			
			ned_output = send_postrequest(conf['address']['ned'][lang], json.dumps(ned_input))
			ned_output = json.loads(ned_output)

		log = write_log({'NED input': ned_input}, log)
		log = write_log({'NED output': ned_output}, log)
	except Exception as e:
		write_log({'NED error': {'exception message': str(e), 'NED output': ned_output}}, log)
		o_json = {'output': '', 'log': log}
		return o_json

	# module: text2k
	try:
		text2k_input = {'input': i_json['input'], 'namedEntities': ned_output['output'], 'lang': lang}
		
		text2k_output = send_postrequest(conf['address']['text2k'][lang], json.dumps(text2k_input))
		text2k_output = json.loads(text2k_output)

		log = write_log({'Text2K input': text2k_input}, log)
		log = write_log({'Text2K output': text2k_output}, log)
	except Exception as e:
		write_log({'Text2K error': {'exception message': str(e), 'Text2K output': text2k_output}}, log)
		o_json = {'output': '', 'log': log}
		return o_json

	# module: rdf generation
	try:
		rdfg_input = {'input': text2k_output['output']}

		rdfg_output = json.loads(send_postrequest(conf['address']['rdfg'], json.dumps(rdfg_input)))

		log = write_log({'RDFG input': rdfg_input}, log)
		log = write_log({'RDFG output': rdfg_output}, log)
	except Exception as e:
		write_log({'RDFG error': {'exception message': str(e), 'RDFG output': rdfg_output}}, log)
		o_json = {'output': '', 'log': log}
		return o_json

	# output generation
	o_json = {'output': rdfg_output['output'], 'log': log}

	# /Service routine -------------------------------------

	return o_json

def write_log(l, log):
	log.append(l)

	return log

def replace_by_index(string, replace, start, end):
	start = int(start)
	end = int(end)

	return string[0:start] + replace + string[end:]

def enable_cors(fn):
	def _enable_cors(*args, **kwargs):
		# set CORS headers
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
		response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

		if request.method != 'OPTIONS':
			# actual request; reply with the actual response
			return fn(*args, **kwargs)
		
	return _enable_cors

def send_postrequest(url, input_string):
	opener = urllib2.build_opener()
	request = urllib2.Request(url, data=input_string, headers={'Content-Type':'application/json'})
	return opener.open(request).read()

def set_conf(new_conf):
	# default configuration
	i_file = open('conf.json', 'r')
	sInput = i_file.read()
	i_file.close()
	conf = json.loads(sInput)

	# updated configuration
	conf.update(new_conf)

	return conf

@route(path='/service', method=['OPTIONS', 'POST'])
@enable_cors
def do_request():
	if not request.content_type.startswith('application/json'):
		return 'Content-type:application/json is required.'

	# input reading
	i_text = request.body.read()
	try:
		i_text = i_text.decode('utf-8')
	except:
		pass
	i_json = json.loads(i_text)

	# configuration setting
	try:
		conf = set_conf(i_json['conf'])
	except:
		conf = set_conf({})

	# request processing
	o_json = service(i_json, conf)
	o_text = json.dumps(o_json, indent=5, separators=(',', ': '), sort_keys=True)	

	return o_text

run(server='cherrypy', host=host_ip, port=port)