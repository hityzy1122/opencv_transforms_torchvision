from __future__ import division
import torch
import math
import random
import cv2
import numpy as np
import numbers
import types
import collections

from cvtorchvision.cvtransforms import cvfunctional as F


__all__ = ["Compose", "ToTensor", "ToCVImage",
           "Normalize", "Resize", "CenterCrop", "Pad",
           "Lambda", "RandomApply", "RandomOrder", "RandomChoice", "RandomCrop",
           "RandomHorizontalFlip", "RandomVerticalFlip", "RandomResizedCrop",
           "FiveCrop", "TenCrop", "LinearTransformation", "ColorJitter",
           "RandomRotation", "RandomAffine", "RandomAffine6", "RandomPerspective",
           "Grayscale", "RandomGrayscale",
           "RandomGaussianNoise", "RandomPoissonNoise", "RandomSPNoise"]


class Compose(object):
    """Composes several transforms together.

    Args:
        transforms (list of ``Transform`` objects): list of transforms to compose.

    Example:
        >>> transforms.Compose([
        >>>     transforms.CenterCrop(10),
        >>>     transforms.ToTensor(),
        >>> ])
    """

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img):
        for t in self.transforms:
            img = t(img)
        return img

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        for t in self.transforms:
            format_string += '\n'
            format_string += '    {0}'.format(t)
        format_string += '\n)'
        return format_string


class Lambda(object):
    """Apply a user-defined lambda as a transform.
    Attention: The multiprocessing used in dataloader of pytorch is not friendly with lambda function in Windows

    Args:
        lambd (function): Lambda/function to be used for transform.
    """

    def __init__(self, lambd):
        # assert isinstance(lambd, types.LambdaType)
        self.lambd = lambd
        # if 'Windows' in platform.system():
        #     raise RuntimeError("Can't pickle lambda funciton in windows system")

    def __call__(self, img):
        return self.lambd(img)

    def __repr__(self):
        return self.__class__.__name__ + '()'


class ToTensor(object):
    """Convert a ``numpy.ndarray`` to tensor.

    Converts a numpy.ndarray (H x W x C) in the range
    [0, 255] to a torch.FloatTensor of shape (C x H x W) in the range [0.0, 1.0].
    """

    def __call__(self, pic):
        """
        Args:
            pic (numpy.ndarray): Image to be converted to tensor.

        Returns:
            Tensor: Converted image.
        """
        return F.to_tensor(pic)

    def __repr__(self):
        return self.__class__.__name__ + '()'


class ToCVImage(object):
    """Convert a tensor or an to ndarray Image.

    Converts a torch.*Tensor of shape C x H x W or a numpy ndarray of shape
    H x W x C to a CV Image while preserving the value range.

    Args:
        mode (str): color space and pixel depth of input data (optional).
    """
    def __init__(self, mode=None):
        self.mode = mode

    def __call__(self, pic):
        """
        Args:
            pic (Tensor or numpy.ndarray): Image to be converted to PIL Image.

        Returns:
            PIL Image: Image converted to PIL Image.

        """
        return F.to_cv_image(pic, self.mode)


class Normalize(object):
    """Normalize a tensor image with mean and standard deviation.
    Given mean: ``(M1,...,Mn)`` and std: ``(S1,..,Sn)`` for ``n`` channels, this transform
    will normalize each channel of the input ``torch.*Tensor`` i.e.
    ``input[channel] = (input[channel] - mean[channel]) / std[channel]``

    Args:
        mean (sequence): Sequence of means for each channel.
        std (sequence): Sequence of standard deviations for each channel.
    """

    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, tensor):
        """
        Args:
            tensor (Tensor): Tensor image of size (C, H, W) to be normalized.

        Returns:
            Tensor: Normalized Tensor image.
        """
        return F.normalize(tensor, self.mean, self.std)

    def __repr__(self):
        return self.__class__.__name__ + '(mean={0}, std={1})'.format(self.mean, self.std)


class Resize(object):
    """Resize the input PIL Image to the given size.

    Args:
        size (sequence or int): Desired output size. If size is a sequence like
            (h, w), output size will be matched to this. If size is an int,
            smaller edge of the image will be matched to this number.
            i.e, if height > width, then image will be rescaled to
            (size * height / width, size)
        interpolation (int, optional): Desired interpolation. Default is
            ``BILINEAR``
    """

    def __init__(self, size, interpolation='BILINEAR'):
        assert isinstance(size, int) or (isinstance(size, collections.Iterable) and len(size) == 2)
        self.size = size
        self.interpolation = interpolation

    def __call__(self, img):
        """
        Args:
            img (np.ndarray): Image to be scaled.

        Returns:
            np.ndarray: Rescaled image.
        """
        return F.resize(img, self.size, self.interpolation)

    def __repr__(self):
        interpolate_str = self.interpolation
        return self.__class__.__name__ + '(size={0}, interpolation={1})'.format(self.size, interpolate_str)


class CenterCrop(object):
    """Crops the given PIL Image at the center.

    Args:
        size (sequence or int): Desired output size of the crop. If size is an
            int instead of sequence like (h, w), a square crop (size, size) is
            made.
    """

    def __init__(self, size):

        self.size = size

    def __call__(self, img):
        """
        Args:
            img (CV Image): Image to be cropped.

        Returns:
            CV Image: Cropped image.
        """
        return F.center_crop(img, self.size)

    def __repr__(self):
        return self.__class__.__name__ + '(size={0})'.format(self.size)


class Pad(object):
    """Pad the given CV Image on all sides with the given "pad" value.

    Args:
        padding (int or tuple): Padding on each border. If a single int is provided this
            is used to pad all borders. If tuple of length 2 is provided this is the padding
            on left/right and top/bottom respectively. If a tuple of length 4 is provided
            this is the padding for the left, top, right and bottom borders
            respectively.
        fill: Pixel fill value for constant fill. Default is 0. If a tuple of
            length 3, it is used to fill R, G, B channels respectively.
            This value is only used when the padding_mode is constant
        padding_mode: Type of padding. Should be: constant, edge, reflect or symmetric. Default is constant.
            constant: pads with a constant value, this value is specified with fill
            edge: pads with the last value at the edge of the image
            reflect: pads with reflection of image (without repeating the last value on the edge)
                padding [1, 2, 3, 4] with 2 elements on both sides in reflect mode
                will result in [3, 2, 1, 2, 3, 4, 3, 2]
            symmetric: pads with reflection of image (repeating the last value on the edge)
                padding [1, 2, 3, 4] with 2 elements on both sides in symmetric mode
                will result in [2, 1, 1, 2, 3, 4, 4, 3]
    """

    def __init__(self, padding, fill=0, padding_mode='constant'):
        assert isinstance(padding, (numbers.Number, tuple))
        assert isinstance(fill, (numbers.Number, str, tuple))
        assert padding_mode in ['constant', 'edge', 'reflect', 'symmetric']
        if isinstance(padding, collections.Sequence) and len(padding) not in [2, 4]:
            raise ValueError("Padding must be an int or a 2, or 4 element tuple, not a " +
                             "{} element tuple".format(len(padding)))

        self.padding = padding
        self.fill = fill
        self.padding_mode = padding_mode

    def __call__(self, img):
        """
        Args:
            img (CV Image): Image to be padded.

        Returns:
            CV Image: Padded image.
        """
        return F.pad(img, self.padding, self.fill, self.padding_mode)

    def __repr__(self):
        return self.__class__.__name__ + '(padding={0}, fill={1}, padding_mode={2})'.\
            format(self.padding, self.fill, self.padding_mode)


class RandomTransforms(object):
    """Base class for a list of transformations with randomness

    Args:
        transforms (list or tuple): list of transformations
    """

    def __init__(self, transforms):
        assert isinstance(transforms, (list, tuple))
        self.transforms = transforms

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        for t in self.transforms:
            format_string += '\n'
            format_string += '    {0}'.format(t)
        format_string += '\n)'
        return format_string


class RandomApply(RandomTransforms):
    """Apply randomly a list of transformations with a given probability

    Args:
        transforms (list or tuple): list of transformations
        p (float): probability
    """

    def __init__(self, transforms, p=0.5):
        super(RandomApply, self).__init__(transforms)
        self.p = p

    def __call__(self, img):
        if self.p < random.random():
            return img
        for t in self.transforms:
            img = t(img)
        return img

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        format_string += '\n    p={}'.format(self.p)
        for t in self.transforms:
            format_string += '\n'
            format_string += '    {0}'.format(t)
        format_string += '\n)'
        return format_string


class RandomOrder(RandomTransforms):
    """Apply a list of transformations in a random order
    """
    def __call__(self, img):
        order = list(range(len(self.transforms)))
        random.shuffle(order)
        for i in order:
            img = self.transforms[i](img)
        return img


class RandomChoice(RandomTransforms):
    """Apply single transformation randomly picked from a list
    """
    def __call__(self, img):
        t = random.choice(self.transforms)
        return t(img)


class RandomCrop(object):
    """Crop the given CV Image at a random location.

    Args:
        size (sequence or int): Desired output size of the crop. If size is an
            int instead of sequence like (h, w), a square crop (size, size) is
            made.
        padding (int or sequence, optional): Optional padding on each border
            of the image. Default is 0, i.e no padding. If a sequence of length
            4 is provided, it is used to pad left, top, right, bottom borders
            respectively.
        pad_if_needed (boolean): It will pad the image if smaller than the
            desired size to avoid raising an exception.
    """

    def __init__(self, size, padding=0, pad_if_needed=False):
        if isinstance(size, numbers.Number):
            self.size = (int(size), int(size))
        else:
            self.size = size
        self.padding = padding
        self.pad_if_needed = pad_if_needed

    @staticmethod
    def get_params(img, output_size):
        """Get parameters for ``crop`` for a random crop.

        Args:
            img (CV Image): Image to be cropped.
            output_size (tuple): Expected output size of the crop.

        Returns:
            tuple: params (i, j, h, w) to be passed to ``crop`` for random crop.
        """
        h, w, _ = img.shape
        th, tw = output_size
        if w == tw and h == th:
            return 0, 0, h, w

        try:
            i = random.randint(0, h - th)
        except ValueError:
            i = random.randint(h - th, 0)
        try:
            j = random.randint(0, w - tw)
        except ValueError:
            j = random.randint(w - tw, 0)
        return i, j, th, tw

    def __call__(self, img):
        """
        Args:
            img (np.ndarray): Image to be cropped.

        Returns:
            np.ndarray: Cropped image.
        """
        if self.padding > 0:
            img = F.pad(img, self.padding)

        # pad the width if needed
        if self.pad_if_needed and img.shape[1] < self.size[1]:
            img = F.pad(img, (int((1 + self.size[1] - img.shape[1]) / 2), 0))
        # pad the height if needed
        if self.pad_if_needed and img.shape[0] < self.size[0]:
            img = F.pad(img, (0, int((1 + self.size[0] - img.shape[0]) / 2)))

        i, j, h, w = self.get_params(img, self.size)

        return F.crop(img, i, j, h, w)

    def __repr__(self):
        return self.__class__.__name__ + '(size={0}, padding={1})'.format(self.size, self.padding)


class RandomHorizontalFlip(object):
    """Horizontally flip the given CV Image randomly with a given probability.

    Args:
        p (float): probability of the image being flipped. Default value is 0.5
    """

    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, img):
        """
        Args:
            img (CV Image): Image to be flipped.

        Returns:
            CV Image: Randomly flipped image.
        """
        if random.random() < self.p:
            return F.hflip(img)
        return img

    def __repr__(self):
        return self.__class__.__name__ + '(p={})'.format(self.p)


class RandomVerticalFlip(object):
    """Vertically flip the given CV Image randomly with a given probability.

    Args:
        p (float): probability of the image being flipped. Default value is 0.5
    """

    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, img):
        """
        Args:
            img (CV Image): Image to be flipped.

        Returns:
            CV Image: Randomly flipped image.
        """
        if random.random() < self.p:
            return F.vflip(img)
        return img

    def __repr__(self):
        return self.__class__.__name__ + '(p={})'.format(self.p)


class RandomResizedCrop(object):
    """Crop the given CV Image to random size and aspect ratio.

    A crop of random size (default: of 0.08 to 1.0) of the original size and a random
    aspect ratio (default: of 3/4 to 4/3) of the original aspect ratio is made. This crop
    is finally resized to given size.
    This is popularly used to train the Inception networks.

    Args:
        size: expected output size of each edge
        scale: range of size of the origin size cropped
        ratio: range of aspect ratio of the origin aspect ratio cropped
        interpolation: Default: BILINEAR
    """

    def __init__(self, size, scale=(0.08, 1.0), ratio=(3. / 4., 4. / 3.), interpolation='BILINEAR'):
        self.size = (size, size)
        self.interpolation = interpolation
        self.scale = scale
        self.ratio = ratio

    @staticmethod
    def get_params(img, scale, ratio):
        """Get parameters for ``crop`` for a random sized crop.

        Args:
            img (CV Image): Image to be cropped.
            scale (tuple): range of size of the origin size cropped
            ratio (tuple): range of aspect ratio of the origin aspect ratio cropped

        Returns:
            tuple: params (i, j, h, w) to be passed to ``crop`` for a random
                sized crop.
        """
        for attempt in range(10):
            area = img.shape[0] * img.shape[1]
            target_area = random.uniform(*scale) * area
            aspect_ratio = random.uniform(*ratio)

            w = int(round(math.sqrt(target_area * aspect_ratio)))
            h = int(round(math.sqrt(target_area / aspect_ratio)))

            if random.random() < 0.5:
                w, h = h, w

            if w <= img.shape[1] and h <= img.shape[0]:
                i = random.randint(0, img.shape[0] - h)
                j = random.randint(0, img.shape[1] - w)
                return i, j, h, w

        # Fallback
        w = min(img.shape[0], img.shape[1])
        i = (img.shape[0] - w) // 2
        j = (img.shape[1] - w) // 2
        return i, j, w, w

    def __call__(self, img):
        """
        Args:
            img (np.ndarray): Image to be cropped and resized.

        Returns:
            np.ndarray: Randomly cropped and resized image.
        """
        i, j, h, w = self.get_params(img, self.scale, self.ratio)
        return F.resized_crop(img, i, j, h, w, self.size, self.interpolation)

    def __repr__(self):
        interpolate_str = self.interpolation
        format_string = self.__class__.__name__ + '(size={0}'.format(self.size)
        format_string += ', scale={0}'.format(tuple(round(s, 4) for s in self.scale))
        format_string += ', ratio={0}'.format(tuple(round(r, 4) for r in self.ratio))
        format_string += ', interpolation={0})'.format(interpolate_str)
        return format_string


class FiveCrop(object):
    """Crop the given CV Image into four corners and the central crop

    .. Note::
         This transform returns a tuple of images and there may be a mismatch in the number of
         inputs and targets your Dataset returns. See below for an example of how to deal with
         this.

    Args:
         size (sequence or int): Desired output size of the crop. If size is an ``int``
            instead of sequence like (h, w), a square crop of size (size, size) is made.

    Example:
         >>> transform = Compose([
         >>>    FiveCrop(size), # this is a list of CV Images
         >>>    Lambda(lambda crops: torch.stack([ToTensor()(crop) for crop in crops])) # returns a 4D tensor
         >>> ])
         >>> #In your test loop you can do the following:
         >>> input, target = batch # input is a 5d tensor, target is 2d
         >>> bs, ncrops, c, h, w = input.size()
         >>> result = model(input.view(-1, c, h, w)) # fuse batch size and ncrops
         >>> result_avg = result.view(bs, ncrops, -1).mean(1) # avg over crops
    """

    def __init__(self, size):
        self.size = size
        if isinstance(size, numbers.Number):
            self.size = (int(size), int(size))
        else:
            assert len(size) == 2, "Please provide only two dimensions (h, w) for size."
            self.size = size

    def __call__(self, img):
        return F.five_crop(img, self.size)

    def __repr__(self):
        return self.__class__.__name__ + '(size={0})'.format(self.size)


class TenCrop(object):
    """Crop the given CV Image into four corners and the central crop plus the flipped version of
    these (horizontal flipping is used by default)

    .. Note::
         This transform returns a tuple of images and there may be a mismatch in the number of
         inputs and targets your Dataset returns. See below for an example of how to deal with
         this.

    Args:
        size (sequence or int): Desired output size of the crop. If size is an
            int instead of sequence like (h, w), a square crop (size, size) is
            made.
        vertical_flip(bool): Use vertical flipping instead of horizontal

    Example:
         >>> transform = Compose([
         >>>    TenCrop(size), # this is a list of PIL Images
         >>>    Lambda(lambda crops: torch.stack([ToTensor()(crop) for crop in crops])) # returns a 4D tensor
         >>> ])
         >>> #In your test loop you can do the following:
         >>> input, target = batch # input is a 5d tensor, target is 2d
         >>> bs, ncrops, c, h, w = input.size()
         >>> result = model(input.view(-1, c, h, w)) # fuse batch size and ncrops
         >>> result_avg = result.view(bs, ncrops, -1).mean(1) # avg over crops
    """

    def __init__(self, size, vertical_flip=False):
        self.size = size
        if isinstance(size, numbers.Number):
            self.size = (int(size), int(size))
        else:
            assert len(size) == 2, "Please provide only two dimensions (h, w) for size."
            self.size = size
        self.vertical_flip = vertical_flip

    def __call__(self, img):
        return F.ten_crop(img, self.size, self.vertical_flip)

    def __repr__(self):
        return self.__class__.__name__ + '(size={0}, vertical_flip={1})'.format(self.size, self.vertical_flip)


class LinearTransformation(object):
    """Transform a tensor image with a square transformation matrix computed
    offline.

    Given transformation_matrix, will flatten the torch.*Tensor, compute the dot
    product with the transformation matrix and reshape the tensor to its
    original shape.

    Applications:
    - whitening: zero-center the data, compute the data covariance matrix
                 [D x D] with np.dot(X.T, X), perform SVD on this matrix and
                 pass it as transformation_matrix.

    Args:
        transformation_matrix (Tensor): tensor [D x D], D = C x H x W
    """

    def __init__(self, transformation_matrix):
        if transformation_matrix.size(0) != transformation_matrix.size(1):
            raise ValueError("transformation_matrix should be square. Got " +
                             "[{} x {}] rectangular matrix.".format(*transformation_matrix.size()))
        self.transformation_matrix = transformation_matrix

    def __call__(self, tensor):
        """
        Args:
            tensor (Tensor): Tensor image of size (C, H, W) to be whitened.

        Returns:
            Tensor: Transformed image.
        """
        if tensor.size(0) * tensor.size(1) * tensor.size(2) != self.transformation_matrix.size(0):
            raise ValueError("tensor and transformation matrix have incompatible shape." +
                             "[{} x {} x {}] != ".format(*tensor.size()) +
                             "{}".format(self.transformation_matrix.size(0)))
        flat_tensor = tensor.view(1, -1)
        transformed_tensor = torch.mm(flat_tensor, self.transformation_matrix)
        tensor = transformed_tensor.view(tensor.size())
        return tensor

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        format_string += (str(self.transformation_matrix.numpy().tolist()) + ')')
        return format_string


class ColorJitter(object):
    """Randomly change the brightness, contrast and saturation of an image.

    Args:
        brightness (float): How much to jitter brightness. brightness_factor
            is chosen uniformly from [max(0, 1 - brightness), 1 + brightness].
        contrast (float): How much to jitter contrast. contrast_factor
            is chosen uniformly from [max(0, 1 - contrast), 1 + contrast].
        saturation (float): How much to jitter saturation. saturation_factor
            is chosen uniformly from [max(0, 1 - saturation), 1 + saturation].
        hue(float): How much to jitter hue. hue_factor is chosen uniformly from
            [-hue, hue]. Should be >=0 and <= 0.5.
    """
    def __init__(self, brightness=0, contrast=0, saturation=0, hue=0):

        assert isinstance(brightness, float) or (isinstance(brightness, collections.Iterable) and len(brightness) == 2)
        assert isinstance(contrast, float) or (isinstance(contrast, collections.Iterable) and len(contrast) == 2)
        assert isinstance(saturation, float) or (isinstance(saturation, collections.Iterable) and len(saturation) == 2)
        assert isinstance(hue, float) or (isinstance(hue, collections.Iterable) and len(hue) == 2)
        
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.hue = hue

    @staticmethod
    def get_params(brightness, contrast, saturation, hue):
        """Get a randomized transform to be applied on image.

        Arguments are same as that of __init__.

        Returns:
            Transform which randomly adjusts brightness, contrast and
            saturation in a random order.
        """
        transforms = []

        if isinstance(brightness, numbers.Number):
        
            if brightness > 0:
                brightness_factor = random.uniform(max(0, 1 - brightness), 1 + brightness)
                transforms.append(Lambda(lambda img: F.adjust_brightness(img, brightness_factor)))

            if contrast > 0:
                contrast_factor = random.uniform(max(0, 1 - contrast), 1 + contrast)
                transforms.append(Lambda(lambda img: F.adjust_contrast(img, contrast_factor)))

            if saturation > 0:
                saturation_factor = random.uniform(max(0, 1 - saturation), 1 + saturation)
                transforms.append(Lambda(lambda img: F.adjust_saturation(img, saturation_factor)))

            if hue > 0:
                hue_factor = random.uniform(-hue, hue)
                transforms.append(Lambda(lambda img: F.adjust_hue(img, hue_factor)))

        
        else:

            if brightness[0] > 0 and brightness[1] > 0:  
                
                brightness_factor = random.uniform(brightness[0], brightness[1])
                transforms.append(Lambda(lambda img: F.adjust_brightness(img, brightness_factor)))

            if contrast[0] > 0 and contrast[1] > 0:

                contrast_factor = random.uniform(contrast[0], contrast[1])
                transforms.append(Lambda(lambda img: F.adjust_contrast(img, contrast_factor)))

            if saturation[0] > 0 and saturation[1] > 0:
            
                saturation_factor = random.uniform(saturation[0], saturation[1])
                transforms.append(Lambda(lambda img: F.adjust_saturation(img, saturation_factor)))

            if hue[0] > 0 and hue[1] > 0:
                hue_factor = random.uniform(hue[0], hue[1])
                transforms.append(Lambda(lambda img: F.adjust_hue(img, hue_factor)))
            
        random.shuffle(transforms)
        transform = Compose(transforms)
        
        return transform

    def __call__(self, img):
        """
        Args:
            img (np.ndarray): Input image.

        Returns:
            np.ndarray: Color jittered image.
        """
        transform = self.get_params(self.brightness, self.contrast,
                                    self.saturation, self.hue)
        return transform(img)

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        format_string += 'brightness={0}'.format(self.brightness)
        format_string += ', contrast={0}'.format(self.contrast)
        format_string += ', saturation={0}'.format(self.saturation)
        format_string += ', hue={0})'.format(self.hue)
        return format_string


class RandomRotation(object):
    """Rotate the image by angle.

    Args:
        degrees (sequence or float or int): Range of degrees to select from.
            If degrees is a number instead of sequence like (min, max), the range of degrees
            will be (-degrees, +degrees) clockwise order.
        resample ({CV.Image.NEAREST, CV.Image.BILINEAR, CV.Image.BICUBIC}, optional):
            An optional resampling filter.
            See http://pillow.readthedocs.io/en/3.4.x/handbook/concepts.html#filters
            If omitted, or if the image has mode "1" or "P", it is set to NEAREST.
        expand (bool, optional): Optional expansion flag.
            If true, expands the output to make it large enough to hold the entire rotated image.
            If false or omitted, make the output image the same size as the input image.
            Note that the expand flag assumes rotation around the center and no translation.
        center (2-tuple, optional): Optional center of rotation.
            Origin is the upper left corner.
            Default is the center of the image.
    """

    def __init__(self, degrees, resample='BILINEAR', expand=False, center=None):
        if isinstance(degrees, numbers.Number):
            if degrees < 0:
                raise ValueError("If degrees is a single number, it must be positive.")
            self.degrees = (-degrees, degrees)
        else:
            if len(degrees) != 2:
                raise ValueError("If degrees is a sequence, it must be of len 2.")
            self.degrees = degrees

        self.resample = resample
        self.expand = expand
        self.center = center

    @staticmethod
    def get_params(degrees):
        """Get parameters for ``rotate`` for a random rotation.

        Returns:
            sequence: params to be passed to ``rotate`` for random rotation.
        """
        angle = random.uniform(degrees[0], degrees[1])

        return angle

    def __call__(self, img):
        """
            img (np.ndarray): Image to be rotated.

        Returns:
            np.ndarray: Rotated image.
        """

        angle = self.get_params(self.degrees)

        return F.rotate(img, angle, self.resample, self.expand, self.center)

    def __repr__(self):
        format_string = self.__class__.__name__ + '(degrees={0}'.format(self.degrees)
        format_string += ', resample={0}'.format(self.resample)
        format_string += ', expand={0}'.format(self.expand)
        if self.center is not None:
            format_string += ', center={0}'.format(self.center)
        format_string += ')'
        return format_string


class RandomAffine(object):
    """Random affine transformation of the image keeping center invariant

    Args:
        degrees (sequence or float or int): Range of degrees to select from.
            If degrees is a number instead of sequence like (min, max), the range of degrees
            will be (-degrees, +degrees). Set to 0 to desactivate rotations.
        translate (tuple, optional): tuple of maximum absolute fraction for horizontal
            and vertical translations. For example translate=(a, b), then horizontal shift
            is randomly sampled in the range -img_width * a < dx < img_width * a and vertical shift is
            randomly sampled in the range -img_height * b < dy < img_height * b. Will not translate by default.
        scale (tuple, optional): scaling factor interval, e.g (a, b), then scale is
            randomly sampled from the range a <= scale <= b. Will keep original scale by default.
        shear (sequence or float or int, optional): Range of degrees to select from.
            If degrees is a number instead of sequence like (min, max), the range of degrees
            will be (-degrees, +degrees). Will not apply shear by default
        resample ({NEAREST, BILINEAR, BICUBIC}, optional): An optional resampling filter.
        fillcolor (int): Optional fill color for the area outside the transform in the output image. (Pillow>=5.0.0)
    """

    def __init__(self, degrees=0, translate=None, scale=None, shear=None, resample='BILINEAR', fillcolor=0):
        if isinstance(degrees, numbers.Number):
            if degrees < 0:
                raise ValueError("If degrees is a single number, it must be positive.")
            self.degrees = (-degrees, degrees)
        else:
            assert isinstance(degrees, (tuple, list)) and len(degrees) == 2, \
                "degrees should be a list or tuple and it must be of length 2."
            self.degrees = degrees

        if translate is not None:
            assert isinstance(translate, (tuple, list)) and len(translate) == 2, \
                "translate should be a list or tuple and it must be of length 2."
            for t in translate:
                if not (0.0 <= t <= 1.0):
                    raise ValueError("translation values should be between 0 and 1")
        self.translate = translate

        if scale is not None:
            assert isinstance(scale, (tuple, list)) and len(scale) == 2, \
                "scale should be a list or tuple and it must be of length 2."
            for s in scale:
                if s <= 0:
                    raise ValueError("scale values should be positive")
        self.scale = scale

        if shear is not None:
            if isinstance(shear, numbers.Number):
                if shear < 0:
                    raise ValueError("If shear is a single number, it must be positive.")
                self.shear = (-shear, shear)
            else:
                assert isinstance(shear, (tuple, list)) and len(shear) == 2, \
                    "shear should be a list or tuple and it must be of length 2."
                self.shear = shear
        else:
            self.shear = shear

        self.resample = resample
        self.fillcolor = fillcolor

    @staticmethod
    def get_params(degrees, translate, scale_ranges, shears, img_size):
        """Get parameters for affine transformation

        Returns:
            sequence: params to be passed to the affine transformation
        """
        angle = random.uniform(degrees[0], degrees[1])
        if translate is not None:
            max_dx = translate[0] * img_size[1]
            max_dy = translate[1] * img_size[0]
            translations = (np.round(random.uniform(-max_dx, max_dx)),
                            np.round(random.uniform(-max_dy, max_dy)))
        else:
            translations = (0, 0)

        if scale_ranges is not None:
            scale = random.uniform(scale_ranges[0], scale_ranges[1])
        else:
            scale = 1.0

        if shears is not None:
            shear = random.uniform(shears[0], shears[1])
        else:
            shear = 0.0

        return angle, translations, scale, shear

    def __call__(self, img):
        """
            img (CV Image): Image to be transformed.

        Returns:
            CV Image: Affine transformed image.
        """
        ret = self.get_params(self.degrees, self.translate, self.scale, self.shear, img.shape)
        return F.affine(img, *ret, resample=self.resample, fillcolor=self.fillcolor)

    def __repr__(self):
        s = '{name}(degrees={degrees}'
        if self.translate is not None:
            s += ', translate={translate}'
        if self.scale is not None:
            s += ', scale={scale}'
        if self.shear is not None:
            s += ', shear={shear}'
        if self.resample > 0:
            s += ', resample={resample}'
        if self.fillcolor != 0:
            s += ', fillcolor={fillcolor}'
        s += ')'
        d = dict(self.__dict__)
        d['resample'] = d['resample']
        return s.format(name=self.__class__.__name__, **d)


class Grayscale(object):
    """Convert image to grayscale.

    Args:
        num_output_channels (int): (1 or 3) number of channels desired for output image

    Returns:
        CV Image: Grayscale version of the input.
        - If num_output_channels == 1 : returned image is single channel
        - If num_output_channels == 3 : returned image is 3 channel with r == g == b

    """

    def __init__(self, num_output_channels=3):
        self.num_output_channels = num_output_channels

    def __call__(self, img):
        """
        Args:
            img (CV Image): Image to be converted to grayscale.

        Returns:
            CV Image: Randomly grayscaled image.
        """
        return F.to_grayscale(img, num_output_channels=self.num_output_channels)

    def __repr__(self):
        return self.__class__.__name__ + '(num_output_channels={0})'.format(self.num_output_channels)


class RandomGrayscale(object):
    """Randomly convert image to grayscale with a probability of p (default 0.1).

    Args:
        p (float): probability that image should be converted to grayscale.

    Returns:
        CV Image: Grayscale version of the input image with probability p and unchanged
        with probability (1-p).
        - If input image is 1 channel: grayscale version is 1 channel
        - If input image is 3 channel: grayscale version is 3 channel with r == g == b

    """

    def __init__(self, p=0.1):
        self.p = p

    def __call__(self, img):
        """
        Args:
            img (np.ndarray): Image to be converted to grayscale.

        Returns:
            np.ndarray: Randomly grayscaled image.
        """
        num_output_channels = 3
        if random.random() < self.p:
            return F.to_grayscale(img, num_output_channels=num_output_channels)
        return img

    def __repr__(self):
        return self.__class__.__name__ + '(p={0})'.format(self.p)


class RandomPerspective(object):
    """Random perspective transformation of the image keeping center invariant
        Args:
            fov(float): range of wide angle = 90+-fov
            anglex (sequence or float or int): Range of degrees rote around X axis to select from.
                If degrees is a number instead of sequence like (min, max), the range of degrees
                will be (-degrees, +degrees). Set to 0 to desactivate rotations.
            angley (sequence or float or int): Range of degrees rote around Y axis to select from.
                If degrees is a number instead of sequence like (min, max), the range of degrees
                will be (-degrees, +degrees). Set to 0 to desactivate rotations.
            anglez (sequence or float or int): Range of degrees rote around Z axis to select from.
                If degrees is a number instead of sequence like (min, max), the range of degrees
                will be (-degrees, +degrees). Set to 0 to desactivate rotations.

            shear (sequence or float or int): Range of degrees for shear rote around axis to select from.
                If degrees is a number instead of sequence like (min, max), the range of degrees
                will be (-degrees, +degrees). Set to 0 to desactivate rotations.
            translate (tuple, optional): tuple of maximum absolute fraction for horizontal
                and vertical translations. For example translate=(a, b), then horizontal shift
                is randomly sampled in the range -img_width * a < dx < img_width * a and vertical shift is
                randomly sampled in the range -img_height * b < dy < img_height * b. Will not translate by default.
            scale (tuple, optional): scaling factor interval, e.g (a, b), then scale is
                randomly sampled from the range a <= scale <= b. Will keep original scale by default.
            resample ({NEAREST, BILINEAR, BICUBIC}, optional): An optional resampling filter.
            fillcolor (int): Optional fill color for the area outside the transform in the output image. (Pillow>=5.0.0)
        """

    def __init__(self, fov=0, anglex=0, angley=0, anglez=0, shear=0,
                 translate=(0, 0), scale=(1, 1), resample='BILINEAR', fillcolor=(0, 0, 0)):

        assert all([isinstance(anglex, (tuple, list)) or anglex >= 0,
                    isinstance(angley, (tuple, list)) or angley >= 0,
                    isinstance(anglez, (tuple, list)) or anglez >= 0,
                    isinstance(shear, (tuple, list)) or shear >= 0]), \
            'All angles must be positive or tuple or list'
        assert 80 >= fov >= 0, 'fov should be in (0, 80)'
        self.fov = fov

        self.anglex = (-anglex, anglex) if isinstance(anglex, numbers.Number) else anglex
        self.angley = (-angley, angley) if isinstance(angley, numbers.Number) else angley
        self.anglez = (-anglez, anglez) if isinstance(anglez, numbers.Number) else anglez
        self.shear = (-shear, shear) if isinstance(shear, numbers.Number) else shear

        assert isinstance(translate, (tuple, list)) and len(translate) == 2, \
            "translate should be a list or tuple and it must be of length 2."
        assert all([0.0 <= i <= 1.0 for i in translate]), "translation values should be between 0 and 1"
        self.translate = translate

        if scale is not None:
            assert isinstance(scale, (tuple, list)) and len(scale) == 2, \
                "scale should be a list or tuple and it must be of length 2."
            assert all([s > 0 for s in scale]), "scale values should be positive"
        self.scale = scale

        self.resample = resample
        self.fillcolor = fillcolor

    @staticmethod
    def get_params(fov_range, anglex_ranges, angley_ranges, anglez_ranges, shear_ranges,
                   translate, scale_ranges,  img_size):
        """Get parameters for perspective transformation

        Returns:
            sequence: params to be passed to the perspective transformation
        """
        fov = 90 + random.uniform(-fov_range, fov_range)
        anglex = random.uniform(anglex_ranges[0], anglex_ranges[1])
        angley = random.uniform(angley_ranges[0], angley_ranges[1])
        anglez = random.uniform(anglez_ranges[0], anglez_ranges[1])
        shear = random.uniform(shear_ranges[0], shear_ranges[1])

        max_dx = translate[0] * img_size[1]
        max_dy = translate[1] * img_size[0]
        translations = (np.round(random.uniform(-max_dx, max_dx)),
                        np.round(random.uniform(-max_dy, max_dy)))

        scale = (random.uniform(1 / scale_ranges[0], scale_ranges[0]),
                 random.uniform(1 / scale_ranges[1], scale_ranges[1]))

        return fov, anglex, angley, anglez, shear, translations, scale

    def __call__(self, img):
        """
            img (np.ndarray): Image to be transformed.

        Returns:
            np.ndarray: Affine transformed image.
        """
        ret = self.get_params(self.fov, self.anglex, self.angley, self.anglez, self.shear,
                              self.translate, self.scale, img.shape)
        return F.perspective(img, *ret, resample=self.resample, fillcolor=self.fillcolor)

    def __repr__(self):
        s = '{name}(degrees={degrees}'
        if self.translate is not None:
            s += ', translate={translate}'
        if self.scale is not None:
            s += ', scale={scale}'
        if self.shear is not None:
            s += ', shear={shear}'
        if self.resample > 0:
            s += ', resample={resample}'
        if self.fillcolor != 0:
            s += ', fillcolor={fillcolor}'
        s += ')'
        d = dict(self.__dict__)
        d['resample'] = d['resample']
        return s.format(name=self.__class__.__name__, **d)


class RandomAffine6(object):
    """Random affine transformation of the image keeping center invariant

    Args:
        anglez (sequence or float or int): Range of rotate to select from.
            If degrees is a number instead of sequence like (min, max), the range of degrees
            will be (-anglez, +anglez). Set to 0 to desactivate rotations.
        shear (sequence or float or int): Range of shear to select from.
            If degrees is a number instead of sequence like (min, max), the range of degrees
            will be (-shear, +shear). Set to 0 to desactivate shear.
        translate (tuple, optional): tuple of maximum absolute fraction for horizontal
            and vertical translations. For example translate=(a, b), then horizontal shift
            is randomly sampled in the range -img_width * a < dx < img_width * a and vertical shift is
            randomly sampled in the range -img_height * b < dy < img_height * b. Will not translate by default.
        scale (tuple, optional): scaling factor interval, e.g (a, b), then scale is
            randomly sampled from the range a <= scale <= b. Will keep original scale by default.
        resample ({NEAREST, BILINEAR, BICUBIC}, optional): An optional resampling filter.
        fillcolor (int): Optional fill color for the area outside the transform in the output image. (Pillow>=5.0.0)
    """

    def __init__(self, anglez=0, shear=0, translate=(0, 0), scale=(1, 1),
                 resample='BILINEAR', fillcolor=(0, 0, 0)):
        if isinstance(anglez, numbers.Number):
            if anglez < 0:
                raise ValueError("If anglez is a single number, it must be positive.")
            self.anglez = (-anglez, anglez)
        else:
            assert isinstance(anglez, (tuple, list)) and len(anglez) == 2, \
                "anglez should be a list or tuple and it must be of length 2."
            self.anglez = anglez

        if isinstance(shear, numbers.Number):
            if shear < 0:
                raise ValueError("If shear is a single number, it must be positive.")
            self.shear = (-shear, shear)
        else:
            assert isinstance(shear, (tuple, list)) and len(shear) == 2, \
                "shear should be a list or tuple and it must be of length 2."
            self.shear = shear

        if translate is not None:
            assert isinstance(translate, (tuple, list)) and len(translate) == 2, \
                "translate should be a list or tuple and it must be of length 2."
            for t in translate:
                if not (0.0 <= t <= 1.0):
                    raise ValueError("translation values should be between 0 and 1")
        self.translate = translate

        if scale is not None:
            assert isinstance(scale, (tuple, list)) and len(scale) == 2, \
                "scale should be a list or tuple and it must be of length 2."
            for s in scale:
                if s <= 0:
                    raise ValueError("scale values should be positive")
        self.scale = scale
        self.resample = resample
        self.fillcolor = fillcolor

    @staticmethod
    def get_params(img_size, anglez_range=(0, 0), shear_range=(0, 0),
                   translate=(0, 0), scale_ranges=(1, 1)):
        """Get parameters for affine transformation

        Returns:
            sequence: params to be passed to the affine transformation
        """
        angle = random.uniform(anglez_range[0], anglez_range[1])
        shear = random.uniform(shear_range[0], shear_range[1])

        max_dx = translate[0] * img_size[1]
        max_dy = translate[1] * img_size[0]
        translations = (np.round(random.uniform(-max_dx, max_dx)),
                        np.round(random.uniform(-max_dy, max_dy)))

        scale = (random.uniform(1 / scale_ranges[0], scale_ranges[0]),
                 random.uniform(1 / scale_ranges[1], scale_ranges[1]))

        return angle, shear, translations, scale

    def __call__(self, img):
        """
            img (np.ndarray): Image to be transformed.

        Returns:
            np.ndarray: Affine transformed image.
        """
        ret = self.get_params(img.shape, self.anglez, self.shear, self.translate, self.scale)
        return F.affine6(img, *ret, resample=self.resample, fillcolor=self.fillcolor)

    def __repr__(self):
        s = '{name}(degrees={degrees}'
        if self.translate is not None:
            s += ', translate={translate}'
        if self.scale is not None:
            s += ', scale={scale}'
        if self.shear is not None:
            s += ', shear={shear}'
        if self.resample > 0:
            s += ', resample={resample}'
        if self.fillcolor != 0:
            s += ', fillcolor={fillcolor}'
        s += ')'
        d = dict(self.__dict__)
        d['resample'] = d['resample']
        return s.format(name=self.__class__.__name__, **d)


class RandomGaussianNoise(object):
    """Applying gaussian noise on the given CV Image randomly with a given probability.

        Args:
            p (float): probability of the image being noised. Default value is 0.5
        """

    def __init__(self, p=0.5, mean=0, std=0.1):
        assert isinstance(mean, numbers.Number) and mean >= 0, 'mean should be a positive value'
        assert isinstance(std, numbers.Number) and std >= 0, 'std should be a positive value'
        assert isinstance(p, numbers.Number) and p >= 0, 'p should be a positive value'
        self.p = p
        self.mean = mean
        self.std = std

    @staticmethod
    def get_params(mean, std):
        """Get parameters for gaussian noise

        Returns:
            sequence: params to be passed to the affine transformation
        """
        mean = random.uniform(-mean, mean)
        std = random.uniform(-std, std)

        return mean, std

    def __call__(self, img):
        """
        Args:
            img (np.ndarray): Image to be noised.

        Returns:
            np.ndarray: Randomly noised image.
        """
        if random.random() < self.p:
            return F.gaussian_noise(img, mean=self.mean, std=self.std)
        return img

    def __repr__(self):
        return self.__class__.__name__ + '(p={})'.format(self.p)


class RandomPoissonNoise(object):
    """Applying Poisson noise on the given CV Image randomly with a given probability.

        Args:
            p (float): probability of the image being noised. Default value is 0.5
        """

    def __init__(self, p=0.5):
        assert isinstance(p, numbers.Number) and p >= 0, 'p should be a positive value'
        self.p = p

    def __call__(self, img):
        """
        Args:
            img (np.ndarray): Image to be noised.

        Returns:
            np.ndarray: Randomly noised image.
        """
        if random.random() < self.p:
            return F.poisson_noise(img)
        return img

    def __repr__(self):
        return self.__class__.__name__ + '(p={})'.format(self.p)


class RandomSPNoise(object):
    """Applying salt and pepper noise on the given CV Image randomly with a given probability.

        Args:
            p (float): probability of the image being noised. Default value is 0.5
        """

    def __init__(self, p=0.5, prob=0.1):
        assert isinstance(p, numbers.Number) and p >= 0, 'p should be a positive value'
        assert isinstance(prob, numbers.Number) and prob >= 0, 'p should be a positive value'
        self.p = p
        self.prob = prob

    def __call__(self, img):
        """
        Args:
            img (np.ndarray): Image to be noised.

        Returns:
            np.ndarray: Randomly noised image.
        """
        if random.random() < self.p:
            return F.salt_and_pepper(img, self.prob)
        return img

    def __repr__(self):
        return self.__class__.__name__ + '(p={})'.format(self.p)