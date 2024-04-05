# Pybin11Example


> 在使用`Python`的时候由于`GIL`的限制以及本身的性能瓶颈，我们很多时候希望在Python中使用`C/C++`格式的代码。本博客聚焦点也是在此。




主流在Python中使用`C/C++`代码主要有两种方式，第一种是使用`pybind11`构建。

#  Pybind11

具体代码可以参考：

[linkedlist771/Pybin11Example (github.com)](https://github.com/linkedlist771/Pybin11Example)

在这里我们举一个最简单的例子来说明使用Pybind11来处理。对`lena.png`图像进行二值化处理。首先我们选出最简单的`lena`图片作为使用图片来使用。下面分别给出三种实现方式：

1. 直接使用`opencv` 内置二值化函数
2. 使用`numpy`的布尔广播机制
3. 使用`python`的显示for循环。

```python
def timeit(func):
    """A decorator that measures the execution time of a function."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__:<20} executed in {end_time - start_time:.6f} seconds.")
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

```



查看输出时间可以看出：

```
binarize_cv2         executed in 0.013167 seconds.
binarize_raw         executed in 0.000973 seconds.
binarize_explicit    executed in 0.299734 seconds.
```

其实`opencv`内置的函数并不是最快的，nupy的广播最快的。

下面再给出使用`pybind11`的实现。

- 克隆`pybind11`项目：

```bash
git submodule add https://github.com/pybind/pybind11.git pybind11
git submodule update --init
```

- 编写`CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.4...3.18)
project(binary_example)

add_subdirectory(pybind11)
pybind11_add_module(binary_example main.cpp)

# EXAMPLE_VERSION_INFO is defined by setup.py and passed into the C++ code as a
# define (VERSION_INFO) here.
target_compile_definitions(binary_example
                           PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
```

- 编写`c++`代码

```c++
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> 
#include <vector>

namespace py = pybind11;

std::vector<std::vector<uint8_t>> binarize_pybind11(const std::vector<std::vector<uint8_t>>& image, uint8_t threshold) {
    std::vector<std::vector<uint8_t>> result = image;
    for (auto& row : result) {
        for (auto& pixel : row) {
            pixel = (pixel > threshold) ? 255 : 0;
        }
    }
    return result;
}

PYBIND11_MODULE(binary_example, m) {
    m.doc() = "Pybind11 example plugin";

    m.def("binarize_pybind11", &binarize_pybind11, "A function that binarizes an image",
          py::arg("image"), py::arg("threshold") = 127);
}

```

- 运行编译脚本

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

然后观看输出:

```bash
  binary_example.vcxproj -> C:\Users\23174\Desktop\GitHub Project\Pybin11Example\build\Release\binary_example.cp39-win_amd64.pyd
```

可以看到在windows环境下，已经被保存为`pyd`格式了。 然后把编译得到的结果移动到和代码同目录就可以使用了。

```python
import binary_example
@timeit
def binarize_pybind(image, threshold: int = 127):
    binary = binary_example.binarize_pybind11(image, threshold)
    return binary
```

得到的输出如下：

```bash
binarize_cv2         executed in 0.011669 seconds.
binarize_raw         executed in 0.000998 seconds.
binarize_explicit    executed in 0.265970 seconds.
binarize_pybind      executed in 0.020431 seconds.
```

可以看到使用`C++`for循环的速度比原生的Python for循环块，但是慢于其他的实现。当然我们，也可以尝试使用`numpy`的`C++`版本来实现看看。

```c++
py::array_t<uint8_t> binarize_numpy(py::array_t<uint8_t> input, uint8_t threshold) {
    auto buf = input.request();
    auto result = py::array_t<uint8_t>(buf.size);
    auto ptr = static_cast<uint8_t*>(buf.ptr);
    auto result_ptr = static_cast<uint8_t*>(result.request().ptr);

    for (ssize_t i = 0; i < buf.size; i++) {
        result_ptr[i] = (ptr[i] > threshold) ? 255 : 0;
    }

    result.resize(buf.shape);
    return result;
}
```

```python
@timeit
def binarize_pybind_numpy(image, threshold: int = 127):
    binary = binary_example.binarize_numpy(image, threshold)
    return binary
```

对比输出：

```bash
binarize_cv2         executed in 0.01235200 seconds.
binarize_raw         executed in 0.00070800 seconds.
binarize_explicit    executed in 0.28122040 seconds.
binarize_pybind      executed in 0.02416850 seconds.
binarize_pybind_numpy executed in 0.00038980 seconds.
```

可以看到，在C++中基于numpy实现的二值化函数是最快的， 甚至比Python调用numpy库更快。

