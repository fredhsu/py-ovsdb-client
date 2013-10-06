import sys
import Queue
import socket
import json
from select import select

OVSDB_IP = '127.0.0.1'
OVSDB_PORT = 6632
DEFAULT_DB = 'Open_vSwitch'
BUFFER_SIZE = 4096

# TODO: Could start by getting the DB name and using that for ongoing requests
# TODO: How to keep an eye out for montor, update, echo messages?
def gather_reply(socket):
    print "Waiting for reply"
    result = ""
    # we got the whole thing if we received all the fields
    while "error" not in result or "id" not in result or "result" not in result:
        reply = socket.recv(BUFFER_SIZE)
        result += reply
    return json.loads(result)

def listen_for_messages(sock, message_queues):
    # To send something, add a message to queue and append sock to outputs
    inputs = [sock, sys.stdin]
    outputs = []
    while sock:
        readable, writable, exceptional = select(inputs, outputs, [])
        for s in readable:
            if s is sock:
                data = sock.recv(4096)
                # should test if its echo, if so, reply
                # message_type = get_msg_type(data)
                # if message_type is "echo":
                #   send_echo(message_
                message_queues[sock].put(data)
                outputs.append(sock)
                print "recv:" + data
            elif s is sys.stdin:
                print sys.stdin.readline()
                sock.close()
                return
            else:
                print "error"
        for w in writable:
            if w is sock:
                sock.send(message_queues[sock].get_nowait())
                outputs.remove(sock)
            else:
                print "error"

def list_dbs():
    list_dbs_query =  {"method":"list_dbs", "params":[], "id": 0}
    return json.dumps(list_dbs_query)

def get_schema(socket, db = DEFAULT_DB, current_id = 0):
    list_schema = {"method": "get_schema", "params":[db_name], "id": current_id}
    socket.send(json.dumps(list_schema))
    result = gather_reply(socket)
    return result

def get_schema_version(socket, db = DEFAULT_DB):
    db_schema = get_schema(socket, db)
    return db_schema['version']

def list_tables(server, db):
    # keys that are under 'tables'
    db_schema = get_schema(socket, db)
    # return db_schema['tables'].keys
    return json.loads()

def list_columns(server, db):
    return

def transact(server, transactions):
    # Variants of this will add stuff
    return

def monitor(socket, columns, monitor_id = None, db = DEFAULT_DB):
    # Variants of this will do ovs-vsctl list commands
    msg = {"method":"monitor", "params":[db, monitor_id, columns], "id":0}
    #print json.dumps(msg)
    socket.send(json.dumps(msg))
    reply = gather_reply(socket)
    return reply

def monitor_cancel():
    return

def locking():
    return

def echo():
    echo_msg = {"method":"echo","id":"echo","params":[]}
    return json.dumps(echo_msg)

def dump(server, db):
    return

def list_bridges(socket, db = DEFAULT_DB):
    # What if we replaced with a more specific query
    # columns = {"Bridge":{"name"}}
    columns = {"Port":{"columns":["fake_bridge","interfaces","name","tag"]},"Controller":{"columns":[]},"Interface":{"columns":["name"]},"Open_vSwitch":{"columns":["bridges","cur_cfg"]},"Bridge":{"columns":["controller","fail_mode","name","ports"]}}
    # TODO: cancel the monitor after we're done?
    return monitor(socket, columns, db)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((OVSDB_IP, OVSDB_PORT))

current_id = 0

s.send(list_dbs())
db_list = gather_reply(s)
db_name = db_list['result'][0]
print "list bridges:"
bridge_list = list_bridges(s, db_name)

print bridge_list
bridges = bridge_list['result']['Bridge']
print "\nbridges\n"
print bridges.values()
for bridge in bridges.values():
    print "---"
    print bridge['new']['name']
#db_schema = get_schema(s, db_name)
#print db_schema

#columns = {"Bridge":{"columns":["name"]}}
#print monitor(s, columns, 1)

# TODO: Put this in a thread and use Queues to send/recv data from the thread
message_queues = {}
message_queues[s] = Queue.Queue()
listen_for_messages(s, message_queues)
