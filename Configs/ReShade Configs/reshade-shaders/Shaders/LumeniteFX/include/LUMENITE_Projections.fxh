#pragma once

#include "ReShade.fxh"

/*------------------.
| :: DEFINITIONS :: |
'------------------*/

#define FOV 60.0

/*--------------.
| :: HELPERS :: |
'--------------*/

//=== Vertex Shader
struct VSOUT
{
    float4 vpos              : SV_Position;
    float2 uv                : TEXCOORD0;
    float tan_half_fov_x     : TEXCOORD1;
    float tan_half_fov_y     : TEXCOORD2;
    float far_plane          : TEXCOORD3;
    float inv_tan_half_fov_x : TEXCOORD4;
    float inv_tan_half_fov_y : TEXCOORD5;
};

#define TAN_HALF_FOV_Y tan(radians(FOV * 0.5))
#define ASPECT_RATIO_X_OVER_Y ((float)BUFFER_WIDTH / (float)BUFFER_HEIGHT)
#define TAN_HALF_FOV_X TAN_HALF_FOV_Y * ASPECT_RATIO_X_OVER_Y
#define INV_TAN_HALF_FOV_X rcp(TAN_HALF_FOV_X)
#define INV_TAN_HALF_FOV_Y rcp(TAN_HALF_FOV_Y)

VSOUT VS(uint id : SV_VertexID)
{
    VSOUT o;
    o.uv.x = (id == 2) ? 2.0 : 0.0;
    o.uv.y = (id == 1) ? 2.0 : 0.0;
    o.vpos = float4(mad(o.uv.x, 2.0, -1.0), mad(o.uv.y, -2.0, 1.0), 0.0, 1.0);
    o.tan_half_fov_x = TAN_HALF_FOV_X;
    o.tan_half_fov_y = TAN_HALF_FOV_Y;
    o.inv_tan_half_fov_x = INV_TAN_HALF_FOV_X;
    o.inv_tan_half_fov_y = INV_TAN_HALF_FOV_Y;
    o.far_plane = RESHADE_DEPTH_LINEARIZATION_FAR_PLANE;
    return o;
}

//=== Projection Functions
float3 UVToViewSpace(float2 uv, float linear_depth_vs, VSOUT ps_input)
{
    float3 view_pos;
    float ndc_x = mad(uv.x, 2.0, -1.0);
    float ndc_y = mad(uv.y, -2.0, 1.0);

    view_pos.x = ndc_x * ps_input.tan_half_fov_x * linear_depth_vs;
    view_pos.y = ndc_y * ps_input.tan_half_fov_y * linear_depth_vs;
    view_pos.z = linear_depth_vs;
    return view_pos;
}

float2 ViewSpaceToUV(float3 view_pos, VSOUT ps_input)
{
    float2 ndc;
    float inv_z = rcp(view_pos.z);
    ndc.x = view_pos.x * inv_z * ps_input.inv_tan_half_fov_x;
    ndc.y = view_pos.y * inv_z * ps_input.inv_tan_half_fov_y;
    float2 uv;
    uv.x = mad(ndc.x, 0.5, 0.5);
    uv.y = mad(ndc.y, -0.5, 0.5);
    return uv;
}
