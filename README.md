# Blur Shader Research with Slang

## Overview

This project implements several image blur algorithms using Slang and SlangPy.

The goal is to provide a lightweight environment for developing, testing, and comparing different blur algorithms without relying on a game engine.

The project uses Python to manage the rendering pipeline and Slang to implement the shaders. Rendering is performed on the GPU through Direct3D 12.

## Implemented Algorithms

The following blur algorithms are currently implemented:

- Box Blur
- Gaussian Blur
- Two-Pass Gaussian Blur
- Kawase Blur
- Multi-Pass Kawase Blur
- Dual Kawase Blur
- Dither-Based Blur

Each algorithm is implemented in Slang and can be selected through the Python program.

## Requirements

The project was developed and tested with the following environment:

- Windows 10/11
- Python 3.12.10
- SlangPy 0.43.1
- NumPy
- Pillow
- Direct3D 12 compatible GPU

**Optional:**

- Slang SDK / Compiler — for compiling Slang shaders into other shader languages, such as GLSL.
- Visual Studio Code and the Slang extension — for shader development.

## Installation

Install the required Python packages:

```bash
python -m pip install slangpy==0.43.1 numpy pillow
```

To verify the GPU environment:

```bash
python -c "import slangpy as spy; device = spy.Device(type=spy.DeviceType.d3d12); print('D3D12 OK')"
```

## Project Structure

```text
Blur/
├── main.py
├── rendering.py
├── input.png
├── Noise.png
├── Shaders/
│   ├── Vertex.slang
│   ├── BoxBlur.slang
│   ├── GaussianBlur.slang
│   ├── HorizontalGaussian.slang
│   ├── VerticalGaussian.slang
│   ├── KawaseBlur.slang
│   ├── DualKawaseDown.slang
│   ├── DualKawaseUp.slang
│   └── DitherBlur.slang
└── outputs/
```

- `main.py`: Configures blur algorithms, manages render targets, and executes rendering passes.
- `rendering.py`: Provides reusable functions for creating pipelines, configuring render passes, and issuing draw commands.
- `Shaders/`: Contains the Slang shader implementations.
- `input.png`: Source image used for blur processing.
- `Noise.png`: Noise texture used by Dither Blur.
- `outputs/`: Stores the generated images.

## How to Run

Open a terminal in the project root directory and run:

```bash
python main.py
```

To select a blur algorithm, change the `blur_name` variable in `main.py`.

For example:

```python
blur_name = "DualKawase"
```

The program will execute the selected algorithm and save the resulting image in the `outputs/` directory.

## Shader Compilation

The Slang SDK can be used to compile shaders into other languages.

For example, to compile a fragment shader into GLSL:

```bash
slangc Shaders/GaussianBlur.slang -entry FragmentMain -stage fragment -target glsl -profile glsl_450 -o GaussianBlur.glsl
```

The generated shader may require additional adaptation for the target rendering environment.

## Notes

- The current rendering implementation uses Direct3D 12.
- Multi-pass algorithms use intermediate render targets.
- Dual Kawase Blur uses different render target resolutions across its downsampling and upsampling passes.
- Dither Blur uses noise-based UV distortion and two input texture samples per fragment.
- GPU performance benchmarking is not included in the current implementation.
