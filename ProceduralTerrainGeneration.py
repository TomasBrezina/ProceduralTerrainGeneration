from tkinter import *
from tkinter.filedialog import asksaveasfilename,asksaveasfile
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


class Generator:
    def __init__(self):
        pass

    def get_random_noise(self, scale, shape, octaves, persistence, lacunarity, seed=False):
        scale = shape[1] * (scale / 100)
        persistence /= 100
        lacunarity /= 10
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

    def assign_colors(self, layers, noise_array, sea_level):
        altitudes = (layers[:, 2] + sea_level).astype(int)
        colors = np.array([np.array([*color], dtype=np.uint8) for color in layers[:, 1]])
        color_indices = np.digitize(noise_array, altitudes)
        color_array = np.array([colors[ind] for ind in color_indices])
        return color_array

    def array_to_image(self,color_world):
        return fromarray(color_world, mode="RGB")

class App:
    def __init__(self, master, stg, layers):
        self.master = master
        self.stg = stg
        self.layers = layers

        self.gen = Generator()

        height,width = self.master.winfo_screenheight(),self.master.winfo_screenwidth()
        # default, min, max
        self.stg["height"] = [height//2, height//10, height]
        self.stg["width"] = [height//2, height//10, width]

        self.master.resizable(0,0)
        self.master.geometry(str(self.stg["width"][0]) + "x" + str(self.stg["height"][0]))

        self.show = True

        self.image = None
        self.tk_image = None
        self.bg_label = Label(self.master, background="white", image=self.tk_image)

        self.frm = {}
        self.lbl = {}
        self.wid = {}

        self.wid["generate"] = Button(self.master, text="Generate", font=FONT, bg=WHT, activebackground=WHT, relief=SOLID,command=self.generate)
        self.wid["show"] = Button(self.master, text="Show settings", font=FONT2, bg=WHT, activebackground=WHT, relief=SOLID,command=self.show_frames)
        self.wid["save"] = Button(self.master, text="Save image", font=FONT2, bg=WHT, activebackground=WHT, relief=SOLID,command=self.save)


        for key in self.stg:
            sub_stg = self.stg[key]
            if len(sub_stg) == 3:
                self.frm[key] = Frame(self.master, bg=WHT, relief=SOLID, bd=1)
                self.lbl[key] = Label(self.frm[key], text=key, font=FONT2, bg=WHT)
                self.wid[key] = Spinbox(self.frm[key], width=4, from_=sub_stg[1], to=sub_stg[2], bg=WHT, relief=SOLID)
        self.default_settings()

        self.lbl["seed"].config(text="seed [0=rand]")

        self.draw()
        self.generate()

    def get_inputs(self):
        for key in self.frm:
            value = int(self.wid[key].get())
            if value < self.stg[key][1]: value = self.stg[key][1] #min
            elif value > self.stg[key][2]: value = self.stg[key][2]  # min
            self.stg[key][0] = value
            self.wid[key].delete(0, "end")
            self.wid[key].insert(0, self.stg[key][0])

    def default_settings(self):
        for key in self.frm:
            self.wid[key].delete(0, "end")
            self.wid[key].insert(0, self.stg[key][0])

    @timing
    def generate(self):
        self.get_inputs()

        noise_array = self.gen.get_random_noise(
            self.stg["scale"][0], (self.stg["height"][0], self.stg["width"][0]), self.stg["octaves"][0], self.stg["persistence"][0], self.stg["lacunarity"][0],
            seed=self.stg["seed"][0]
        )
        color_array = self.gen.assign_colors(layers, noise_array, self.stg["sea_level"][0])

        self.image = self.gen.array_to_image(color_array)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.bg_label.config(image=self.tk_image)

        self.master.geometry(str(self.stg["width"][0]) + "x" + str(self.stg["height"][0]))


    def draw(self):
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.wid["generate"].pack(anchor=NE, padx=15, pady=15)
        self.wid["save"].pack(anchor=NE, padx=15, pady=5)
        self.wid["show"].pack(anchor=NE, padx=15, pady=5)

        for name in self.frm:
            self.lbl[name].pack(side=LEFT, padx=2)
            self.wid[name].pack(side=LEFT, padx=2)
        self.show_frames()

    def show_frames(self):
        if self.show:
            for key in self.frm:
                self.frm[key].pack(anchor=NE, padx=15, pady=2)
            self.show = False
            self.wid["show"].config(text="Hide settings")
        else:
            for key in self.frm:
                self.frm[key].pack_forget()
            self.show = True
            self.wid["show"].config(text="Show settings")

    def save(self):
        dir = asksaveasfilename(
            title="Save your terrain"
        )
        if dir:
            self.image.save(dir+".png")

# (default, min, max)
stg = {
    "height": [0, 0, 0],  # resolution
    "width": [0, 0, 0], # resolution

    "seed" : [0, 0, 100], # 0 is random
    "sea_level": [120, 1, 200], # altitude
    "scale" : [45, 1, 100],
    "octaves" : [6, 1, 15],
    "persistence" : [55, 1, 100],
    "lacunarity" : [20, 1, 100]
}

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

root = Tk()
app = App(root, stg, layers)
root.mainloop()
