#!/usr/bin/env python

import chainer
import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import scipy.misc
import skimage.color

from download import IMAGE_PATH
from download import MODEL_PATH
from model import FCN8s


LABEL_NAMES = [
    'background',
    'aeroplane',
    'bicycle',
    'bird',
    'boat',
    'bottle',
    'bus',
    'car',
    'cat',
    'chair',
    'cow',
    'diningtable',
    'dog',
    'horse',
    'motorbike',
    'person',
    'potted plant',
    'sheep',
    'sofa',
    'train',
    'tv/monitor',
]


def main():
    # load model
    model = FCN8s()
    print('Loading pretrained model from {0}'.format(MODEL_PATH))
    chainer.serializers.load_hdf5(MODEL_PATH, model)

    # prepare net input

    print('Loading image from {0}'.format(IMAGE_PATH))
    img = scipy.misc.imread(IMAGE_PATH, mode='RGB')
    img_in = img.copy()

    img = img[:, :, ::-1]  # RGB -> BGR
    img = img.astype(np.float32)
    mean_bgr = np.array([104, 117, 123], dtype=np.float32)
    img -= mean_bgr

    x_data = np.array([img.transpose(2, 0, 1)])
    x = chainer.Variable(x_data, volatile='ON')

    # infer
    model(x)
    score = model.score.data[0]

    # visualize result

    label = np.argmax(score, axis=0)
    n_labels = score.shape[0]
    colormap = matplotlib.cm.Set1(np.linspace(0, 1, n_labels-1))[:, :3]
    colormap = np.vstack(([0, 0, 0], colormap))  # bg color
    label_viz = skimage.color.label2rgb(label, colors=colormap[1:], bg_label=0)

    # network input
    plt.subplot(211)
    plt.imshow(img_in)
    plt.axis('off')

    # network output
    plt.subplot(212)
    plt.imshow(label_viz)
    plt.axis('off')
    plt_handlers = []
    plt_titles = []
    for label_value in np.unique(label):
        if (label == label_value).sum() < 0.01 * label.size:
            continue  # skip small region
        fc = colormap[label_value]
        p = plt.Rectangle((0, 0), 1, 1, fc=fc)
        plt_handlers.append(p)
        plt_titles.append(LABEL_NAMES[label_value])
    plt.legend(plt_handlers, plt_titles, loc='upper right',
               framealpha=0.5)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
