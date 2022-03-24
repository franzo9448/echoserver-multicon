import selectors
import socket
import types

HOST = "127.0.0.1"
PORT = 65432


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#    s.bind((HOST, PORT))
#    s.listen()
#    conn, addr = s.accept()
#    with conn:
#        print(f"Connected by {addr}")
#        while True:
#            data = conn.recv(1024)
#            if not data:
#                break
#           conn.sendall(data)

def accept(sock):
    conn, addr = sock.accept()
    print("accept")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    eventi = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, eventi, data=data)


def connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(recv_data)
            data.outb = recv_data
        else:
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE and data.outb:
        sent = sock.send(data.outb)
        data.outb = data.outb[sent:]


sel = selectors.DefaultSelector()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for keys, masks in events:
            if keys.data is None:
                accept(keys.fileobj)
            else:
                connection(keys, masks)
except KeyboardInterrupt:
    print("key pressed")
finally:
    sel.close()
