from PIL import ImageTk, Image
from functools import lru_cache
import time

class ImageLoader():

    def default_image(self, w, h, color=(0, 0, 0, 255)):
        return ImageTk.PhotoImage(Image.new(mode="RGBA", size=(int(w), int(h)), color=color))

    @lru_cache(maxsize=32)
    def load_resized_landscape(self, path, w):
        print("Cache miss, loading", path)
        original = Image.open(path)
        original_w, original_h = original.size
        ar = original_h/original_w
        if original_h > original_w:
            resized = original.rotate(90, expand=True).resize((int(w), int(w/ar)))
        else:
            resized = original.resize((int(w), int(ar*w)))
        return ImageTk.PhotoImage(resized)

    @lru_cache(maxsize=32)
    def load_resized(self, path, h):
        print("Cache miss, loading", path)
        original = Image.open(path)
        original_w, original_h = original.size
        ar = original_h/original_w
        resized = original.resize((int(h/ar), int(h)))
        return ImageTk.PhotoImage(resized)