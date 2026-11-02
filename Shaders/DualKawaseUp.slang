#include "Vertex.slang"

Texture2D<float4> inputTexture : register(t0);
SamplerState inputSampler : register(s0);

cbuffer BlurParams
{
    float blurOffset;
}

[shader("fragment")]
float4 FragmentMain(VertexOutput input) : SV_Target
{
    uint width, height;
    inputTexture.GetDimensions(width, height);

    // Calculate the size of one texel in UV Space
    float2 texelSize = 1.0/float2(width, height);

    // Calculate the sample distance
    float2 offset = texelSize * blurOffset * 0.5;

    float4 color = float4(0.0);

    // Four axis-aligned samples (weight = 2)
    color += inputTexture.Sample(
        inputSampler, input.uv + float2(-offset.x, 0.0)
    ) * 2.0;

    color += inputTexture.Sample(
        inputSampler, input.uv + float2( offset.x, 0.0)
    ) * 2.0;

    color += inputTexture.Sample(
        inputSampler, input.uv + float2(0.0, -offset.y)
    ) * 2.0;

    color += inputTexture.Sample(
        inputSampler, input.uv + float2(0.0,  offset.y)
    ) * 2.0;

    // Four diagonal samples (weight = 1)
    color += inputTexture.Sample(
        inputSampler, input.uv + float2(-offset.x, -offset.y)
    );

    color += inputTexture.Sample(
        inputSampler, input.uv + float2( offset.x, -offset.y)
    );

    color += inputTexture.Sample(
        inputSampler, input.uv + float2(-offset.x,  offset.y)
    );

    color += inputTexture.Sample(
        inputSampler, input.uv + float2( offset.x,  offset.y)
    );

    // Normalize the total weight
    return color / 12.0;

}