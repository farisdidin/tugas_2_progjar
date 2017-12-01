import socket, select, sys, os, subprocess
import ConfigParser

config = ConfigParser.RawConfigParser()   
config.read('httpserver.conf')

server_address = ('0.0.0.0',config.getint('server','port'))
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server_socket.bind(server_address)
server_socket.listen(5)

input_socket = [server_socket]

print 'Serve at %s port %s'%server_address
try:
	while True:
		read_ready, write_ready, exception = select.select(input_socket, [], [])

		for sock in read_ready:
			if sock == server_socket:
				client_socket, client_address = server_socket.accept()
				input_socket.append(client_socket)
			else:
				data = sock.recv(4096)

				# header = "<html><head><title>dinz</title></head><body>"
				# footer = "</body></html>"
				# result = header + "<h1>hgob</h2>" + footer;
				# print data

				request_header = data.split('\r\n')
				request_file = request_header[0].split()[1]
				print "----- RESPONSE -----"
				print request_file

				if request_file == '/index.html' or request_file == '/':
					f = open('index.html','r')
					response_data = f.read()
					f.close()
					
					content_length = len(response_data)
					response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' +str(content_length) + '\r\n\r\n'
				
				elif request_file == '/test.php':
					currdir = os.getcwd()
					proc = subprocess.Popen("php '"+currdir+"/shell.php'", shell=True, stdout=subprocess.PIPE)
					response_data = proc.stdout.read()
					content_length = len(response_data)
					response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' +str(content_length) + '\r\n\r\n'
				
				else:
					f = open('404.html','r+')
					response_data = f.read()
					f.close()
					content_length = len(response_data)
					response_header= 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' +str(content_length) + '\r\n\r\n'	
						
				sock.sendall(response_header + response_data )
				
				print response_header
				print "--------------------"

except KeyboardInterrupt:
	server_socket.close()
	sys.exit(0)
