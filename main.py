import logging
import requests
import json

from flask import Flask, render_template, abort, request

myapp = Flask(__name__)

def setup_logging():
    #
    # setup global logger
    #
    glogger = logging.getLogger("fan_logger")
    glogger.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    glogger.addHandler(c_handler)

setup_logging()
logger = logging.getLogger("fan_logger")
    
def call_api(kind, path):
    if kind == 'tree':
        host = 'http://192.168.7.30:5008'
    if kind == 'map':
        host = 'http://192.168.7.30:5006'

    logger.debug('=> {0}{1}'.format(host, path))

    try:
        req_api = requests.get(host + path)
    except Exception as e:
        abort(500, description=e)

    logger.debug('<= {0}'.format(req_api.text)[:80])

    return req_api.text

def get_neighbours(guid, distance=6, quality="0.8"):
    ret = call_api('tree', '/neighbours2/{0}?distance={1}&quality={2}&reference=R00000039'.format(guid, distance, quality))
    return ret

@myapp.route('/')
def home():
    return render_template('home.template')

@myapp.route('/sample')
def sample():
    return render_template('sample.template')

@myapp.route('/sample/map/')
def sample_map():
    sample_name = request.args.get("sample_name")

    req_lookup = requests.get('http://192.168.7.30:5008/lookup/{0}'.format(sample_name))
    names_guids = json.loads(req_lookup.text)

    my_guid = names_guids[0][0]
    sample_name = names_guids[0][1]
    other_guids = list()
    for guid,_ in names_guids[1:]:
        other_guids.append(guid)


    req_coord = requests.get('http://192.168.7.30:5006/coordinates2/{0}'.format(sample_name))
    data = json.loads(req_coord.text)[0]

    sample_name = data[0]
    map_x = data[2]
    map_y = data[3]
    herd_id = data[4]
    eartag = data[7]

    req_movement = requests.get('http://192.168.7.30:5006/api/locations/{0}'.format(sample_name))
    movement_data = json.loads(req_movement.text)['data'][sample_name]

    return render_template('map.template', 
                           sample_name = sample_name,
                           sample_guid = my_guid,
                           eartag = eartag,
                           map_x = map_x,
                           map_y = map_y,
                           herd_id = herd_id,
                           other_guids = other_guids,
                           movement_data = movement_data
    )

@myapp.route('/sample/neighbour/')
def sample_neighbour():
    my_guid = request.args.get("sample_guid")
    my_distance = request.args.get('distance')
    my_quality = request.args.get('quality')
    if my_distance and my_quality:
        # [neighbour, distance]
        neighbours = get_neighbours(my_guid, my_distance, my_quality)

        # get sample names
        neighbour_guids = [x[0] for x in neighbours]
        neighbour_guids = ",".join(neighbour_guids)
        call_api('tree', '/lookup/{0}'.format(neighbour_guids))


    else:
        neighbours = list()

    

    # do coordinate lookup on names


    data = call_api('map', '/coordinates2/{0}'.format(coordinate_query))

    return render_template('neighbour.template',
                           sample_guid = my_guid,
                           sample_name = "asdf",
                           neighbours = neighbours
    )

@myapp.route('/herd')
def herd():
    return render_template('herd.template')

@myapp.route('/cluster')
def cluster():
    return render_template('cluster.template')

@myapp.route('/subcluster')
def subcluster():
    return render_template('subcluster.template')

@myapp.route('/about')
def about():
    return render_template('about.template')

myapp.run()
