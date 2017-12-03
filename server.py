import socket, select, sys, os, subprocess
import ConfigParser
import urllib2

config = ConfigParser.RawConfigParser()   
config.read('httpserver.conf')

server_address = ('0.0.0.0',config.getint('server','port'))
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server_socket.bind(server_address)
server_socket.listen(5)

input_socket = [server_socket]
list_dataset = []

#------
for dirname, dirnames, filenames in os.walk('./dataset'):
    # print path to all subdirectories first.
    for subdirname in dirnames:
        print(os.path.join(dirname, subdirname))

    # print path to all filenames.
    numb = 1
    for filename in filenames:
        print(os.path.join(dirname, filename))
        list_dataset.append(os.path.join(dirname, filename).split("/")[2]) 
        numb+=1

    # Advanced usage:
    # editing the 'dirnames' list will stop os.walk() from recursing into there.
    if '.git' in dirnames:
        # don't go into any .git directories.
        dirnames.remove('.git')

print list_dataset
#------
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

				if data:
					
					print data

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
						print content_length
					elif request_file == '/dataset':
						currdir = os.getcwd()
						proc = subprocess.Popen("php '"+currdir+"/test.php'", shell=True, stdout=subprocess.PIPE)
						response_data = proc.stdout.read()
						content_length = len(response_data)
						response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' +str(content_length) + '\r\n\r\n'

					

					else:
						for a in list_dataset:
							if request_file == '/dataset/'+a:
								print "bisa tuh >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
								file_download = 'dataset/'+a
								content_length = os.path.getsize(file_download)
								file = open(file_download, 'rb')
								response_data = file.read()
								file.close()
								response_header = 'HTTP/1.1 200 OK\r\nContent-Type: multipart/form-data; charset=UTF-8\r\nContent-Length:' +str(content_length) + '\r\n\r\n'

									
						# f = open('404.html','r+')
						# response_data = f.read()
						# f.close()
						# content_length = len(response_data)
						# response_header= 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' +str(content_length) + '\r\n\r\n'	
							
					sock.sendall(response_header + response_data )
					
					print content_length
					print response_data
					print "--------------------"

except KeyboardInterrupt:
	server_socket.close()
	sys.exit(0)
