# [ref] https://typesense.org/docs/guide/installing-a-client.html

# typesense_client.py
import typesense
from typing import Dict

# In-memory cache for clients keyed by API key + host:port
_clients_cache = {}

async def get_typesense_client(config: Dict):
    """
    config example:
    {
        "host": "localhost",
        "port": "8108",
        "protocol": "http",
        "api_key": "xyz"
    }
    """

    #set..
    # Loop through nodes and join host:port
    host_ports = [f"{node['host']}:{node['port']}" for node in config["nodes"]]
    _host_ports = "_".join(host_ports)



    # Use a unique key per Typesense endpoint + API key
    #key = f"{config['host']}:{config['port']}:{config['api_key']}"
    key = f"{_host_ports}:{config['api_key']}"


    #log..
    #print(key)
    #print(config)


    """
    {
            "nodes": [
                {
                    "host": config["host"],
                    "port": config["port"],
                    "protocol": config.get("protocol", "http")
                }
            ],
            "api_key": config["api_key"],
            "connection_timeout_seconds": 2
        }
    """

    #set..
    if key not in _clients_cache:
        #client = await typesense.Client(config)
        client = typesense.Client(config)
        _clients_cache[key] = client

    return _clients_cache[key]
