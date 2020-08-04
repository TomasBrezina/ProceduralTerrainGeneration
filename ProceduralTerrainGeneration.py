from tkinter import *
from PIL.Image import fromarray
from PIL import ImageTk, Image
import noise
import numpy as np
import time

# for measuring time
def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

WHT = "#eeeeee"
FONT = ("Tahoma","15")
FONT2 = ("Tahoma", "8")

# name, color, altitude
layers = np.array([
    ["blue1", (22, 156, 233), -10],
    ["blue2", (45, 166, 235), -5],
    ["blue3", (68, 176, 238), 0],
    ["beach", (244, 218, 138), 3],
    ["green0", (181, 202, 116), 6],
    ["green1", (116, 186, 94), 25],
    ["green2", (80, 143, 61), 35],
    ["green3", (50, 89, 38), 42],
    ["grey1", (58, 29, 19), 46],
    ["grey2", (92, 61, 61), 52],
    ["snow", (245, 240, 240), 255]
])

class Generator:
    def __init__(self):
        pass

    @timing
    def get_random_noise(self, scale, shape, octaves, persistence, lacunarity, seed=False):
        scale = shape[1] * (scale / 100)
        world = np.zeros(shape)
        if seed == False or seed <= 0: seed = np.random.randint(1,100)
        for i in range(shape[0]):
            for j in range(shape[1]):
                world[i][j] = noise.pnoise2(i / scale, j / scale,
                                            octaves=octaves,
                                            persistence=persistence,
                                            lacunarity=lacunarity,
                                            base=seed)
        return ((world + 1) * 128).astype(np.uint8)
    @timing
    def assign_colors(self, layers, noise_array, sea_level=120):
        altitudes = (layers[:, 2] + sea_level).astype(int)
        colors = np.array([np.array([*color], dtype=np.uint8) for color in layers[:, 1]])
        color_indices = np.digitize(noise_array, altitudes)
        color_array = np.array([colors[ind] for ind in color_indices])
        return color_array
    @timing
    def array_to_image(self,color_world):
        return fromarray(color_world, mode="RGB")

class App:
    def __init__(self, master, stg):
        self.stg = stg
        self.master = master

        self.stg["shape"] = (self.master.winfo_screenheight()//2,self.master.winfo_screenheight()//2)

        self.master.resizable(0,0)
        self.master.geometry(str(self.stg["shape"][1]) + "x" + str(str(self.stg["shape"][0])))

        self.gen = Generator()

        self.image = None
        self.tk_image = None
        self.bg_label = Label(self.master, background="white", image=self.tk_image)

        self.frm = {}
        self.lbl = {}
        self.wid = {}

        self.wid["generate"] = Button(self.master, text="Generate", font=FONT, bg=WHT, activebackground=WHT, relief=SOLID,command=self.generate)

        self.frm["seed"] = Frame(self.master, bg=WHT, relief=SOLID, bd=1)
        self.lbl["seed"] = Label(self.frm["seed"], text="Seed (0 if random)", font=FONT2, bg=WHT)
        self.wid["seed"] = Spinbox(self.frm["seed"], width=4, from_=1, to=100, bg=WHT, relief=SOLID)

        self.frm["octaves"] = Frame(self.master, bg=WHT, relief=SOLID, bd=1)
        self.lbl["octaves"] = Label(self.frm["octaves"], text="Octaves", font=FONT2, bg=WHT)
        self.wid["octaves"] = Spinbox(self.frm["octaves"], width=4, from_=1, to=15, bg=WHT, relief=SOLID)

        self.frm["scale"] = Frame(self.master, bg=WHT, relief=SOLID, bd=1)
        self.lbl["scale"] = Label(self.frm["scale"], text="Scale", font=FONT2, bg=WHT)
        self.wid["scale"] = Spinbox(self.frm["scale"], width=4, from_=1, to=100, bg=WHT, relief=SOLID)

        for name in self.frm:
            self.wid[name].delete(0,"end")
            self.wid[name].insert(0,self.stg[name])
        self.draw()
        self.generate()

    def get_inputs(self):
        for name in self.frm:
            self.stg[name] = int(self.wid[name].get())

    def generate(self):
        self.get_inputs()

        noise_array = self.gen.get_random_noise(
            self.stg["scale"], self.stg["shape"], self.stg["octaves"], self.stg["persistence"], self.stg["lacunarity"],
            seed=self.stg["seed"]
        )
        color_array = self.gen.assign_colors(layers, noise_array, 120)

        self.image = self.gen.array_to_image(color_array)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.bg_label.config(image=self.tk_image)
        #image.show()

    def draw(self):
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.wid["generate"].pack(anchor=NE, padx=15, pady=15)

        for name in self.frm:
            self.frm[name].pack(anchor=NE,padx=15,pady=5)
            self.lbl[name].pack(side=LEFT, padx=5)
            self.wid[name].pack(side=LEFT, padx=5)


stg = {
    "seed" : False,
    "sea_level": 120, # altitude
    "shape" : (500, 500), # resolution
    "scale" : 45,
    "octaves" : 6,
    "persistence" : 0.55,
    "lacunarity" : 2
}

root = Tk()
app = App(root, stg)
root.mainloop()
