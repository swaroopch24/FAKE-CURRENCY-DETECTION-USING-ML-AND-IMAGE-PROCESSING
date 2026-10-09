import sys
import platform
import os

print(f'Python version: {sys.version}')
print(f'Platform: {platform.platform()}')
try:
    import tensorflow as tf
    print(f'TensorFlow version: {tf.__version__}')
    print(f'Keras version: {tf.keras.__version__}')
    print(f'GPU Available: {tf.test.is_built_with_cuda()} / {tf.config.list_physical_devices("GPU")}')
except ImportError:
    print('TensorFlow: NOT INSTALLED')
try:
    import numpy as np
    print(f'NumPy version: {np.__version__}')
except ImportError:
    print('NumPy: NOT INSTALLED')
try:
    import cv2
    print(f'OpenCV version: {cv2.__version__}')
except ImportError:
    print('OpenCV: NOT INSTALLED')
try:
    from PIL import Image
    import PIL
    print(f'Pillow version: {PIL.__version__}')
except ImportError:
    print('Pillow: NOT INSTALLED')
try:
    import onnxruntime
    print(f'ONNX Runtime version: {onnxruntime.__version__}')
except ImportError:
    print('ONNX Runtime: NOT INSTALLED')
