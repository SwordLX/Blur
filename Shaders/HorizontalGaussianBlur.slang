#include "Vertex.slang"

Texture2D<float4> inputTexture : register(t0);
SamplerState inputSampler : register(s0);

[shader("fragment")]
float4 FragmentMain(VertexOutput input) : SV_Target
{
    const int blurRadius = 3;  //================================================= Change blur radius and sigma here ============================================
    const float sigma = 2.0;

    uint width, height;
    inputTexture.GetDimensions(width, height);

    //one texel in the horizontal direction
    float2 texelOffset = float2(1.0/width, 0.0);

    float4 color = float4(0.0);
    float totalWeight = 0.0;

    //Start Loop
    for(int x =  -blurRadius; x<= blurRadius; x++)
    {
        // Calculate the 1D Gaussian weight
        float distanceSquare = float(x * x);
        float weight = exp(
            -distanceSquare/(2.0 * sigma * sigma)
        );

        // Calculate Offset
        float2 offset = float(x) * texelOffset;

        color += inputTexture.Sample(inputSampler, input.uv + offset) * weight;
        totalWeight += weight;
    }

    return color/totalWeight;
    
}