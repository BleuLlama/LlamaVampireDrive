
class Transform(object):
    """do-nothing: forward all data unchanged"""
    def rx(self, text):
        """text received from serial port"""
        return text

    def tx(self, text):
        """text to be sent to serial port"""
        return text

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text
