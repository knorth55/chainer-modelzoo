import chainer
import chainer.functions as F
import chainer.links as L


class AlexNet(chainer.Chain):

    insize = 227

    def __init__(self):
        super(AlexNet, self).__init__(
            conv1=L.Convolution2D(3,  96, 11, stride=4),
            conv2=L.Convolution2D(96, 256,  5, pad=2),
            conv3=L.Convolution2D(256, 384,  3, pad=1),
            conv4=L.Convolution2D(384, 384,  3, pad=1),
            conv5=L.Convolution2D(384, 256,  3, pad=1),
            fc6=L.Linear(256 * 6 * 6, 4096),
            fc7=L.Linear(4096, 4096),
            fc8=L.Linear(4096, 1000),
        )
        self.train = False

    def __call__(self, x, t=None):
        h = F.max_pooling_2d(F.relu(
            F.local_response_normalization(self.conv1(x))), 3, stride=2)
        h = F.max_pooling_2d(F.relu(
            F.local_response_normalization(self.conv2(h))), 3, stride=2)
        h = F.relu(self.conv3(h))
        h = F.relu(self.conv4(h))
        h = F.max_pooling_2d(F.relu(self.conv5(h)), 3, stride=2)
        h = F.dropout(F.relu(self.fc6(h)), train=self.train)
        h = F.dropout(F.relu(self.fc7(h)), train=self.train)
        h = self.fc8(h)
        self.score = h

        if t is None:
            assert not self.train
            return

        self.loss = F.softmax_cross_entropy(self.score, t)
        self.accuracy = F.accuracy(self.score, t)
        chainer.report({'loss': self.loss, 'accuracy': self.accuracy})

        return self.loss
