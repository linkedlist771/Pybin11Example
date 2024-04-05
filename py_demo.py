import cv2
import time
import binary_example




def timeit(func):
    """A decorator that measures the execution time of a function."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"{func.__name__:<20} executed in {end_time - start_time:.8f} seconds.")
        return result
    return wrapper

@timeit
def binarize_cv2(image, threshold: int = 127):
    _, binary = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return binary

@timeit
def binarize_raw(image, threshold: int = 127):

    image[image > threshold] = 255
    image[image <= threshold] = 0
    return image

@timeit
def binarize_explicit(image, threshold: int = 127):
    height, width = image.shape
    binary = image.copy()
    for i in range(height):
        for j in range(width):
            binary[i, j] = 255 if image[i, j] > threshold else 0
    return binary

@timeit
def binarize_pybind(image, threshold: int = 127):
    binary = binary_example.binarize_pybind11(image, threshold)
    return binary

@timeit
def binarize_pybind_numpy(image, threshold: int = 127):
    binary = binary_example.binarize_numpy(image, threshold)
    return binary

image_path = "lena.png"
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
img_cv2 = img.copy()
img_raw = img.copy()
img_explicit = img.copy()
img_pybind = img.copy()
img_numpy = img.copy()
binary_cv2 = binarize_cv2(img_cv2)
binary_raw = binarize_raw(img_raw)
binary_explicit = binarize_explicit(img_explicit)
binary_pybind = binarize_pybind(img_pybind)
binary_numpy = binarize_pybind_numpy(img_numpy)

assert (binary_cv2 == binary_raw).all()
assert (binary_cv2 == binary_explicit).all()
assert (binary_cv2 == binary_pybind).all()
assert (binary_cv2 == binary_numpy).all()
