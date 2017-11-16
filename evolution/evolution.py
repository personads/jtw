import sys, os
from subprocess import Popen


config_path = "/home/kuro/Projects/ComputationalIntelligence/torcs-server/example_torcs_config.xml"

if __name__ == '__main__':
    torcs_process = Popen(['torcs' ,'-r', config_path], shell=False)
    driver1_process = Popen(['python', '/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/run/mlp.py'], shell=False)
    print(str(driver1_process.pid))
    stdout, stderr = driver1_process.communicate()
    while(driver1_process.poll() == None):
        pass