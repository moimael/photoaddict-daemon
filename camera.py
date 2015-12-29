class Camera:
    def __init__(self):
        self.manufacturer = None
        self.model = None
        self.serial_number = None
        self.last_plugged = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
