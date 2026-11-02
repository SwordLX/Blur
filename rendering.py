import slangpy as spy

# ==============================================
# Create Graphics Pipeline
# ==============================================

def create_pipeline(device, program, target_format):
    return device.create_render_pipeline(
        program = program,
        input_layout = None,
        primitive_topology = spy.PrimitiveTopology.triangle_list,
        targets=[
            spy.ColorTargetDesc({"format": target_format})
            ],
        rasterizer = spy.RasterizerDesc({
            "cull_mode": spy.CullMode.none,
        })
    )


# ==================================================
# Create Render Pass Description
# ==================================================

def create_render_pass_desc(texture):
    texture_view = texture.create_view()

    attachment = spy.RenderPassColorAttachment({
        "view": texture_view,
        "load_op": spy.LoadOp.clear,
        "store_op": spy.StoreOp.store,
        "clear_value": (0.0, 0.0, 0.0, 1.0)
    })

    pass_desc = spy.RenderPassDesc({
        "color_attachments": [attachment]
    })

    return pass_desc, texture_view, attachment


# ====================================================
# Create Render State
# ====================================================

def create_render_state(width, height):
    return spy.RenderState({
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

# ===============================================
# Draw Fullscreen Triangle
# ===============================================

def draw_fullscreen(encoder, pass_desc, pipeline, input_texture, sampler, render_state, 
                    blur_offset = None,
                    noise_texture = None,
                    noise_sampler = None,
                    blur_strength = None
                    ):
    
    render_pass = encoder.begin_render_pass(pass_desc)

    root = render_pass.bind_pipeline(pipeline)
    cursor = spy.ShaderCursor(root)

    #bind Shader Resources
    cursor.find_field("inputTexture").write(input_texture)
    cursor.find_field("inputSampler").write(sampler)

    # Bind Kawase blur parameter if provided
    if blur_offset is not None:
        cursor.find_field("BlurParams").find_field("blurOffset").write(float(blur_offset))


    # bind Dither blur parameter if provided
    if noise_texture is not None:
        cursor.find_field("noiseTexture").write(noise_texture)

    if noise_sampler is not None:
        cursor.find_field("noiseSampler").write(noise_sampler)

    if blur_strength is not None:
        cursor.find_field("BlurParams").find_field("blurStrength").write(float(blur_strength))
    
    # configure viewport and scissor
    render_pass.set_render_state(render_state)

    #draw fullscreen triangle
    render_pass.draw(
        spy.DrawArguments({
                    "vertex_count": 3,
                    "instance_count": 1,
                })
    )

    render_pass.end()