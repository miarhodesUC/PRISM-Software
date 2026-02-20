import numpy
import csv
import os
import pigpio
import Firmware as firmware

class CoatCycle():
    def __init__(self, firmware = firmware.SCodeParse(), cycle_count = 0):
        self.firmware = firmware
        self.demoMode = False

        self.nozzle_path = 0
        self.cycle_count = 0
        self.step_count = 0
        self.arr_reservoir = []
        self.arr_coat_count = []
        self.coat_vector = []

        self.current_cycle = 0
        self.current_step = 0
        self.current_coat_count = 0
        self.current_reservoir = 0

        self.basepath = os.getcwd()
        self.nozzle_paths = os.listdir(self.basepath + '\\nozzle_paths')

    def addStep(self, reservoir, coat):
        self.arr_reservoir.append(reservoir)
        self.arr_coat_count.append(coat)
        self.step_count += 1

    def generateSaveFile(self): #TODO make this a JSON file
        coat_vector = self.coat_vector
        with open("SavedCycle.csv", "w", newline="") as file:
            writer = csv.writer(file)
            for row in coat_vector:
                writer.writerow(row)
            print("Cycle data saved to SavedCycle.csv")
    
    def loadSaveFile(self, filename):
        with open(filename, "r") as file:
            content = csv.reader(file)
            for line in content:
                int_line = [int(s) for s in line]
                self.coat_vector.append(int_line)
                print(int_line)
        self.loadCoatVector()
        
    def loadCoatVector(self):
        self.step_count = self.coat_vector[2][0]
        self.cycle_count = self.coat_vector[2][1]
        self.arr_reservoir = self.coat_vector[0]
        self.arr_coat_count = self.coat_vector[1]
        self.nozzle_path = self.coat_vector[3]

    def executeCycle(self):
        self.loadSaveFile()
        if self.demoMode:
            for cycle_index in range(self.cycle_count):
                for step_index in range(self.step_count):
                    self.current_reservoir = self.arr_reservoir[step_index]
                    self.current_coat_count = self.arr_coat_count[step_index]
                    for coat_index in range(self.current_coat_count):
                        print("Cycle #{0} Step #{1} : Coating Reservoir #{2} : Coat #{3} deployed".format(
                            cycle_index, step_index, self.current_reservoir, coat_index))
                    self.incrementStep()
                self.incrementCycle()
        else:
            self.firmware.startSequence(self.nozzle_path, self.coat_vector)
    
    def changeCycleCount(self, cycle_count):
        self.cycle_count = cycle_count

    def updatePathFiles(self):
        self.nozzle_paths = os.listdir(self.basepath + 'nozzle_paths')
    
    def incrementStep(self):
        self.current_step += 1

    def incrementCycle(self):
        self.current_cycle += 1
    
    
