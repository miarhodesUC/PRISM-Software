import numpy

class CoatCycle():
    def __init__(self, cycle_count = 0, arr_reservoir = [], arr_coat_count = []):
        if len(arr_reservoir) != len(arr_coat_count):
            print("ERROR reservoir array and coat count array have unequal size")
            return 0
        
        self.arr_reservoir = arr_reservoir
        self.arr_coat_count = arr_coat_count

        self.cycle_count = cycle_count
        self.step_count = len(self.arr_reservoir)

        self.current_cycle = 0
        self.current_step = 0
        self.current_coat_count = 0
        self.current_reservoir = 0

    def addStep(self, reservoir, coat):
        self.arr_reservoir.append(reservoir)
        self.arr_coat_count.append(coat)
        self.step_count += 1

    def generateSaveFile(self):
        pass

    def loadCycleSettings(self, cycle_count, step_count, arr_reservoir, arr_coat_count):
        self.cycle_count = cycle_count
        self.step_count = step_count
        self.arr_reservoir = arr_reservoir
        self.arr_coat_count = arr_coat_count

    def executeCycle(self):
        for cycle_index in range(self.cycle_count):
            for step_index in range(self.step_count):
                self.current_reservoir = self.arr_reservoir[step_index]
                self.current_coat_count = self.arr_coat_count[step_index]
                for coat_index in range(self.current_coat_count):
                    print("Cycle #{0} Step #{1} : Coating Reservoir #{2} : Coat #{3} deployed".format(cycle_index, step_index, self.current_reservoir, coat_index))
                self.incrementStep()
            self.incrementCycle()
    
    def changeCycleCount(self, cycle_count):
        self.cycle_count = cycle_count

    def incrementStep(self):
        self.current_step += 1

    def incrementCycle(self):
        self.current_cycle += 1
    
    
