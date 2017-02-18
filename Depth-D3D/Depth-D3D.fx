//------------------------------------------------------------------------------
// <copyright file="Depth-D3D.fx" company="Microsoft">
//     Copyright (c) Microsoft Corporation.  All rights reserved.
// </copyright>
//------------------------------------------------------------------------------

Texture2D<int> txDepth : register(t0);

//--------------------------------------------------------------------------------------
// Constant Buffer Variables
//--------------------------------------------------------------------------------------
cbuffer cbChangesEveryFrame : register(b0)
{
    matrix  ViewProjection;
    float4  playerDepthMinMax[8];
    float4  XYScale;
};

//--------------------------------------------------------------------------------------
// Constants
//--------------------------------------------------------------------------------------
static const float4 playerColorCoefficients[8] = 
{
    float4(1.0,  1.0,  1.0,  1.0), 
    float4(1.4,  0.8,  0.8,  1.0),
    float4(0.8,  1.4,  0.8,  1.0),
    float4(0.8,  0.8,  1.4,  1.0),
    float4(0.6,  1.2,  1.2,  1.0),
    float4(1.2,  0.6,  1.2,  1.0),
    float4(1.2,  1.2,  0.6,  1.0),
    float4(1.3,  0.9,  0.8,  1.0)
};

static const int DepthWidth = 640;
static const int DepthHeight = 480;
static const float2 DepthWidthHeight = float2(DepthWidth, DepthHeight);
static const float2 DepthHalfWidthHeight = DepthWidthHeight / 2.0;
static const float2 DepthHalfWidthHeightOffset = DepthHalfWidthHeight - 0.5;

// vertex offsets for building a quad from a depth pixel
static const float2 quadOffsets[4] = 
{
    float2(0,   0  ),
    float2(1.0, 0  ),
    float2(0,   1.0),
    float2(1.0, 1.0)
};

// texture lookup offsets for sampling current and nearby depth pixels
static const int3 texOffsets4Samples[4] =
{
    int3(0, 0, 0),
    int3(1, 0, 0),
    int3(0, 1, 0),
    int3(1, 1, 0)
};

//--------------------------------------------------------------------------------------
// Structures
//--------------------------------------------------------------------------------------
struct GS_INPUT
{
};

struct PS_INPUT
{
    float4 Pos : SV_POSITION;
    float4 Col : COLOR;
};

//--------------------------------------------------------------------------------------
// Vertex Shader
//--------------------------------------------------------------------------------------
GS_INPUT VS( )
{
    GS_INPUT output = (GS_INPUT)0;
 
    return output;
}

//--------------------------------------------------------------------------------------
// Geometry Shader
// 
// Takes in a single vertex point.  Expands it into the 4 vertices of a quad.
// Depth is sampled from a texture passed in of the Kinect's depth output.
//--------------------------------------------------------------------------------------
[maxvertexcount(4)]
void GS(point GS_INPUT particles[1], uint primID : SV_PrimitiveID, inout TriangleStream<PS_INPUT> triStream)
{
    PS_INPUT output;

    // use the minimum of near mode and standard
    static const int minDepth = 300 << 16;

    // use the maximum of near mode and standard
    static const int maxDepth = 4000 << 16;

    // texture load location for the pixel we're on 
    int3 baseLookupCoords = int3(primID % DepthWidth, primID / DepthWidth, 0);

    int4 depths;
    depths[0] = txDepth.Load(baseLookupCoords);
    depths[1] = txDepth.Load(baseLookupCoords + texOffsets4Samples[1]);
    depths[2] = txDepth.Load(baseLookupCoords + texOffsets4Samples[2]);
    depths[3] = txDepth.Load(baseLookupCoords + texOffsets4Samples[3]);
    
    // remove player index information
    float4 realDepths = depths / 65536.0;

    float4 avgDepth = (realDepths[0] + realDepths[1] + realDepths[2] + realDepths[3]) / 4.0; 
    
    // test the difference between each of the depth values and the average
    // if any deviate by the cutoff or more, don't generate this quad
    static const float joinCutoff = 20.0;
    float4 depthDev = abs(realDepths - avgDepth);
    float4 branch = step(joinCutoff, depthDev);

    if ( any(branch) )
    {
        return;
    }

    // constant for all c
    int player = depths[0] & 0x7;

    float4 baseColor = playerColorCoefficients[player];

    // log scale to push brighter
    // normalize z to between 0 and 1, where 0 is min depth and 1 is max depth
    // log2 of player depth max-min is precomputed and passed into the z component of playerDepthMinMax
    // flip by subtracting it from 1.0 to make closer brighter
    float4 zNormalized = 1.0 - log2(realDepths - playerDepthMinMax[player].x) / playerDepthMinMax[player].w;

    // convert realDepths to meters
    realDepths /= 1000.0;

    // set the w coordinate here so we don't have to do it per vertex
    float4 WorldPos = float4(0.0, 0.0, 0.0, 1.0);
    
    // Likely will be unrolled, but force anyway
    [unroll]
    for (int c = 0; c < 4; ++c)
    {      
        // convert x and y to meters
        WorldPos.xy = ((baseLookupCoords + quadOffsets[c]) - DepthHalfWidthHeightOffset) * XYScale.xy * realDepths[c];
        WorldPos.z = realDepths[c];
             
        output.Pos = mul(WorldPos, ViewProjection);
            
        // closer is brighter
        output.Col = zNormalized[c];

        // add this vertex to the triangle strip
        triStream.Append(output);
    }
}

//--------------------------------------------------------------------------------------
// Pixel Shader
//--------------------------------------------------------------------------------------
float4 PS(PS_INPUT input) : SV_Target
{
    return input.Col;
}