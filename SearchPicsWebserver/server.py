from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import asyncio
import logging
import asyncio_redis


def run(myserverprotocol):
    # Create a new redis connection (this will also auto reconnect)
    connection = yield from asyncio_redis.Connection.create('localhost', 6379)

    try:
        # Subscribe to a channel.
        subscriber = yield from connection.start_subscribe()
        yield from subscriber.subscribe(['spider-channel'])

        # Print published values in a while/true loop.
        while True:
            reply = yield from subscriber.next_published()
            print('Received: ', repr(reply.value), 'on channel', reply.channel)
            myserverprotocol.sendMessage("a")

    finally:
        connection.close()


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    #coro = loop.create_connection(myserverprotocol, '127.0.0.1', '8888')
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)
  #  coro2 = loop.create_task(run(myserverprotocol))
  #  server2 = loop.run_until_complete(coro2)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()