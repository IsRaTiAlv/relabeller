from PIL import Image, ImageEnhance, ImageDraw
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, QSize
import numpy as np
import colorsys
import os
import json
from pycocotools import mask
from random import random
from itertools import groupby


def resize_input_image(image, width, height):
    # This is a function because functionality will evolve in the future
    # for better resizing, like padding or better interpolation, superscaling,
    # smarter downscaling
    image = image.resize((width, height))
    return image


def brightness(img_path, factor):
    im = Image.open(img_path)
    enhancer = ImageEnhance.Brightness(im)
    output = enhancer.enhance(factor)
    return output


def rand_color():
    h, s, le = random(), 0.5 + random() / 2.0, 0.4 + random() / 5.0
    r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, le, s)]
    return r, g, b


def ndarray2Pixmap(ndarray):
    pil_image = Image.fromarray(ndarray)
    qim = ImageQt(pil_image)
    return QPixmap.fromImage(qim)


def PIL2Pixmap(pil_image):
    qim = ImageQt(pil_image)
    return QPixmap.fromImage(qim)


def cursor(mode, size, color):
    icon_size = 120
    scale = 3
    r, g, b = [int(c * 255) for c in color]
    if mode == 'pen':
        icon = Image.open('icons/pen.png')
    elif mode == 'eraser':
        icon = Image.open('icons/eraser.png')
    elif mode == 'fill':
        icon = Image.open('icons/fill.png')
    elif mode == 'unfill':
        icon = Image.open('icons/clear.png')
    image = Image.new('RGBA', (icon_size, icon_size))
    draw = ImageDraw.Draw(image)
    # draw.ellipse((20, 180, 180, 20), fill = 'blue', outline ='blue')
    draw.ellipse((0, int(icon_size* (1/ 3)), int(icon_size* (2/ 3)), icon_size), fill=(r, g, b, 180), outline='white')
    image.paste(icon, (int(icon_size* (1/ 2)), 0), icon)
    pix_image = PIL2Pixmap(image)
    Csize = QSize(size * scale, size * scale)
    cursor = pix_image.scaled(Csize, Qt.KeepAspectRatio)
    cursor = QCursor(cursor, size, size * 2)
    return cursor


def mask2rle(binary_mask):
    rle = {'counts': [], 'size': list(binary_mask.shape)}
    counts = rle.get('counts')
    for i, (value, elements) in enumerate(groupby(binary_mask.ravel(order='F'))):
        if i == 0 and value == 1:
            counts.append(0)
        counts.append(len(list(elements)))
    return rle


def rle2mask(rle):
    compressed_rle = mask.frPyObjects(rle, rle.get('size')[0], rle.get('size')[1])
    return mask.decode(compressed_rle)


def pathpng2json(path):
    path_list = path.split('/')
    path_list[-1] = path_list[-1].split('.')[0] + '.json'
    return "/" + os.path.join(*path_list)


def random_colors(N, bright=True):
    """ Generate random colors """
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    # random.shuffle(colors)
    return colors


def apply_mask(image, mask, color, alpha=0.5):
    """Apply the given mask to the image"""
    for c in range(3):
        image[:, :, c] = np.where(mask == 1, image[:, :, c] * (1 - alpha) + alpha * color[c] * 255,
                                  image[:, :, c])
    return image


def generate_mask(img_path, masks):
    masked_image = np.array(Image.open(img_path))
    colors = random_colors(masks.shape[0])
    for i, color in enumerate(colors):
        masked_image = apply_mask(masked_image, masks[i], color, 0.5)
    return masked_image


def open_label(jsonname):
    # jsonname = (filename.split('/')[-1]).split('.')[0] + '.json'
    # print(jsonname)
    with open(jsonname) as json_file:
        data = json.load(json_file)
    annotations = data['annotations']
    classes = list()
    masks = list()
    for instance in annotations:
        classes.append(instance['category'])
        masks.append(rle2mask(instance['segmentation']))
    return np.array(masks), classes
