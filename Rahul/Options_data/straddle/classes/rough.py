class MyClass:
    def __init__(self,value):
        self.value = value

    def print_value(self):
        print(self.value*self.value)


values = [1,2,3,4,5]



for value in values:
    obj = MyClass(value)
    obj.print_value()