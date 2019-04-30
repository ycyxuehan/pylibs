from soraka import Soraka
from soraka import start_server
from soraka import SoAnt
from time import sleep

class SoTest(Soraka):
    def service(self, params):
        print('service:', params)
        return 'good!'

class SoTestAnt(SoAnt):
    def service(self, params):
        self.report({'status':'running', 'process':'01', 'resultFilelink':'data/result.csv'})
        for i in range(0,100):
            print('service:', params)
            sleep(3)
        self.report({'status':'completd', 'process':'01', 'resultFilelink':'data/result.csv'})
        return 'good!'

if __name__ == '__main__':
    SERVICES = [
        {'location':'/51job', 'args':{'SoAnt':SoTestAnt(host='192.168.1.203', port=30000)}, 'method':'GET', 'name':'51Job'},
        {'location':'/meituan', 'args':{'SoAnt':SoTestAnt(host='192.168.1.203', port=30000)}, 'method':'GET', 'name':'Meituan'},
        {'location':'/dazhongdianping', 'args':{'SoAnt':SoTestAnt(host='192.168.1.203', port=30000)}, 'method':'GET', 'name':'Dazhongdianping'}
    ]
    test = Soraka(host='192.168.1.203', port='30000', services=SERVICES)
    start_server(test)
