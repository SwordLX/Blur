#include "Vertex.slang"

Texture2D<float4> inputTexture : register(t0);
SamplerState inputSampler : register(s0);


[shader("fragment")]
float4 FragmentMain(VertexOutput input) : SV_TARGET
{

    const int blurRadius = 3;  //================================================ You can change the kernel radius here ===================================================================

    // 1. Get input texture size
    uint width;
    uint height;
    inputTexture.GetDimensions(width, height);

    //2. calculate the pixel size in UV space
    float2 pixelSize = float2(1.0 / width, 1.0 / height);

    //3. Accumulate samples
    float4 color = float4(0.0, 0.0, 0.0, 0.0);


    for (int x = -blurRadius; x <= blurRadius; ++x)
    {
        for (int y = -blurRadius; y <= blurRadius; ++y)
        {
            float2 offset = float2(x, y) * pixelSize;
            color += inputTexture.Sample(inputSampler, input.uv + offset);
        }

    }

    // average the samples
    int kernelSize = 2 * blurRadius + 1;
    float sampleCount = float(kernelSize * kernelSize);
    return color / sampleCount;

}