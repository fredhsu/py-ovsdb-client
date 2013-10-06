import ovsdb
import unittest
import socket

class TestFunctions(unittest.TestCase):

    def setUp(self):
        OVSDB_IP = '127.0.0.1'
        OVSDB_PORT = 6632
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((OVSDB_IP, OVSDB_PORT))

    def test_list_dbs(self):
        self.sock.send(ovsdb.list_dbs())
        db_list = ovsdb.gather_reply(self.sock)
        db_name = db_list['result'][0]
        self.assertEqual(db_name, 'Open_vSwitch')

    def test_monitor(self):
        columns = {"Bridge":{"columns":["name"]}}
        self.sock.send(ovsdb.monitor(columns))
        result = ovsdb.gather_reply(self.sock)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['id'], 0)
        self.assertTrue("Bridge" in result['result'])

    def test_list_br(self):
        self.sock.send(ovsdb.list_bridges())
        bridge_list = ovsdb.gather_reply(self.sock)
        bridges = bridge_list['result']['Bridge']
        #print bridges
        print bridges.values()
        self.assertTrue("br0" in bridges.values())

    def test_choice(self):
        self.assertTrue(True)
    
if __name__ == '__main__':
    unittest.main()
