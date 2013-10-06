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
    result = ""
    # we got the whole thing if we received all the fields
    while "error" not in result or "id" not in result or "result" not in result:
        reply = socket.recv(BUFFER_SIZE)
        result += reply
    return result

def listen_for_messages(sock):
    inputs = [sock, sys.stdin]
    outputs = []
    message_queues = {}
    message_queues[sock] = Queue.Queue()
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
                print data
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

def list_dbs(socket, current_id):
    list_dbs_query =  '{"method":"list_dbs", "params":[], "id": %d}' % (current_id)
    socket.send(list_dbs_query)
    reply = socket.recv(BUFFER_SIZE)
    # add some error checking here to confirm that the reply is correct and has right id
    return json.loads(reply)['result']

def get_schema(socket, db = DEFAULT_DB, current_id = 0):
    list_schema = {"method": "get_schema", "params":[db_name], "id": current_id}
    socket.send(json.dumps(list_schema))
    result = gather_reply(socket)
    return json.loads(result)

def get_schema_version(server, db = DEFAULT_DB):
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
    print reply
    return json.loads(reply)

def monitor_cancel():
    return

def locking():
    return

def echo():
    return

def dump(server, db):
    return

def list_bridges(socket, db = DEFAULT_DB):
    # What if we replaced with a more specific query
    # columns = {"Bridge":{"name"}}
    columns = {"Port":{"columns":["fake_bridge","interfaces","name","tag"]},"Controller":{"columns":[]},"Interface":{"columns":["name"]},"Open_vSwitch":{"columns":["bridges","cur_cfg"]},"Bridge":{"columns":["controller","fail_mode","name","ports"]}}
    #msg = """
    #    { "method": "monitor",
    #            "params":["Open_vSwitch",null,{"Port":{"columns":["fake_bridge","interfaces","name","tag"]},"Controller":{"columns":[]},"Interface":{"columns":["name"]},"Open_vSwitch":{"columns":["bridges","cur_cfg"]},"Bridge":{"columns":["controller","fail_mode","name","ports"]}}],
    #                    "id": 0} 
    #"""
    #return monitor(socket, columns, db)['result']
    # TODO: cancel the monitor after we're done?
    return monitor(socket, columns, db)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((OVSDB_IP, OVSDB_PORT))

current_id = 0

db_list = list_dbs(s, current_id)
print db_list
db_name = db_list[0]
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
listen_for_messages(s)
