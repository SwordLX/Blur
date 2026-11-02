
#include "Vertex.slang"

Texture2D<float4> inputTexture;
Texture2D<float4> noiseTexture;

SamplerState inputSampler;
SamplerState noiseSampler;

cbuffer BlurParams
{
    float blurStrength;
};

[shader("fragment")]
float4 FragmentMain(VertexOutput input) : SV_Target
{
    static const float alphaThreshold = 0.0;
    static const float randomValue = 1.0;
    static const float temporalSampleIndex = 0.0;

    uint width, height;
    inputTexture.GetDimensions(width, height);

    // Calculate screen pixel position
    float2 pixelPosition = input.uv * float2(width, height);

    // Generate the procedural dither pattern
    float2 p = pixelPosition + float2(
        temporalSampleIndex,
        temporalSampleIndex
    );

    uint pattern = (uint(p.x) + 2u * uint(p.y)) % 5u;

    // Sample the 64x64 noise texture
    float2 noiseUV = frac(pixelPosition / 64.0);

    float4 noise = noiseTexture.Sample(
        noiseSampler,
        noiseUV
    );

    // Combine procedural and texture noise
    float randomNoise = noise.r * noise.g * randomValue;

    float dither = (float(pattern) + randomNoise) / 6.0;

    // Apply alpha threshold
    float result = dither + alphaThreshold - 0.5;

    // Distort the input UV coordinates
    float2 distortedUV1 = input.uv + result * blurStrength;
    float2 distortedUV2 = input.uv + (result + 0.15) * blurStrength;


    // Sample the original image
    float4 color1 = inputTexture.Sample(
        inputSampler,
        distortedUV1
    );

    float4 color2 = inputTexture.Sample(
        inputSampler,
        distortedUV2
    );

    return (color1 + color2) * 0.5;
}
