import socket
from cell import Cell

class Socket:
    def __init__(self, adress):
        self.sock = None
        self.conn = None
        self.adress = adress
        try:
            print("conn")
            self.conn = socket.socket()
            self.conn.connect(adress)
            print("conn finish")

        except (ConnectionRefusedError, TimeoutError):
            print("sock")
            self.conn = None
            self.sock = socket.socket()
            self.sock.bind(adress)
            self.sock.listen(1)
            print("sock finish")
            
    def accept(self):    
        self.sock.setblocking(0)
        try:      
            self.conn, self.addr = self.sock.accept()
        except socket.error:
            return None
        else:
            return 0

    def send_color_and_size(self, color, size):
        self.conn.send(bytes(f'{color}, {size}', 'utf-8'))

    def recv_color_and_size(self):
        self.conn.setblocking(0)
        color = None
        try:
            data = self.conn.recv(40)
            udata = data.decode("utf-8").split(",")
            if udata[0] == 'Cell.RED':
                color = Cell.RED
            elif udata[0] == 'Cell.BLUE':
                color = Cell.BLUE
        except socket.error:
            return None
        else:           
            return color, udata[1]

    def send(self, coordinats):
        if coordinats == 'EXIT':
            self.conn.send(b'EXIT')
        elif coordinats == 'CHANGING_RIVAL':
            self.conn.send(b'CHANGING_RIVAL')
        else:
            self.conn.send(bytes(coordinats))

    def recv(self):
        self.conn.setblocking(0)
        try:
            data = self.conn.recv(20)
            if data == b'EXIT':
                return 'EXIT'
            elif data == b'CHANGING_RIVAL':
                return 'CHANGING_RIVAL'
            else:
                return tuple(data)
        except socket.error:
            return None