from tkinter import Tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilename


class Url_path:
    def __init__(self):
        self.root = Tk()
        self.fi = []

    def save_path(self):
        self.fi = []
        file = askopenfilename()

        if file:
            self.fi.append(str(file))
            self.fi = f'{self.fi[0]}'
            print(self.fi)

URL = Url_path()
URL.save_path()
print(URL.fi)