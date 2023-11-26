import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from skimage.data import astronaut
from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import felzenszwalb, slic, quickshift, watershed
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float


class superpixel_model:

    def __init__(self):
        # Specify a path
        self.PATH = './masks/'
        self.class_names = ['Person']

    def slic_prediction(self, img_path, segments=200, compact=20, sig=1):
        image = Image.open(img_path)
        img = np.array(image)
        segments = slic(img, n_segments=segments, compactness=compact, sigma=sig, start_label=1)
        marked = mark_boundaries(img, segments)
        # print(predictions.shape)
        return segments, (marked * 255).astype('uint8')
