import io
import ctypes
import struct
import contextlib
import socket
from random import randint

# The whole code is a workaround it will be replaced with an async routine
# 'import asyncio', but at the moment it will be solved by a Thread

#TODO: recv incomming messages messages
#TODO: support multiple packages

class ResponseFIFO:
    def __init__(self, size=20):
        self._data = dict()
        self._keys = list()
        self._size = size

    def pop(self, p_id):
        try:
            self._keys.remove(p_id)
            r = self._data[p_id]
            del self._data[p_id]
        except Exception as e:
            r = b''
        return r

    def put(self, p_id, data):
        if p_id in self._keys:
            self._data[p_id] += data
            return
        if len(self._keys) == self._size:
            self.pop(self._keys[self._size-1])
        self._keys.insert(0, p_id)
        self._data[p_id] = data
        return

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value


class Transport(object):
    max_pack_size = 4096
    head_size = 12
    def __init__(self, hostinfo):
        # Tuple (IP, PORT, Password)
        self.hostinfo = hostinfo
        self._sock = None
        self._create_connection()
        self.current_pack_id = ctypes.c_uint32()
        self.current_pack_id.value = randint(0, 2**32 - 1)
        self._auth()
        self._resp = ResponseFIFO(size=20)

    def send(self, data):
        packets = [self._pack(data)] if len(data) < self.max_pack_size - 10 else [self._pack(x) for x in self._cut_message(data)]

        for packet_to_send in packets:
            try:
                self._sock.send(packet_to_send[0])
            except Exception:
                self._create_connection
                self._auth()
                self._sock.send(packet_to_send[0])
        while True:
            try:
                header = self.recv(self.head_size)
                size, p_id, packet_type = self._read_header(header)
                self._resp.put(p_id,  self.recv(size))
            except:
                break
        return (packet[1] for packet in packets)

    def get(self, p_id):
        return io.BytesIO(self._resp.pop(p_id))

    def timeout(self, timeout_time):
        self._sock.settimeout(timeout_time)
        if timeout_time == 0:
            self._sock.setblocking(False)

    def _create_connection(self):
        try:
            if self._sock:
                self._sock.close()
            self._sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            # Timeout for the creation of the server (it may be laggy etc..)
            self._sock.settimeout(4)
            self._sock.connect((self.hostinfo[0], self.hostinfo[1]))
            self._sock.setblocking(False)
        except Exception as e:
            raise e

    def _read_header(self, bin_header):
        size, p_id, packet_type = struct.unpack('<III', bin_header[:12])
        size -= 8
        return size, p_id, packet_type

    def _auth(self):
        auth_pack, p_id = self._pack(self.hostinfo[2], packet_type=3)
        self._sock.send(auth_pack)
        if self._read_header(self._sock.recv(14))[1] != p_id:
            raise NoAuth

    def _pack(self, data, packet_type=2):
        """Normal packet is the source standart SERVERDATA_EXECCOMMAND
        further reading: https://developer.valvesoftware.com/wiki/Source_RCON_Protocol"""
        p_id = self.current_pack_id.value
        self.current_pack_id.value += 1
        r = struct.pack('<III{0}sc'.format(len(data)), len(data) + 9, p_id, packet_type, data.encode(), b'\x00')
        return r, p_id

    def _cut_message(self, message):
        while self.cvars:
            if len(self.cvars) > self.max_len:
                data = self.cvars[:self.max_len]
                tail = self.max_len - data[::-1].index(';')
                data = self.cvars[:tail]
                self.cvars = self.cvars[tail:]
            else:
                data = self.cvars
                self.cvars = ""
            yield data

    def __del__(self):
        with contextlib.suppress(Exception):
            self._sock.close()

class NoAuth(Exception):
    def __str__(self):
        return 'Password is wrong'
