import subprocess
import ast

class ExteriorTemp():

    def __init__(self):
        self.temp_script_path = "/home/pi/Temp/temp.m"
    
    def get(self, year, month, day):
        """
        Return dictionnary of time associated with temperature.
        """
        d = subprocess.check_output([self.temp_script_path, year, month, day])
        l = d.split("\n")
        print l
        return ast.literal_eval(l.pop())
        

if __name__ == "__main__":
    b = ExteriorTemp()
    print b.get("2014", "11", "2")
