#!/usr/bin/env python3
"""Write demo.pcap: a small synthetic capture for the "agent reads packets" demo.
No external dependencies. Contents (all made up, RFC 5737 / RFC 1918 addresses):
  1. DNS query/response for intranet.example.edu
  2. TCP handshake + HTTP POST /login with a cleartext form password
  3. HTTP GET /admin with an Authorization: Basic header
  4. A burst of SYNs from one host to many ports (looks like a port scan)
"""
import struct, time, base64

CLIENT  = ("10.9.0.5",  "02:42:0a:09:00:05")
SERVER  = ("10.9.0.80", "02:42:0a:09:00:50")
DNSSRV  = ("10.9.0.1",  "02:42:0a:09:00:01")
SCANNER = ("10.9.0.66", "02:42:0a:09:00:42")

def ip2b(s): return bytes(int(x) for x in s.split("."))
def mac2b(s): return bytes.fromhex(s.replace(":", ""))

def csum(b):
    if len(b) % 2: b += b"\0"
    s = sum(struct.unpack("!%dH" % (len(b)//2), b))
    while s >> 16: s = (s & 0xffff) + (s >> 16)
    return (~s) & 0xffff

def ipv4(src, dst, proto, payload):
    hdr = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20+len(payload), 1, 0x4000, 64, proto, 0, ip2b(src), ip2b(dst))
    hdr = hdr[:10] + struct.pack("!H", csum(hdr)) + hdr[12:]
    return hdr + payload

def tcp(src, sport, dst, dport, seq, ack, flags, payload=b""):
    hdr = struct.pack("!HHIIBBHHH", sport, dport, seq, ack, 5<<4, flags, 65535, 0, 0)
    pseudo = ip2b(src) + ip2b(dst) + struct.pack("!BBH", 0, 6, len(hdr)+len(payload))
    c = csum(pseudo + hdr + payload)
    return hdr[:16] + struct.pack("!H", c) + hdr[18:] + payload

def udp(src, sport, dst, dport, payload):
    return struct.pack("!HHHH", sport, dport, 8+len(payload), 0) + payload

def eth(smac, dmac, payload): return mac2b(dmac) + mac2b(smac) + b"\x08\x00" + payload

frames = []
t = time.time()
def add(frame, dt=0.001):
    global t
    t += dt
    frames.append((t, frame))

SYN, ACK, PSH, FIN, RST = 0x02, 0x10, 0x08, 0x01, 0x04

# 1. DNS
qname = b"".join(bytes([len(l)]) + l for l in b"intranet.example.edu".split(b".")) + b"\0"
q = struct.pack("!HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0) + qname + struct.pack("!HH", 1, 1)
add(eth(CLIENT[1], DNSSRV[1], ipv4(CLIENT[0], DNSSRV[0], 17, udp(CLIENT[0], 51000, DNSSRV[0], 53, q))))
r = struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0) + qname + struct.pack("!HH", 1, 1) \
    + b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 300, 4) + ip2b(SERVER[0])
add(eth(DNSSRV[1], CLIENT[1], ipv4(DNSSRV[0], CLIENT[0], 17, udp(DNSSRV[0], 53, CLIENT[0], 51000, r))))

# 2. TCP handshake + cleartext login
def http_exchange(sport, request, response):
    cs, ss = 1000, 5000
    add(eth(CLIENT[1], SERVER[1], ipv4(CLIENT[0], SERVER[0], 6, tcp(CLIENT[0], sport, SERVER[0], 80, cs, 0, SYN))))
    add(eth(SERVER[1], CLIENT[1], ipv4(SERVER[0], CLIENT[0], 6, tcp(SERVER[0], 80, CLIENT[0], sport, ss, cs+1, SYN|ACK))))
    add(eth(CLIENT[1], SERVER[1], ipv4(CLIENT[0], SERVER[0], 6, tcp(CLIENT[0], sport, SERVER[0], 80, cs+1, ss+1, ACK))))
    add(eth(CLIENT[1], SERVER[1], ipv4(CLIENT[0], SERVER[0], 6, tcp(CLIENT[0], sport, SERVER[0], 80, cs+1, ss+1, PSH|ACK, request))), 0.02)
    add(eth(SERVER[1], CLIENT[1], ipv4(SERVER[0], CLIENT[0], 6, tcp(SERVER[0], 80, CLIENT[0], sport, ss+1, cs+1+len(request), PSH|ACK, response))), 0.05)
    add(eth(CLIENT[1], SERVER[1], ipv4(CLIENT[0], SERVER[0], 6, tcp(CLIENT[0], sport, SERVER[0], 80, cs+1+len(request), ss+1+len(response), FIN|ACK))))
    add(eth(SERVER[1], CLIENT[1], ipv4(SERVER[0], CLIENT[0], 6, tcp(SERVER[0], 80, CLIENT[0], sport, ss+1+len(response), cs+2+len(request), FIN|ACK))))

body = b"username=jdoe&password=Fall2026!&remember=1"
req = (b"POST /login HTTP/1.1\r\nHost: intranet.example.edu\r\nUser-Agent: Mozilla/5.0\r\n"
       b"Content-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n" % len(body)) + body
resp = b"HTTP/1.1 302 Found\r\nLocation: /home\r\nSet-Cookie: session=8f3a9c1e; HttpOnly\r\nContent-Length: 0\r\n\r\n"
http_exchange(52001, req, resp)

# 3. Basic auth
tok = base64.b64encode(b"admin:hunter2").decode()
req2 = ("GET /admin HTTP/1.1\r\nHost: intranet.example.edu\r\nAuthorization: Basic %s\r\n\r\n" % tok).encode()
resp2 = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 27\r\n\r\n<h1>Admin dashboard</h1>\n"
http_exchange(52002, req2, resp2)

# 4. SYN burst from another host
for i, port in enumerate([21, 22, 23, 25, 80, 110, 139, 143, 443, 445, 3306, 3389, 5432, 8080]):
    add(eth(SCANNER[1], SERVER[1], ipv4(SCANNER[0], SERVER[0], 6, tcp(SCANNER[0], 40000+i, SERVER[0], port, 777, 0, SYN))), 0.0003)
    if port in (22, 80, 443):
        add(eth(SERVER[1], SCANNER[1], ipv4(SERVER[0], SCANNER[0], 6, tcp(SERVER[0], port, SCANNER[0], 40000+i, 9000, 778, SYN|ACK))), 0.0002)
    else:
        add(eth(SERVER[1], SCANNER[1], ipv4(SERVER[0], SCANNER[0], 6, tcp(SERVER[0], port, SCANNER[0], 40000+i, 0, 778, RST|ACK))), 0.0002)

with open("demo.pcap", "wb") as f:
    f.write(struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))
    for ts, fr in frames:
        f.write(struct.pack("<IIII", int(ts), int((ts % 1) * 1e6), len(fr), len(fr)) + fr)
print("wrote demo.pcap with", len(frames), "frames")
