#include "Vertex.slang"

Texture2D<float4> inputTexture : register(t0);
SamplerState inputSampler : register(s0);


[shader("fragment")]
float4 FragmentMain(VertexOutput input) : SV_TARGET
{
    //Sample the texture using the provided UV coordinates
    float4 color = inputTexture.Sample(inputSampler, input.uv);
    return color;

    //return float4(input.uv.x, input.uv.y, 0.0, 1.0);
}