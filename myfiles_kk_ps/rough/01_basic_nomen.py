
# Nomenclature
#function -->  def snake_casing 
#class -->  class PascalCase
#method --> def camelCase 


#   %% 
def square(num):
    return num**2

my_func = square(4)

print(my_func)


# %%
lst = [1,2,3,4,5,6,my_func]
lst

# %%
s = 'hello'
s.append('x')

# %%
lst = list((1,2,3))
print(lst)
print(type(lst))

# %% OOP START
def square():
    print('Hello')

square()


# %%
class SquareOfNo:

    # constructor
    def __init__ (self,num):
        self.num = 3
        print('Hello my name is constructor')
        self.squareNikalKeDo()

    def squareNikalKeDo(self):
        print(self.num**2)

    def method2(self):
        pass

    def method3(self):
        pass


obj = SquareOfNo(10)
# obj.squareNikalKeDo(5)

# %% MAKING OUR OWN ATM MACHINE USING OOP

class Atm:

    def __init__ (self):
        self.pin = ''
        self.bank_balance = 500
        self.menu()

    
    def menu(self):
            user_input = input("""
                        Hi how can I help you?
                        1. Press 1 to create pin
                        2. Press 2 to change pin
                        3. Press 3 to check balance
                        4. Press 4 to withdraw
                        5. Anything else to exit
    """)
            

            if user_input == '1':
                self.createPin()
                
            elif user_input == '2':
                self.changePin()

            elif user_input == '3':
                self.checkBalance()

            elif user_input == '4':
                self.withdraw()

            else:
                exit()


    def createPin(self):
        new_pin = input('Enter four digit pin')
        self.pin = new_pin

    def changePin(self):
        old_pin = input('Enter four digit old pin')
        if self.pin == old_pin:
            new_pin = input('Enter your new four digit pin')
            self.pin = new_pin

        else:
            print('chal yaha se')


    def checkBalance(self):
        old_pin = input('Enter four digit old pin')
        if self.pin == old_pin:
            print(self.bank_balance)

        else:
            print('chhor hai kya')

    def withdraw(self):
        old_pin = input('Enter four digit old pin')
        if self.pin == old_pin:
            amount = int(input('Enter amount you need '))

            if amount<= self.bank_balance:
                self.bank_balance = self.bank_balance - amount
                print('Balance withdrawl successful')

            else:
                print('abe bhikhari balance to dekh le kitna hai')

        
        else:
            print('pakka chhor hai tu')
                





obj = Atm()
# print(obj.pin)


# %%
