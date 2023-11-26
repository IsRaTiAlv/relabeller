from skimage import measure
import numpy as np


class save_annotations:

    def __init__(self):
        pass

    def masks_to_json(self, masks, labels, poly_rate=1):
        shapes = []
        groups = 0
        for i, label in enumerate(labels):
            contours = measure.find_contours(masks[i], 0)
            print(len(contours))
            if len(contours) > 1:
                for contour in contours:
                    polygons = np.flip(contour, axis=1)
                    points = polygons[::poly_rate]
                    points = list(map(tuple, points.astype('float')))
                    instance = {
                        'label': label,
                        'points': points,
                        'group_id': groups,
                        'shape_type': 'polygon',
                        'flags': {}
                    }
                    shapes.append(instance)
                groups += 1
            else:
                polygons = np.flip(contours[0], axis=1)
                points = polygons[::poly_rate]
                points = list(map(tuple, points.astype('float')))
                instance = {
                    'label': label,
                    'points': points,
                    'group_id': None,
                    'shape_type': 'polygon',
                    'flags': {}
                }
                shapes.append(instance)
        return shapes

    def bbox_inference(self, img_path):
        # im = cv2.imread("/home/israel/repos/labelme/examples/test/gait1.jpg")
        _, pred_boxes, labels = self.get_prediction(img_path, 0.5)
        # masks = outputs['instances'].pred_masks.to('cpu').numpy()
        # labels = outputs['instances'].pred_classes.to('cpu').numpy()
        shapes = []
        for i, label in enumerate(labels):
            # _, _, polygons = binary_mask_to_polygon(masks[i], 0)
            instance = {
                'label':
                    label,
                'points':
                    list(([list(map(float, pred_boxes[i][0])),
                           list(map(float, pred_boxes[i][1]))])),
                'group_id':
                    None,
                'shape_type':
                    'rectangle',
                'flags': {}
            }
            shapes.append(instance)
        return shapes

    def class_inference(self, img_path):
        # im = cv2.imread("/home/israel/repos/labelme/examples/test/gait1.jpg")
        _, _, labels = self.get_prediction(img_path, 0.5)
        # masks = outputs['instances'].pred_masks.to('cpu').numpy()
        # labels = outputs['instances'].pred_classes.to('cpu').numpy()
        flags = {}
        for i, name in enumerate(self.class_names):
            flags.update({name: True if labels[0] == name else False})
        return flags
