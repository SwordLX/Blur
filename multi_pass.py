import numpy as np
from PIL import Image
import slangpy as spy
from pathlib import Path

image = Image.open("IceSword.png").convert("RGBA")

width, height = image.size

image_data = np.ascontiguousarray(
    np.asarray(image, dtype=np.uint8)
)

print("Image Size:", image.size)
print("Image Shape:", image_data.shape)



# Create a device (D3D12 in this case)
device = spy.Device(type = spy.DeviceType.d3d12)
print("Device Created")

# create a texture from the image data
texture_loader = spy.TextureLoader(device)

input_texture = texture_loader.load_texture("IceSword.png")

print("Texture Created")


#create a sampler for the texture
sampler = device.create_sampler(
    min_filter = spy.TextureFilteringMode.linear,
    mag_filter = spy.TextureFilteringMode.linear,
    address_u = spy.TextureAddressingMode.clamp_to_edge,
    address_v = spy.TextureAddressingMode.clamp_to_edge,
)
print("Sampler Created")


#load Shader
# ========================================================================================Change Shader File Here =========================================================================================

shader_path_horizontal =  "Shaders/HorizontalGaussianBlur.slang"                                                       # Change the shader file here
horizontal_program = device.load_program(
    module_name = shader_path_horizontal,
    entry_point_names=["VertexMain", "FragmentMain"]
)

shader_path_vertical = "Shaders/VerticalGaussianBlur.slang"
vertical_program = device.load_program(
    module_name = shader_path_vertical,
    entry_point_names=["VertexMain", "FragmentMain"]
)

# ==========================
# Create a render pipeline
# ==========================

horizontal_pipeline = device.create_render_pipeline(
    program = horizontal_program,
    input_layout = None,
    primitive_topology = spy.PrimitiveTopology.triangle_list,
    targets=[
        spy.ColorTargetDesc({"format": spy.Format.rgba16_float})
        ],
    rasterizer = spy.RasterizerDesc({
        "cull_mode": spy.CullMode.none,
    })
)

vertical_pipeline = device.create_render_pipeline(
    program = vertical_program,
    input_layout= None,
    primitive_topology = spy.PrimitiveTopology.triangle_list,
    targets = [
        spy.ColorTargetDesc({"format": spy.Format.bgra8_unorm_srgb})
    ],
    rasterizer = spy.RasterizerDesc({
        "cull_mode": spy.CullMode.none,
    })
)


print("Render Pipeline Created")


# ==================================================
# Create an intermediate Texture For multi-pass
# ===================================================
intermediate_texture = device.create_texture(
    width = width,
    height = height,
    format = spy.Format.rgba16_float,
    usage = (spy.TextureUsage.render_target | spy.TextureUsage.shader_resource)
)

intermediate_texture_view = intermediate_texture.create_view()

# ==========================
# Create a render target
# ==========================

render_target = device.create_texture(
    width = width,
    height = height,
    format = spy.Format.bgra8_unorm_srgb,
    usage = spy.TextureUsage.render_target
)

render_target_view = render_target.create_view()

print("Render Target Created")


# ==========================
# Create Render Pass
# ==========================

horizontal_color_attachment = spy.RenderPassColorAttachment({
    "view": intermediate_texture_view,
    "load_op": spy.LoadOp.clear,
    "store_op": spy.StoreOp.store,
    "clear_value": (0.0, 0.0, 0.0, 1.0)
})
horizontal_render_pass_desc = spy.RenderPassDesc({
    "color_attachments": [horizontal_color_attachment]
})

vertical_color_attachment = spy.RenderPassColorAttachment({
    "view": render_target_view,
    "load_op": spy.LoadOp.clear,
    "store_op": spy.StoreOp.store,
    "clear_value": (0.0, 0.0, 0.0, 1.0)
})

vertical_render_pass_desc = spy.RenderPassDesc({
    "color_attachments": [vertical_color_attachment]
})


# ==========================
# Set render state
# ==========================

render_state = spy.RenderState({
    "viewports": [
        spy.Viewport({
            "x": 0.0,
            "y": 0.0,
            "width": float(width),
            "height": float(height),
            "min_depth": 0.0,
            "max_depth": 1.0
        })
    ],
    "scissor_rects": [
        spy.ScissorRect({
            "min_x": 0,
            "min_y": 0,
            "max_x": width,
            "max_y": height
        })
    ]
})

# ==========================
# Record GPU Commands
# ==========================
encoder = device.create_command_encoder()

# pass1:
horizontal_render_pass = encoder.begin_render_pass(horizontal_render_pass_desc)

horizontal_root = horizontal_render_pass.bind_pipeline(horizontal_pipeline)

# Bind the texture and sampler to the fragment shader
horizontal_cursor = spy.ShaderCursor(horizontal_root)

horizontal_render_pass.set_render_state(render_state)

horizontal_cursor.find_field("inputTexture").write(input_texture)
horizontal_cursor.find_field("inputSampler").write(sampler)


# Draw fullscreen quad
horizontal_render_pass.draw(
    spy.DrawArguments({
        "vertex_count": 3,
        "instance_count": 1,
    })
)

horizontal_render_pass.end()

# pass2:
vertical_render_pass = encoder.begin_render_pass(vertical_render_pass_desc)

vertical_root = vertical_render_pass.bind_pipeline(vertical_pipeline)

vertical_cursor = spy.ShaderCursor(vertical_root)

vertical_render_pass.set_render_state(render_state)

vertical_cursor.find_field("inputTexture").write(intermediate_texture)
vertical_cursor.find_field("inputSampler").write(sampler)

vertical_render_pass.draw(
    spy.DrawArguments({
            "vertex_count": 3,
            "instance_count": 1,
        })
)

vertical_render_pass.end()
# ==========================
# Submit Commands to GPU
# ==========================

command_buffer = encoder.finish()

# device.submit(command_buffer)

submission_id = device.submit_command_buffer(command_buffer)
device.wait_for_submit(submission_id)

print("GPU execution completed")


# =========================
# Read back the rendered image
# =========================

output_data = render_target.to_numpy()


# Convert BGRA to RGBA
output_data = output_data[..., [2, 1, 0, 3]]  # Swap B and R channels

output_data = np.ascontiguousarray(output_data)


# Save the output image
output_image = Image.fromarray(output_data, mode="RGBA")

#======================================================================================Change Output File Name Here=========================================================================================
Outputs_dir = Path("Outputs")
Outputs_dir.mkdir(parents=True, exist_ok=True)
Outputs_path = Outputs_dir / "TwoPassGaussianBlur.png"  # Change the output file name here
output_image.save(Outputs_path)

# print("program completed, output saved as GaussianBlur.png")