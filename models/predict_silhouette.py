from PIL import Image
import numpy as np


class person_model:

    def __init__(self):
        # Specify a path
        self.PATH = './masks/'
        self.class_names = ['Person']

    def image_prediction(self, img_path):
        path = img_path.split('/')
        path[-2] = 'masks'
        self.mask_path = ('/').join(path)
        image = Image.open(self.mask_path)
        # print(predictions.shape)
        return np.array(image)[np.newaxis].astype('bool'), None, self.class_names
