from PIL import Image

import logging
import numpy as np
import onnxruntime as rt

import utils.misc as utils
from skimage.transform import resize


class custom_model:

    def __init__(self, onnx_network):
        self.logger = logging.getLogger(__name__)
        # Specify a path
        self.class_names = ['grass']
        so = rt.SessionOptions()
        so.log_verbosity_level = 3  # 0:Verbose, 1:Info, 2:Warning. 3:Error, 4:Fatal. Default is 2.
        so.log_severity_level = 3
        self.sess = rt.InferenceSession(onnx_network, sess_options=so)
        self.network_input_width = self.sess.get_inputs()[0].shape[3]
        self.network_input_height = self.sess.get_inputs()[0].shape[2]
        self.threshold = 0.7
        self.input = 'YCbCr'
        self.output = 'masks[ndarray], None, pred_class[list]'
        self.model_name = 'Custom'
        self.description = 'Custom model trained to segment grass'

    def getInfo(self):
        self.info = {
            'name': self.model_name,
            'input': self.input,
            'output': self.output,
            'classes': self.class_names,
            'threshold': str(self.threshold),
            'description': self.description
        }
        return self.info

    def array_prediction(self, array):
        resized_array = resize(array, (self.network_input_width, self.network_input_height),
                               preserve_range=True)
        resized_array = np.moveaxis(np.asarray(resized_array), -1, 0)
        img_array = np.expand_dims(resized_array, axis=0) / 255
        input_name = self.sess.get_inputs()[0].name
        pred_onx = self.sess.run(None, {input_name: img_array.astype(np.float32)})[0]
        pred_onx = np.argmax(pred_onx[0], axis=0)
        pred_onx = resize(pred_onx, (array.shape[0], array.shape[1]), preserve_range=True)
        return pred_onx.astype('bool')

    def image_prediction(self, img_path):
        img = Image.open(img_path)
        img_size = img.size
        if img_size != (self.network_input_width, self.network_input_height):
            self.logger.info("Resizing input image to fit network.")
            img = utils.resize_input_image(img, self.network_input_width, self.network_input_height)
        ycbcr = img.convert('YCbCr')
        ycbcr = np.moveaxis(np.asarray(ycbcr), -1, 0)
        img_array = np.expand_dims(ycbcr, axis=0) / 255
        input_name = self.sess.get_inputs()[0].name
        pred_onx = self.sess.run(None, {input_name: img_array.astype(np.float32)})[0]
        pred_onx = np.argmax(pred_onx[0], axis=0)
        # Using pytorch format, dimensions might need refactor
        pred_onx = np.expand_dims(pred_onx, axis=0)
        # This part is needed to rescale the mask back to original size, could use
        # a simpler approach later
        if img_size != (pred_onx[0].shape[1], pred_onx[0].shape[0]):
            image_mask = Image.fromarray(np.uint8(pred_onx[0] * 255), 'L')
            image_mask = image_mask.resize(img_size)
            pred_onx = np.asarray(image_mask) / 255
            pred_onx = np.expand_dims(pred_onx, axis=0)

        return pred_onx.astype('bool'), None, self.class_names
