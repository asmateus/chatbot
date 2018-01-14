from . import consumers

channel_routing = {
    'websocket.connect': consumers.connect,
    'websocket.receive': consumers.receive,
    'websocket.disconnect': consumers.disconnect,
}
