from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import logging

messages = []
logging.basicConfig(filename='webserver.log',level=logging.DEBUG)


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
       # print("Client connecting: {0}".format(request.peer))
        logging.info("Client connecting: {0}".format(request.peer))
        self.con_is_open = True

    def onOpen(self):
        """
        When connection is open this method checks if there are new messages from redis-server and if so sends it to
        the client.
        @return:
        """
       # print("WebSocket connection open.")
        logging.info("WebSocket connection open.")

        def hello():
            global messages
            while len(messages):
                if not self.con_is_open:
                    return
                self.sendMessage(messages[0].encode('utf8'))
                messages = messages[1:]
                logging.info('Sent message to client')
            self.factory.loop.call_later(5, hello)

        hello()

    def onClose(self, wasClean, code, reason):
       # print("WebSocket connection closed: {0}".format(reason))
        logging.info("WebSocket connection closed: {0}".format(reason))
        self.con_is_open = False


def main():
    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)

    import asyncio_redis

    @asyncio.coroutine
    def example():
        """
        The function that subscribes to redis channel and waits for messages. Once one appear the function stores it in
        global messages.
        @return:
        """
        # Create connection
        connection = yield from asyncio_redis.Connection.create(host='127.0.0.1', port=6379)

        # Create subscriber.
        subscriber = yield from connection.start_subscribe()

        # Subscribe to channel.
        yield from subscriber.subscribe(['our-channel'])

        # Inside a while loop, wait for incoming events.
        while True:
            reply = yield from subscriber.next_published()
            messages.append(repr(reply.value))
            logging.info('Received: {} on channel {}'.format(repr(reply.value), repr(reply.channel)))
            #print('Received: ', repr(reply.value), 'on channel', reply.channel)

        # When finished, close the connection.
        connection.close()

    loop = asyncio.get_event_loop()
    server = asyncio.async(coro)
    subscriber = asyncio.async(example())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()


if __name__ == '__main__':
    main()