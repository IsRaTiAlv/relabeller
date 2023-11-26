import colorsys
import numpy as np
from PIL import Image, ImageDraw
# import matplotlib.pyplot as plt
from PyQt5.QtGui import QImage
from numpy.lib.type_check import imag

from sklearn.cluster import KMeans
from skimage.util import img_as_ubyte
from skimage.morphology import erosion, dilation, disk
from skimage import measure
from skimage.transform import rescale, resize, downscale_local_mean

import scipy.ndimage as ndimage
from models.predict_custom import custom_model


class map_image():

    def __init__(self, img_path, viewer):
        # args img_path = Image's path
        self.pil_image = Image.open(img_path)
        if self.pil_image.mode == "L":
            rgbimg = Image.new("RGB", self.pil_image.size)
            rgbimg.paste(self.pil_image)
            self.pil_image = rgbimg
        self.array_image = np.array(self.pil_image)
        self.width, self.height = self.pil_image.size
        self.screenw, self.screenh = viewer.width(), viewer.height()
        self.masks = []
        self.colors = None
        self.mask_items = None
        self.segments = None
        self.class_names = []
        self.masks_record = []
        self.record = {}
        self.channel = -1
        self.mask_roi = None
        self.coord = None
        self.flip_roi_status = True
        # Variables to set up the masking threshold
        self.alpha = 0.3  # all channels but current threshold
        self.alpha_ = 0.5  # current channel threshold
        self.base_alpha = 0.3
        self.base_alpha_ = 0.5
        self.base_colors = self.random_colors(8)
        # Variables to speed up labeling of large and several masks
        self.first_mask = False
        self.preview = None

    def clear(self):
        '''  Clears the masks and class' names record  '''
        self.masks = []
        self.class_names = []

    def array2pix(self, array):
        '''  Convert an array to pixmap  '''
        height, width, channel = array.shape
        bytesPerLine = 3 * width
        pixmap = QImage(array.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return pixmap

    def pix2array(self, pixmap):
        '''  Converts a QImage into an opencv MAT format  '''
        incomingImage = pixmap.toImage()
        incomingImage = incomingImage.convertToFormat(QImage.Format.Format_RGB32)

        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)
        return arr

    def random_colors(self, N, bright=True):
        """
        Generate random colors.
        To get visually distinct colors, generate them in HSV space then
        convert to RGB.
        """
        brightness = 1.0 if bright else 0.7
        hsv = [(i / N, 1, brightness) for i in range(N)]
        colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
        # random.shuffle(colors)
        return colors

    def apply_mask(self, image, mask, color, alpha=0.5):
        """Apply the given mask to the image"""
        for c in range(3):
            image[:, :,
                  c] = np.where(mask == 1, image[:, :, c] * (1 - alpha) + alpha * color[c] * 255,
                                image[:, :, c])
        return image

    def mask_all_channels_but_current(self):
        masked_image = self.array_image.copy()
        # print(self.mask_items)
        if self.mask_items is not None:
            for i in self.mask_items:
                if not self.channel == i:
                    masked_image = self.apply_mask(masked_image, self.masks[i], self.colors[i],
                                                   self.alpha)
        return masked_image

    def mask_current_channels(self, masked_image):
        # print(self.mask_items)
        if self.mask_items is not None:
            masked_image = self.apply_mask(masked_image, self.masks[self.channel],
                                           self.colors[self.channel], self.alpha_)
        return masked_image

    def apply_masks_to_image(self, keep_last=False):
        if keep_last:
            if self.first_mask:
                # drawing all channels but the current
                self.preview = self.mask_all_channels_but_current()
                masked_image = self.mask_current_channels(self.preview.copy())
                self.first_mask = False
            else:
                masked_image = self.mask_current_channels(self.preview.copy())
        else:
            masked_image = self.array_image.copy()
            if self.mask_items is not None:
                for i in self.mask_items:
                    alpha_color = self.alpha_ if self.channel == i else self.alpha
                    masked_image = self.apply_mask(masked_image, self.masks[i], self.colors[i],
                                                   alpha_color)
        return masked_image

    def circle(self, draw, center, radius, fill):
        self.draw.ellipse((center[0] - radius + 1, center[1] - radius + 1, center[0] + radius - 1,
                           center[1] + radius - 1),
                          fill=fill,
                          outline=None)

    def drawMask(self, QP1, QP2, width, mode):
        factor = 0.5 / ((self.width / self.screenw + self.height / self.screenh) / 2)
        width = int(width // factor) + 1
        img = Image.fromarray(self.masks[self.channel].astype('uint8'))
        P1 = QP1.x(), QP1.y()
        P2 = QP2.x(), QP2.y()
        self.draw = ImageDraw.Draw(img)
        self.draw.line(P1 + P2, fill=mode, width=width)
        self.circle(self.draw, P1, width / 2, mode)
        self.circle(self.draw, P2, width / 2, mode)

        if mode == 0:
            self.masks[self.channel] = np.logical_and(self.masks[self.channel], np.array(img))
        else:
            self.masks[self.channel] = np.logical_or(self.masks[self.channel], np.array(img))

    def drawPixel(self, QP, mode):
        # print(mode)
        # img = Image.fromarray(self.masks[self.channel].astype('uint8'))
        x, y = QP.x(), QP.y()
        x = min(max(0, x), self.width - 1)
        y = min(max(0, y), self.height - 1)
        id_segment = self.segments[y, x]
        # print(id_segment, self.masks.shape, self.channel)
        mask_segment = (self.segments == id_segment)
        # plt.imshow(mask_segment)
        # plt.show()
        # print(mask_segment)
        # print(self.masks[self.channel])
        if mode:
            self.masks[self.channel] = np.logical_or(self.masks[self.channel], mask_segment)
        else:
            # self.masks[self.channel] = np.logical_xor(self.masks[self.channel], mask_segment)
            points = np.where(mask_segment)
            channelchange = self.masks[self.channel]
            channelchange[points] = False
            self.masks[self.channel] = channelchange

    def generate_mask(self, mask_items=None):
        # img = Image.open(img_path)
        # img = np.array(img)
        self.mask_items = mask_items
        if self.mask_items is None:
            if self.masks.shape[0] <= 8:
                self.colors = self.base_colors[:self.masks.shape[0]]
            else:
                self.colors = self.random_colors(self.masks.shape[0])
        # masks[0] += np.array(img_mask)
        masked_image = self.array_image.copy()
        if mask_items is None:
            for i, color in enumerate(self.colors):
                masked_image = self.apply_mask(masked_image, self.masks[i], color, self.alpha)
        elif mask_items != []:
            for i in mask_items:
                masked_image = self.apply_mask(masked_image, self.masks[i], self.colors[i],
                                               (self.alpha_ if self.channel == i else self.alpha))
        # Image.fromarray(masked_image).save('mask.jpg')
        return masked_image

    def roi_prediction(self, roi):
        # print(roi.shape)
        img = roi / 255
        scale = False
        if img.shape[0]<15:
            img = resize(img, (img.shape[0] * 2, img.shape[1] * 2), anti_aliasing=True)
            scale = True
        image_2D = img.reshape(img.shape[0] * img.shape[1], img.shape[2])
        kmeans = KMeans(n_clusters=2, random_state=0).fit(image_2D)
        clustered = kmeans.cluster_centers_[kmeans.labels_]
        clustered_3D = clustered.reshape(img.shape[0], img.shape[1], img.shape[2])
        gray = img_as_ubyte(clustered_3D[:, :, 0])
        eroded = erosion(gray, disk(2))
        dilated = dilation(eroded, disk(3))
        mean = int((int(dilated.max()) + int(dilated.min())) / 2)
        mask = np.where(dilated > mean, 0, 1)
        if scale:
            mask = resize(mask, (mask.shape[0] / 2, mask.shape[1] / 2), anti_aliasing=True)
        return mask.astype('bool')

    def patch_prediction(self, array):
        model = custom_model(
            "models/grasspatch80_80YCbCr_3aa5d61c-1a0c-11ec-8c45-0c9d92c51afe.onnx")
        imagerino = Image.fromarray(array)
        # imagerino.save("/home/PIB1TI/Desktop/patch.png")
        array_yuv = imagerino.convert("YCbCr")
        result_mask = model.array_prediction(np.asarray(array_yuv))
        return result_mask

    def generate_roi(self, origin, end):
        P1 = origin.x(), origin.y()
        P2 = end.x(), end.y()
        # print(P1[0], P1[1])
        # print(self.masks[channel][int(P1[0]), int(P1[1])])
        h0, h1 = (int(P1[0]), int(P2[0])) if P1[0] < P2[0] else (int(P2[0]), int(P1[0]))
        w0, w1 = (int(P1[1]), int(P2[1])) if P1[1] < P2[1] else (int(P2[1]), int(P1[1]))
        h0 = 0 if h0 < 0 else h0
        h1 = self.width if h1 > self.width else h1
        w0 = 0 if w0 < 0 else w0
        w1 = self.height if w1 > self.height else w1
        self.coord = (w0, w1, h0, h1, self.channel)
        # self.mask_roi = self.patch_prediction(self.array_image[w0:w1, h0:h1, :])
        # self.masks[self.channel][w0:w1, h0:h1] = self.mask_roi
        # Second Option down
        self.mask_roi = self.roi_prediction(self.array_image[w0:w1, h0:h1, :])
        self.masks[self.channel][w0:w1, h0:h1] = self.mask_roi

    def close(self):

        blobs = measure.label(self.masks[self.channel], background=0)

        if blobs.max() > 1:
            biggest_blob = None
            biggest_blob_size = 0
            for i in range(1, blobs.max()):
                if np.sum(blobs == i) > biggest_blob_size:
                    biggest_blob = blobs == i
                    biggest_blob_size = np.sum(blobs == i)
        else:
            biggest_blob = blobs

        padded = np.pad(biggest_blob, [10, 10], 'constant')
        contours = measure.find_contours(padded, 0.8)
        contour = contours[0]

        r_mask = np.zeros_like(padded, dtype='bool')
        r_mask[np.round(contour[:, 0]).astype('int'), np.round(contour[:, 1]).astype('int')] = 1
        r_mask = ndimage.binary_fill_holes(r_mask)
        h, w = r_mask.shape
        self.masks[self.channel] = r_mask[10:h - 10, 10:w - 10]

    def flip_roi_mask(self):
        (w0, w1, h0, h1, channel) = self.coord
        if self.flip_roi_status:
            self.masks[channel][w0:w1, h0:h1] = np.invert(self.mask_roi)
            self.flip_roi_status = False
        else:
            self.masks[channel][w0:w1, h0:h1] = self.mask_roi
            self.flip_roi_status = True

    def do_action(self):
        # if delete:
        #     self.record = (self.masks.copy(), self.colors.copy(), self.class_names.copy())
        # else:
        #     self.record = (self.masks.copy(), self.colors.copy(), self.class_names.copy())
        if self.colors is not None:
            self.record = (self.masks.copy(), self.colors.copy(), self.class_names.copy())
        else:
            self.record = (None, None, None)
        self.masks_record.append(self.record)

    def undo_action(self):
        data = self.masks_record.pop(-1)
        self.masks, self.colors, self.class_names = data
