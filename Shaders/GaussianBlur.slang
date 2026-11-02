#include "Vertex.slang"

Texture2D<float4> inputTexture : register(t0);
SamplerState inputSampler : register(s0);


[shader("fragment")]
float4 FragmentMain(VertexOutput input) : SV_Target
{
    const int blurRadius = 3;            // ============================================= Change Blur Radius and Sigma Here ==========================================================
    const float sigma = 2.0;

    uint width, height;
    inputTexture.GetDimensions(width, height);

    // Calculate pixel size
    float2 texelSize = 1.0 / float2(width, height);

    float4 color = float4(0.0);
    float totalWeight = 0.0;

    //Start Sampling Texture
    for(int y = -blurRadius; y<= blurRadius; y++){

        for(int x = -blurRadius; x<= blurRadius; x++){

            // Calculate the Gaussian Weight based on Distance
            float distanceSquared = float(x*x + y*y);
            float weight = exp(
                -distanceSquared /(2.0 * sigma * sigma)
            );

            // Sample the texture and accumulate weighted color
            float2 offset = float2(x,y) * texelSize;
            color += inputTexture.Sample(inputSampler, input.uv + offset) * weight;

            // Accumulate the weight for normalization
            totalWeight += weight;
        }
    }

    return color/totalWeight;

}
