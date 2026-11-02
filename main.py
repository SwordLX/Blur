import numpy as np
from PIL import Image
import slangpy as spy
from pathlib import Path

from rendering import (
    create_pipeline,
    create_render_pass_desc,
    create_render_state,
    draw_fullscreen
)

# ====================================================
# 1. configuration
# ====================================================

BLUR_CONFIGS = {
    "BoxBlur": ["Shaders/BoxBlur.slang"],
    "GaussianBlur": ["Shaders/GaussianBlur.slang"],
    "TwoPassGaussianBlur":["Shaders/HorizontalGaussianBlur.slang", "Shaders/VerticalGaussianBlur.slang"],
    "KawaseBlur": ["Shaders/KawaseBlur.slang"],
    "MultiPassKawase": ["Shaders/KawaseBlur.slang", "Shaders/KawaseBlur.slang", "Shaders/KawaseBlur.slang", "Shaders/KawaseBlur.slang"],
    "DualKawase": ["Shaders/DualKawaseDown.slang", "Shaders/DualKawaseDown.slang","Shaders/DualKawaseDown.slang", "Shaders/DualKawaseUp.slang", "Shaders/DualKawaseUp.slang","Shaders/DualKawaseUp.slang"],
    "DitherBlur": ["Shaders/DitherBlur.slang"],
    "MixBlur": ["Shaders/BoxBlur.slang" ,"Shaders/DitherBlur.slang"]
}

# ====================================================================Change Shader File Here ============================================================
# Select blur algorithm
blur_name = "MixBlur"
shader_files = BLUR_CONFIGS[blur_name]
pass_count = len(shader_files)

# Only Work For Multi-pass Kawase
kawase_offsets = [1.0, 2.0, 3.0, 4.0]

# ===============================================================================Start building Rendering Pipeline ======================================================================================
# Create a device (D3D12 in this case)
device = spy.Device(type = spy.DeviceType.d3d12)


# create a texture from the image data
texture_loader = spy.TextureLoader(device)
input_texture = texture_loader.load_texture("image.png")
noise_texture = texture_loader.load_texture("Good64x64TilingNoiseHighFreq.png")

width = input_texture.width
height = input_texture.height


#create a sampler for the texture
sampler = device.create_sampler(
    min_filter = spy.TextureFilteringMode.linear,
    mag_filter = spy.TextureFilteringMode.linear,
    address_u = spy.TextureAddressingMode.clamp_to_edge,
    address_v = spy.TextureAddressingMode.clamp_to_edge,
)

noise_sampler = device.create_sampler(
    min_filter = spy.TextureFilteringMode.linear,
    mag_filter = spy.TextureFilteringMode.linear,
    address_u = spy.TextureAddressingMode.wrap,
    address_v = spy.TextureAddressingMode.wrap,
)
# ==========================
# Create a render target
# ==========================

render_targets = []

for i in range(pass_count):
    is_last_pass = (i == pass_count - 1)

    # use half resolution for Dual Kawase Downsample
    if blur_name == "DualKawase":
        level = min(i+1, pass_count-i-1)

        target_width = max(1, width // (2**level))
        target_height = max(1, height // (2** level))
    else:
        target_width = width
        target_height = height
    
    # intermediate results use linear floating-point format.
    # final output uses sRGB format.
    target_format = (
        spy.Format.bgra8_unorm_srgb
        if is_last_pass
        else spy.Format.rgba16_float
    )

    usage = (
        spy.TextureUsage.render_target
        if is_last_pass
        else (spy.TextureUsage.render_target | spy.TextureUsage.shader_resource)
    )

    texture = device.create_texture(
        width = target_width,
        height = target_height,
        format = target_format,
        usage = usage
    )

    render_targets.append(texture)


# ==================================================
# Create Pipelines and Render Passes
# ==================================================

programs = []
pipelines = []
render_pass_descs = []
pass_resources = []

for i, shader_path in enumerate(shader_files):

    program = device.load_program(
        module_name = shader_path,
        entry_point_names=["VertexMain", "FragmentMain"]
    )

    pipeline = create_pipeline(device, program, render_targets[i].format)

    render_pass_desc, view, attachment = create_render_pass_desc( render_targets[i] )

    programs.append(program)
    pipelines.append(pipeline)
    render_pass_descs.append(render_pass_desc)

    # keep texture views and attachments alive
    pass_resources.append((view, attachment))


print("Pipelines and Render Passes Created")


# ==========================
# Create Render State
# ==========================

render_states = []

for target in render_targets:
    state = create_render_state(target.width, target.height)
    render_states.append(state)

# render_state = create_render_state(width, height)

# ==========================
# Record GPU Commands
# ==========================

encoder = device.create_command_encoder()

current_input = input_texture

for i in range(pass_count):

    if blur_name == "MultiPassKawase":
        blur_offset = kawase_offsets[i]
    elif blur_name == "DualKawase":
        blur_offset = 2.0
    else:
        blur_offset = None

    if blur_name == "DitherBlur":
        blur_strength = 0.015
    elif blur_name == "MixBlur":
        blur_strength = 0.03
    else:
        blur_strength = None

    draw_fullscreen(
        encoder,
        render_pass_descs[i],
        pipelines[i],
        current_input,
        sampler,
        render_states[i],
        blur_offset = blur_offset,
        noise_texture=noise_texture if blur_name == "DitherBlur" else None,
        noise_sampler=noise_sampler if blur_name == "DitherBlur" else None,
        blur_strength=blur_strength
    )

    # use the current pass output as next pass input
    current_input = render_targets[i]


# ==========================
# Submit Commands to GPU
# ==========================

command_buffer = encoder.finish()

submission_id = device.submit_command_buffer(command_buffer)
device.wait_for_submit(submission_id)

print("GPU execution completed")
# ====================================================================================GPU Work End=========================================================================================================

# ====================================================================================Read back the rendered image==========================================================================================
# Read back the rendered image
# =========================

final_texture = render_targets[-1]
output_data = final_texture.to_numpy()


# Convert BGRA to RGBA
output_data = output_data[..., [2, 1, 0, 3]]  # Swap B and R channels
output_data = np.ascontiguousarray(output_data)


# Save the output image
output_image = Image.fromarray(output_data, mode="RGBA")

#======================================================================================Output File Name Here=========================================================================================
Outputs_dir = Path("Outputs")
Outputs_dir.mkdir(parents=True, exist_ok=True)
Outputs_path = Outputs_dir / f"{blur_name}.png"
output_image.save(Outputs_path)

print("program finish")