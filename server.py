import threading
import SocketServer
import struct
import argparse
import sys
import subprocess
import tempfile
import os
from copy import deepcopy

# Local stuff
from utils import *

class ThreadedEchoRequestHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    compile_directory = tempfile.mkdtemp()

    print 'Compile directory:', compile_directory

    preprocessed_string = recv_msg(self.request)

    preprocessed_file_name = os.path.join(compile_directory, 'temp.C')
    preprocessed_file = open(preprocessed_file_name, 'wb')
    preprocessed_file.write(preprocessed_string)
    preprocessed_file.close()

    clean_compile_command = recv_msg(self.request)

    print 'clean compile command', clean_compile_command

    compile_command = clean_compile_command + ' ' + preprocessed_file_name + ' -o  ' + os.path.join(compile_directory, 'object.o')

    # Compile the file
    try:
      compile_output = subprocess.check_output(compile_command, stderr=subprocess.STDOUT, shell=True)
      send_msg(self.request, '0')
    except subprocess.CalledProcessError as e:
      send_msg(self.request, '1')
      send_msg(self.request, e.output)

    return


    print compile_output

    cur_thread = threading.currentThread()
    send_msg(self.request, cur_thread.getName() + 'stuff')

#    os.removedirs(compile_directory)

    return

class ThreadedEchoServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  pass

# Server
address = ('localhost', 0) # let the kernel give us a port
server = ThreadedEchoServer(address, ThreadedEchoRequestHandler)
ip, port = server.server_address # find out what port we were given

t = threading.Thread(target=server.serve_forever)
t.setDaemon(True) # don't hang on exit
t.start()
print 'Server loop running in thread:', t.getName()
