struct VertexOutput
{
    float4 position : SV_POSITION;
    float2 uv : TEXCOORD0;
};

[shader("vertex")]
VertexOutput VertexMain(uint vertexID : SV_VertexID)
{
    VertexOutput output;
    
    // Define a simple quad with positions and UVs
    float2 uv = float2(
        (vertexID << 1) & 2,
        vertexID & 2
    );
    
    output.position = float4(
        uv.x * 2.0f - 1.0f, 
        1.0 - uv.y * 2.0f,
        0.0, 
        1.0f);

    output.uv = uv;

    return output;
}