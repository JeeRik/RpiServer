import socket
from GpioThread import GpioThread

def readlines(sock, recv_buffer=4096, delim='\n'):
	buffer = ''
	data = True
	while data:
		data = sock.recv(recv_buffer)
		buffer += data

		while buffer.find(delim) != -1:
			line, buffer = buffer.split('\n', 1)
			yield line
	return

# A connection is established, run the main loop for that connection
def connectionBody(c, caddr, thread):
    # while True:
    for line in readlines(c):
        line = line.strip()
        line = line.strip('\r')
        if len(line.split()) <= 0:
            continue

        reply = thread.ctrl(line)
        if not reply.endswith("\n"):
            reply += "\n"
        c.send(reply)

def main():
    server = None;
    t = None

    try:
        print("Setting up server")
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = 12345
        server.bind(("", port))
        server.listen(5)

        print("Starting GPIO thread")
        t = GpioThread()
        t.start()

        print("Listening for connection at port {}".format(port))

        while True:
            c, caddr = server.accept()
            print("Connection from {}".format(caddr))

            connectionBody(c, caddr, t)

            print("EOF")
            c.close()

    finally:
        if server is not None:
            server.close();
            print("Server closed")
        else:
            print("Server not initialized")

        if t is not None:
            t.quit()
            t.join(1)
            print("Gpio thread terminated")
        else:
            print("GpioThread not started")

if __name__ == '__main__':
    main()