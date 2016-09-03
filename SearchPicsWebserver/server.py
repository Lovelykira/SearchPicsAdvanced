from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

# Здесь храним сообщения между получением от редиса и отправкой по вебсокету
messages = []
connection_open = False


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        global connection_open
        connection_open = True


    def onOpen(self):
        print("WebSocket connection open.")

        # при открытии вебсокета, будем раз в секунду проверять появляение сообщений и отправлять их
        def hello():
            global messages, connection_open
            while len(messages):
                if connection_open:
                    self.sendMessage(messages[0].encode('utf8'))
                    messages = messages[1:]
            self.factory.loop.call_later(5, hello)

        hello()

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        global connection_open
        connection_open = False


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

    # Здесь мы подписываемся на обновления от редиса
    @asyncio.coroutine
    def example():
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
            print('Received: ', repr(reply.value), 'on channel', reply.channel)

        # When finished, close the connection.
        connection.close()

    # а тут мы запускаем и сервер, и слушатель редиса асинхронно
    loop = asyncio.get_event_loop()
    server = asyncio.async(coro)
    baa = asyncio.async(example())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()


if __name__ == '__main__':
    main()