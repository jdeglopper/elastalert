import time
import socket
import yaml
import json


CFG = None

try:
    with open('/opt/elastalert/config.yaml', 'r') as ymlfile:
        CFG = yaml.safe_load(ymlfile)
except FileNotFoundError:
    pass


def get_config(key, default):
    return CFG[key] if CFG and key in CFG else default


def wait_for_port(port, host='localhost', timeout=60.0):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                print('Waited too long for the port {} on host {} to start accepting connections.'.format(port, host))
                exit(1)
    print('Host {} and port {} is ready'.format(host, port))


def configure_server():
    conf = {
      'appName': get_config('appName', 'elastalert-server'),
      'port': get_config('port', 3030),
      'wsport': get_config('wsport', 3333),
      'elastalertPath': get_config('elastalertPath', '/opt/elastalert'),
      'verbose': get_config('verbose', False),
      'es_debug': get_config('es_debug', False),
      'debug': get_config('debug', False),
      'rulesPath': {
        'relative': get_config('rulesPath.relative', True),
        'path': get_config('rulesPath.path', '/rules'),
      },
      'templatesPath': {
        'relative': get_config('templatesPath.relative', True),
        'path': get_config('templatesPath.path', '/rule_templates')
      },
      'dataPath': {
        'relative': get_config('dataPath.relative', True),
        'path': get_config('dataPath.path', '/server_data')
      },
      'es_host': get_config('es_host.relative', 'localhost'),
      'es_port': get_config('es_port', 9200),
      'writeback_index': get_config('writeback_index', 'elastalert_status')
    }

    if get_config('start', None):
        conf['start'] = get_config('start', None)

    if get_config('end', None):
        conf['end'] = get_config('end', None)

    with open('/opt/elastalert-server/config/config.json', 'w') as f:
        f.write(json.dumps(conf))


if __name__ == '__main__':
    wait_for_port(
      get_config('es_port', 9200),
      get_config('es_host', 'localhost')
    )
    configure_server()
