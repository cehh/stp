'''
Created on Jan 15, 2013

@author: a0868443
'''

dut = EquipmentInfo("evmskAM335x", "starterware")
dut.serial_params = {'port':'/dev/ttyUSB1', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}

dut = EquipmentInfo("am37x-evm", "starterware")
dut.serial_params = {'port':'/dev/ttyUSB1', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}

