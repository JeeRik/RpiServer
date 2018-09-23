import socket
import logging

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

        if line == "ping":
            reply = "pong"
        else:
            reply = thread.ctrl(line)

        if not reply.endswith("\n"):
            reply += "\n"
        c.send(reply)
        logging.info("Command \"{}\", Reply \"{}\"".format(line, reply.strip()))

def main():
    logging.basicConfig(filename='/home/maara/RpiServer/log.txt', level=logging.DEBUG)

    server = None;
    t = None

    try:
        logging.info("Setting up server")
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = 12345
        server.bind(("", port))
        server.listen(5)

        logging.info("Starting GpioThread")
        t = GpioThread()
        t.start()

        logging.info("Listening for connection at port {}".format(port))

        while True:
            c, caddr = server.accept()
            logging.info("Connection from {}".format(caddr))

            t.isConnected = True
            connectionBody(c, caddr, t)
            t.isConnected = False

            logging.info("Connection EOF")
            c.close()

    finally:
        if server is not None:
            server.close();
            logging.info("Server closed")
        else:
            logging.info("Server not initialized")

        if t is not None:
            t.quit()
            t.join(1)
            logging.info("GpioThread terminated")
        else:
            logging.info("GpioThread not started")

if __name__ == '__main__':
    main()