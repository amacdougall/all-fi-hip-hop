class MockedMessage:
    def copy(self, value):
        print("MockedMido.MockedMessage 'copy' method!")
        print(f'message: {value}')
        return self

class MockedOutput:
    def send(self, midoMessageObject):
        print("MockedMido.MockedOutput 'send' method!")
        print(f'message: {midoMessageObject}')

class MockedMido:    
    def Message(self, message='', note='', velocity='', channel='', control='', value=''):  
        print("MockedMido 'Message' method!")
        print(f'message: {message}')
        print(f'note: {note}')
        print(f'velocity: {velocity}')
        print(f'channel: {channel}')
        return MockedMessage()
  
    def open_output(self, function):  
        print("MockedMido 'open_output' method!")
        return MockedOutput()

    def get_output_names(self):  
        print("MockedMido 'get_output_names' method!")
        return []
          
    #end of the class definition 