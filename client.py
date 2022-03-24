import selectors
import socket
import types

HOST = "127.0.0.1"
PORT = 65432

sel = selectors.DefaultSelector()
messages = [b"Hello1", b"Hello2"]


def start_connection(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        event = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outbound=b""
        )
        sel.register(sock, event, data=data)


def feed_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_WRITE:
        if not data.outbound and data.messages:
            data.outbound = data.messages.pop(0)
        if data.outbound:
            send = sock.send(data.outbound)
            data.outbound = data.outbound[send:]
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        print(f"receiving data: {recv_data}")
        if recv_data:
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            sel.unregister(sock)
            sock.close()


start_connection(HOST, PORT, 2)

try:
    while True:
        events = sel.select(timeout=None)
        if events:
            for keys, masks in events:
                feed_connection(keys, masks)
        if not sel.get_map():
            break

except KeyboardInterrupt:
    print("key pressed")
finally:
    sel.close()
