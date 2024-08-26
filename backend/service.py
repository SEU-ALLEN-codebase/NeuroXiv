''' Network service functions
to run, in the terminal:
>> export FLASK_APP=service.py
>> python -m flask run
'''
import io
import json
import sys
import uuid
from datetime import timedelta

import redis
from flask import Flask, jsonify, request, make_response, send_from_directory, Response, stream_with_context, session, g
from werkzeug.utils import secure_filename
from flask_caching import Cache
import hashlib
from flask_compress import Compress
import time

from dataset_db import neurons, get_summary_info
import random
import string
from features.calculate_func_new import process_file_figs
import os
from features.search_similar import Get_Similar_Range
from atlas import atlas
from LLM.AIPOM import AIPOM, predict_intent
from LLM.AIPOM_gpt4 import AIPOM_gpt4_turbo
from LLM.LLMLiteratureSearch import LiteratureSearch
from LLM.LLMChat import chatWithLLM
from LLM.LLMSearchCondition import predict_search_condition
import nbformat as nbf
from flask_cors import CORS
from LLM import data_summary_final, data_summary

neuron_class = neurons('/data')


def make_cache_key(*args, **kwargs):
    query_string = request.query_string.decode('utf-8')
    body = request.get_json(silent=True)
    key = request.path + '?' + query_string + str(body)
    cache_key = hashlib.sha256(key.encode()).hexdigest()
    return cache_key


@app.before_request
def make_session_permanent():
    session.permanent = True


def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    print(session['session_id'])
    return session['session_id']


@app.route(ROUTE_ROOT + '/')
def test():
    return 'aha\n'




@app.route(ROUTE_ROOT + '/GetIntent/<string:question>', methods=['GET', 'POST'])
def GetSearchIntent(question):
    print(question)
    response = predict_intent(question)
    print(response)
    if response:
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'ChatGPT API request failed'}), 500


@app.route(ROUTE_ROOT + '/GetSearchCondition/<string:question>', methods=['GET', 'POST'])
def Predict_Search_Condition(question):
    print(question)
    response = predict_search_condition(question)
    print(response)
    if response:
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'ChatGPT API request failed'}), 500


@app.route(ROUTE_ROOT + '/AI_RAG/<string:question>', methods=['GET', 'POST'])
def getAiAnswer(question):
    response = AIPOM(question)
    # response = AIPOM_gpt4_turbo(question)
    print(response)

    if response:
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'ChatGPT API request failed'}), 500


@app.route(ROUTE_ROOT + '/AI_Chat/<string:question>', methods=['GET', 'POST'])
def getAiAdvice(question):
    response = chatWithLLM(question)
    print(response)

    if response:
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'ChatGPT API request failed'}), 500


@app.route(ROUTE_ROOT + '/Article/<string:query>', methods=['GET', 'POST'])
def getArticle(query):
    fetch_articles = LiteratureSearch(query)
    articles = {"articles": fetch_articles}
    print(articles)
    if articles:
        return jsonify({'response': articles})
    else:
        return jsonify({'error': 'Search Articles failed'}), 500


@app.route('/api/start_stream', methods=['POST'])
def start_stream():
    global should_stop_generation
    should_stop_generation = False  # 重置停止标志

    neuronlists = request.json['id_list']

    prompts, origin_input = data_summary_final.generate_prompts(neuronlists)
    print('origin input\n\n')
    print(origin_input)

    def generate():
        print('in generate summary')
        last_heartbeat = time.time()  # 上次发送心跳包的时间
        heartbeat_interval = 30  # 心跳包的发送间隔，单位是秒

        for data_type, prompt in prompts.items():
            # 定期检查是否应该停止生成
            if should_stop_generation:
                print('Generation stopped.')
                break

            yield from data_summary_final.generate_MoE_Summary_stream(prompt, origin_input[data_type], data_type)
            time.sleep(0.1)  # 模拟延迟，以便在长时间生成时可以响应停止请求

            # 发送心跳包
            current_time = time.time()
            if current_time - last_heartbeat > heartbeat_interval:
                yield 'data: {"type": "ping", "message": "keep streaming"}\n\n'
                last_heartbeat = current_time

        yield 'data: {"type": "end", "message": "streaming finished"}\n\n'

    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
    }
    print('finish generate summary')
    return Response(stream_with_context(generate()), headers=headers)


@app.route(ROUTE_ROOT + '/all_info.json')
def hello():
    res = neuron_class.get_info_criteria()
    return jsonify(res)


@app.route(ROUTE_ROOT + '/search', methods=['GET', 'POST'])
@cache.memoize(timeout=300000000000, make_name=make_cache_key)
def search_neurons():
    t1 = time.time()
    msg = ''
    code = 0
    if request.json is None or len(request.json) == 0:
        res = neuron_class.get_info_all()
    elif 'id_list' in request.json:
        res = neuron_class.get_info_list(request.json['id_list'])
        if res is None:
            code = 1
            msg = 'found 0 neuron matches ID in request'
    elif 'criteria' in request.json:
        if len(request.json['criteria']) == 0:
            res = neuron_class.get_info_all()
        else:
            querry_dict = request.json['criteria']
            print(querry_dict)
            res = neuron_class.get_info_criteria(query_dict=request.json['criteria'])
        if res is None:
            code = 1
            msg = 'found 0 neuron meet criteria'
    else:
        res = None
        code = 1
        msg = 'cannot understand querry neuron request'
    if res is not None:
        res['neurons'] = sort_neurons_by_id(res['neurons'])
    t2 = time.time()
    print(t2 - t1)
    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route(ROUTE_ROOT + '/neurons/<string:neuron_id>', methods=['GET', 'POST'])
def get_neuron_info(neuron_id):
    global neuron_class
    code = 0
    msg = ''
    if request.json is not None and 'neuron_id' in request.json and \
            'atlas' in request.json:
        # neuron_id = request.json['neuron_id']
        atlas = request.json['atlas']
        res = neuron_class.get_neuron_info(neuron_id, atlas)
        if res is None:
            code = 1
            msg = 'please enter the neuron ID' if neuron_id == 'null' else 'neuron ID %s and atlas %s cannot find' % (
                neuron_id, atlas)
    else:
        msg = 'Missing parameters'
        code = 2
        res = None
    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    code = 0
    msg = ''

    f = request.files['file']
    fname = secure_filename(f.filename)
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 9))
    savename = "_".join([fname, ran_str])
    save_path = "D:/NeuroXiv/dataset/temp/{}".format(savename)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    swc_path = os.path.join(save_path, fname)
    f.save(swc_path)

    res = process_file_figs(swc_path)

    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route("/search_similar_neurons", methods=['GET', 'POST'])
def search_similar_neurons():
    code = 0
    msg = ''

    if request.json is None or len(request.json) == 0:
        code = 2
        msg = 'Missing parameters'
        res = None
    else:
        res = Get_Similar_Range(request.json)
    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route(ROUTE_ROOT + '/search_roi/<string:roi_parameter>', methods=['GET', 'POST'])
def search_roi_neurons(roi_parameter):
    code = 0
    msg = ''
    if request.json is not None and 'roi_parameter' in request.json and \
            'atlas' in request.json:
        roi_parameter = request.json['roi_parameter']
        atlas = request.json['atlas']
        res = neuron_class.search_roi_neurons(roi_parameter, atlas)
        if res is None:
            code = 1
            msg = 'found 0 neuron in the ROI'
    else:
        msg = 'Missing parameters'
        code = 2
        res = None
    # res = neuron_class.search_roi_neurons(roi_parameter)
    # if res is None:
    #     code = 1
    #     msg = 'found 0 neuron in the ROI'
    if res is not None:
        res['neurons'] = sort_neurons_by_id(res['neurons'])
    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route(ROUTE_ROOT + '/species_all', methods=['GET'])
def get_all_species():
    code = 0
    msg = ''
    res = atlas.get_all_species()
    if res is None:
        code = 1
        msg = 'found zero species in the database'
    return jsonify({
        'code': code,
        'msg': msg,
        'data': res
    })


@app.route(ROUTE_ROOT + '/species/<string:id>', methods=['GET'])
def get_species_info(id):
    code = 0
    msg = ''
    res = atlas.get_species_info(int(id))
    if res is None:
        code = 1
        msg = 'there is no species id named {}'.format(id)
    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route(ROUTE_ROOT + '/species_image', methods=['GET', 'POST'])
def get_image():
    msg = ''
    code = 0
    if request.json is not None and 'id' in request.json and \
            'type' in request.json and 'zslice' in request.json:
        species_id = request.json['id']
        image_type = request.json['type']
        zslice = request.json['zslice']
        res = atlas.get_image(species_id, image_type, zslice)
        if res is None:
            msg = 'there is no species id named {} or no image type named {}'.format(species_id, image_type)
            code = 1
    else:
        msg = 'Missing parameters'
        code = 2
        res = None
    print(res)
    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route(ROUTE_ROOT + '/thumbnail_list', methods=['GET', 'POST'])
def get_thumbnail_list():
    msg = ''
    code = 0
    if request.json is not None and 'id' in request.json and \
            'type' in request.json:
        species_id = request.json['id']
        image_type = request.json['type']
        res = atlas.get_thumbnail_list(species_id, image_type)
        if res is None:
            msg = 'there is no species id named {} or no image type named {}'.format(species_id, image_type)
            code = 1
    else:
        msg = 'Missing parameters'
        code = 2
        res = None

    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route(ROUTE_ROOT + '/structural_ontology/<string:id>', methods=['GET'])
def get_structural_ontology(id):
    code = 0
    msg = ''
    res = atlas.get_structural_ontology(int(id))
    if res is None:
        code = 1
        msg = 'there is no structural ontology named {}'.format(id)
    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})

@app.route(ROUTE_ROOT + '/species_atlas', methods=['GET', 'POST'])
def get_species_atlas():
    msg = ''
    code = 0
    if request.json is not None and 'ontology_id' in request.json and \
            'zslice' in request.json:
        ontology_id = request.json['ontology_id']
        zslice = request.json['zslice']
        res = atlas.get_species_atlas(ontology_id, zslice)
        if res is None:
            msg = 'there is no species atlas id named {} or no {} zslice'.format(ontology_id, zslice)
            code = 1
    else:
        msg = 'Missing parameters'
        code = 2
        res = None

    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


@app.route(ROUTE_ROOT + '/atlas_brain_region', methods=['GET', 'POST'])
def get_brain_region_info():
    msg = ''
    code = 0
    if request.json is not None and 'ontology_id' in request.json and \
            'brain_region_id' in request.json:
        ontology_id = request.json['ontology_id']
        brain_region_id = request.json['brain_region_id']
        res = atlas.get_brain_region_info(ontology_id, brain_region_id)
        if res is None:
            msg = 'there is no species atlas id named {} or no brain region id named {}'.format(ontology_id,
                                                                                                brain_region_id)
            code = 1
    else:
        msg = 'Missing parameters'
        code = 2
        res = None

    return jsonify({'code': code,
                    'msg': msg,
                    'data': res})


def sort_neurons_by_id(neuron_data):
    def neuron_id_sort_key(neuron):
        neuron_id = neuron.get('id', '')
        if neuron_id.startswith('SEU'):
            return 0
        elif neuron_id.startswith('MouseLight'):
            return 1
        elif neuron_id.startswith('ION'):
            return 2
        elif neuron_id.contains('local'):
            return 3
        else:
            return 4

    return sorted(neuron_data, key=neuron_id_sort_key)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
