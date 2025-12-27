
#pragma once

#include "ReShade.fxh"

/*------------------.
| :: DEFINITIONS :: |
'------------------*/

#define PI 3.14159265359
#define EPSILON 1e-6

/*--------------.
| :: UNIFORMS ::|
'--------------*/

// Built-in temporal uniforms
uniform float TIMER < source = "timer"; >;
uniform float FRAME_TIME < source = "frametime"; >;
uniform int FRAME_COUNT < source = "framecount"; >;

/*--------------.
| :: HELPERS :: |
'--------------*/

bool CheckerboardSkip(uint2 currentPos, float scale)
{
    // Map current buffer pixel to Full Screen pixel. Use floor to ensure we snap to the integer grid of the full screen
    uint2 fullScreenPos = uint2(floor(currentPos.x * scale), floor(currentPos.y * scale));
    return (((fullScreenPos.x + fullScreenPos.y + (FRAME_COUNT & 1)) & 1) == 1);
}

float GetDepth(float2 uv)
{
	return ReShade::GetLinearizedDepth(uv);
}
