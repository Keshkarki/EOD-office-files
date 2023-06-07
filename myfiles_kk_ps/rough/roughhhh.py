class Atm:

    def __init__ (self):
        self.pin = '1234'
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
        new_pin = input('Enter four digit pin ')
        self.pin = new_pin

    def changePin(self):
        old_pin = input('Enter four digit old pin ')
        if self.pin == old_pin:
            new_pin = input('Enter your new four digit pin ')
            self.pin = new_pin
            print('pin change succesfully')

        else:
            print('chal yaha se')

    def checkBalance(self):
        old_pin = input('Enter four digit old pin ')
        if self.pin == old_pin:
            print(self.bank_balance)

        else:
            print('chhor hai kya')

    def withdraw(self):
        old_pin = input('Enter four digit old pin ')
        if self.pin == old_pin:
            amount = int(input('Enter amount you need '))

            if amount<= self.bank_balance:
                self.bank_balance = self.bank_balance - amount
                print(f'Balance withdrawl successful your remainig balance is {self.bank_balance}')

            else:
                print('abe bhikhari balance to dekh le kitna hai')
        
        else:
            print('pakka chhor hai tu')
obj = Atm()