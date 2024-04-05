#include <pybind11/pybind11.h>
#include <pybind11/stl.h> 
#include <vector>
#include <pybind11/numpy.h> 

namespace py = pybind11;

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
    m.def("binarize_numpy", &binarize_numpy, "A function that binarizes an image using NumPy arrays",
        py::arg("image"), py::arg("threshold") = 127);
}
