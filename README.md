# opencv_torchvision_transform
1) This is a "transforms" in [torchvision](https://github.com/pytorch/vision/tree/master/torchvision/transforms) based on opencv. 

2) All functions depend on only cv2 and pytorch (PIL-free). As the [article](https://www.kaggle.com/vfdev5/pil-vs-opencv) says, cv2 is three times faster than PIL.

3) Most functions in transforms are reimplemented, except that:

   1) ToPILImage (opencv we used :)), Scale and RandomSizedCrop which are deprecated in the original version are
    ignored.
   
   2) The affine transform in the original one only has 5 degrees of freedom, I implement an Affine transform with 6
    degress of freedom called `RandomAffine6` (can be found in [cvtransforms.py](cvtorchvision/cvtransforms/cvtransforms.py)). The
     original method `RandomAffine` is still retained and reimplemented with opencv.
   3) My rotate function is clockwise, however the original one is  anticlockwise.
   4) Adding some new methods which can be found in **Support** (the bolded ones).
   4) **All the outputs of the opencv version are almost the same as the original one's (test in [cvfunctional.py](/cvtorchvision/cvtransforms/cvfunctional.py#L892-L906))**.
## Support:
* `Compose`, `ToTensor`, `ToCVImage`, `Normalize`

* `Resize`, `CenterCrop`, `Pad`

* `Lambda` (doesn't work well in multiprocess in Windows)

* `RandomApply`, `RandomOrder`, `RandomChoice`, `RandomCrop`,

* `RandomHorizontalFlip`, `RandomVerticalFlip`, `RandomResizedCrop`,

* `FiveCrop`, `TenCrop`, `LinearTransformation`, `ColorJitter`,

* `RandomRotation`, `RandomAffine`, `*RandomAffine6`, `*RandomPerspective`

* `*RandomGaussianNoise`, `*RandomPoissonNoise`, `*RandomSPNoise`

* `Grayscale`, `RandomGrayscale`
# How to use:
1) git clone https://github.com/YU-Zhiyang/opencv_torchvision_transforms.git .

2) Add `cvtorchvision` to your python path.

3) Add `from cvtorchvision import cvtransforms` in your python file.

4) You can use all functions as the original version, for example:

       transform = cvtransforms.Compose([
        
                cvtransforms.RandomAffine(degrees=10, translate=(0.1, 0.1), scale=(0.9, 1.1), shear=(-10, 0),
        
                cvtransforms.Resize(size=(350, 350), interpolation='BILINEAR'),
        
                cvtransforms.ToTensor(),
        
                cvtransforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                ])

more details can be found in the examples of official [tutorials](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html).

# Good News:
You can install this package via `pip install opencv-torchvision-transforms-yuzhiyang` (Old version only)
 
# Attention: 
The multiprocessing used in dataloader of pytorch is not friendly with lambda function in Windows as lambda function can't be pickled (https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled).

So the Lambda in [cvtransforms.py](cvtorchvision/cvtransforms/cvtransforms.py) may not work properly in Windows.

# Requirements
python >=3.5.2

numpy >=1.10 ('@' operator may not be overloaded before this version)

pytorch>=0.4.1

torchvision>=0.2.1

opencv-contrib-python-3.4.2 (test with this version, but any version of opencv3 is ok, I think)

# Postscript
Welcome to point out and help fixing bugs!

Thanks [HongChu](https://github.com/hongchu098) who helps a lot.
