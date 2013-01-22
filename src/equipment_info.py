'''
Created on Jan 15, 2013

@author: a0868443
'''
platforms_list = {}
 
class EquipmentInfo:
    "class to define equipment information."
    serial_params = {}
    name =  ""
    buildId = ""
    def __init__(self,name, builId = None):
        self.name = name
        self.builId = builId
        platforms_list[name] = self	

