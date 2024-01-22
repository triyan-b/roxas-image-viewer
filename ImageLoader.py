from PIL import ImageTk, Image
from functools import lru_cache

class ImageLoader():

    def default_image(self, w, h, color=(0, 0, 0, 255)):
        return ImageTk.PhotoImage(Image.new(mode="RGBA", size=(int(w), int(h)), color=color))

    @lru_cache(maxsize=32)
    def load_resized_landscape(self, path, w, max_h=None):
        print("Cache miss, loading", path)
        original = Image.open(path)
        original_w, original_h = original.size
        ar = original_h/original_w
        if original_h > original_w:
            new_h = min(int(w/ar), max_h) if max_h else int(w/ar)
            new_w = int(new_h*ar)
            resized = original.rotate(90, expand=True).resize((new_w, new_h))
        else:
            new_h = min(int(w*ar), max_h) if max_h else int(w*ar)
            new_w = int(new_h/ar)
            resized = original.resize((new_w, new_h))
        return ImageTk.PhotoImage(resized)

    @lru_cache(maxsize=32)
    def load_resized(self, path, h, max_w=None):
        print("Cache miss, loading", path)
        original = Image.open(path)
        original_w, original_h = original.size
        ar = original_h/original_w
        new_w = min(int(h/ar), max_w) if max_w else int(h/ar)
        new_h = int(new_w*ar)
        resized = original.resize((new_w, new_h))
        return ImageTk.PhotoImage(resized)