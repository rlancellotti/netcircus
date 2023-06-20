import sys
import unittest
import host
import network 




class MioModuloTestCase(unittest.TestCase):
    def test_simple_creation(self):
        net=network.Network()


        data={'id' : 'Host0' ,'x': 20, 'y': 30, 'width': 48, 'height': 48}
        h=host.Host(net, data)

        self.assertEqual(20,h.x,'Host.x not set properly')
        self.assertEqual(30,h.y,'Host.y not set properly')
        self.assertEqual(48,h.width,'Host.width not set properly')
        self.assertEqual(48,h.height,'Host.height not set properly')
        self.assertEqual('Host0',h.id,'Host.id not set properly')


if __name__ == '__main__':
	unittest.main()





