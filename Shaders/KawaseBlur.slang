#include "Vertex.slang"

Texture2D<float4> inputTexture : register(t0);
SamplerState inputSampler : register(s0);

// Blur Parameters
cbuffer BlurParams
{
    float blurOffset;
}

[shader("fragment")]
float4 FragmentMain(VertexOutput input) : SV_TARGET
{

    uint width, height;
    inputTexture.GetDimensions(width, height);

    // Calculate the size of one texel in UV Space
    float2 texelSize = 1.0/float2(width, height);

    // Calculate the sample distance
    float2 offset = texelSize * blurOffset;

    // Sample four diagonal positions
    float4 color = float4(0.0);

    color += inputTexture.Sample(inputSampler, input.uv + float2(-offset.x, -offset.y));
    color += inputTexture.Sample(inputSampler, input.uv + float2(offset.x, -offset.y));
    color += inputTexture.Sample(inputSampler, input.uv + float2(-offset.x, offset.y));
    color += inputTexture.Sample(inputSampler, input.uv + float2(offset.x, offset.y));

    // Average the four samples
    return color * 0.25;
}