import argparse

import modules.client as client
import modules.logger as logger
import modules.server as server
from modules.utils import is_ip_valid

logger = logger.get_logger(__name__)

def run_server(ip, port):
    server.run(ip, port)

def run_client(ip, port):
    client.run(ip, port)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true', help='Run as server', default=False)
    
    ip = input('Server ip: ')
    port = input('Server port: ')

    try:
        port = int(port)
    except:
        raise ValueError('Port must be an int')

    args = parser.parse_args()

    if not is_ip_valid(ip):
        raise ValueError('Incorrect IP')

    if args.server:
        run_server(ip, port)
    else:
        run_client(ip, port)

if __name__ == '__main__':
    main()
