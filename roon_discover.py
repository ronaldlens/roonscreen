import time

from roonapi import RoonApi, RoonDiscovery

def run_discover():

    appinfo = {
        "extension_id": "Ronald's roon screen",
        "display_name": "screen for roon",
        "display_version": "1.0",
        "publisher": "Ronald",
        "email": "ronald@ronald.com"

    }
    print("Start discovery roon_discover")
    start = time.time()
    discover = RoonDiscovery(None)
    servers = discover.all()
    print("stop disovery")
    discover.stop()
    end = time.time()

    print("found the following:")
    print(servers)
    print("time taken: ", end - start)

    apis = [RoonApi(appinfo, None, server[0], server[1], False) for server in servers]

    auth_api = []
    while len(auth_api) == 0:
        print("Waiting for authorisation...")
        time.sleep(1)
        auth_api = [api for api in apis if api.token is not None]

    api = auth_api[0]

    print("Got authorisation")
    print(api.host)
    print(api.core_name)
    print(api.core_id)

    zone_id = ""
    output_id = ""
    for zone in api.zones.values():
        if zone["display_name"] == "WiiM":
            zone_id = zone["zone_id"]
            output_id = zone["outputs"][0]["output_id"]
            print(output_id)
        print(zone["display_name"])


    print("Shutdown apis")
    for api in apis:
        api.stop()


    core_id = api.core_id
    token = api.token

    with open("my_core_id_file", "w") as f:
        f.write(api.core_id)
    with open("my_token_file", "w") as f:
        f.write(api.token)
    with open("my_zone_id", "w") as f:
        f.write(zone_id)
    with open("my_output_id", "w") as f:
        f.write(output_id)

print("roon_discover__")
run_discover()