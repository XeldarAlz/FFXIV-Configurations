/////////////////////////////////  MIT LICENSE  ////////////////////////////////

//  Copyright (C) 2025 Edward Jeffrey
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to
//  deal in the Software without restriction, including without limitation the
//  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
//  sell copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//  
//  The above copyright notice and this permission notice shall be included in
//  all copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
//  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
//  IN THE SOFTWARE.

// The upsampling and downsampling code in this shader are modified from the 
// FXShaders project by Lucas Melo, specifically the VirtualResolution shader, 
// which is originally licensed under the following MIT license:

// Copyright (c) 2017 Lucas Melo

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#ifndef CROP_SCALE_UPFILTER
#define CROP_SCALE_UPFILTER POINT
#endif

#ifndef CROP_SCALE_DOWNFILTER
#define CROP_SCALE_DOWNFILTER POINT
#endif

#ifndef CROP_SCALE_UPFILTER
#define CROP_SCALE_UPFILTER LINEAR
#endif

#ifndef CROP_SCALE_DOWNFILTER
#define CROP_SCALE_DOWNFILTER LINEAR
#endif


#ifndef CONTENT_WIDTH
#define CONTENT_WIDTH BUFFER_WIDTH
#endif

#ifndef CONTENT_HEIGHT
#define CONTENT_HEIGHT BUFFER_HEIGHT
#endif


uniform float fFinalResolutionX <
    ui_label = "Final Resolution Width";
    ui_type  = "drag";
    ui_min   = 1.0;
    ui_max   = BUFFER_WIDTH;
    ui_step  = 1.0;
> = BUFFER_WIDTH;

uniform float fFinalResolutionY <
    ui_label = "Final Resolution Height";
    ui_type  = "drag";
    ui_min   = 1.0;
    ui_max   = BUFFER_HEIGHT;
    ui_step  = 1.0;
> = BUFFER_HEIGHT;

uniform float fIntermediateResolutionX <
    ui_label = "Intermediate Resolution Width";
    ui_type  = "drag";
    ui_min   = 1.0;
    ui_max   = BUFFER_WIDTH;
    ui_step  = 1.0;
> = BUFFER_WIDTH;

uniform float fIntermediateResolutionY <
    ui_label = "Intermediate Resolution Height";
    ui_type  = "drag";
    ui_min   = 1.0;
    ui_max   = BUFFER_HEIGHT;
    ui_step  = 1.0;
> = BUFFER_HEIGHT;

uniform float ContentX <
    ui_label = "Content Width";
    ui_type  = "drag";
    ui_min   = 1.0;
    ui_max   = BUFFER_WIDTH;
    ui_step  = 1.0;
> = BUFFER_WIDTH;

uniform float ContentY <
    ui_label = "Content Height";
    ui_type  = "drag";
    ui_min   = 1.0;
    ui_max   = BUFFER_HEIGHT;
    ui_step  = 1.0;
> = BUFFER_HEIGHT;

texture BackBufferTex : COLOR;

sampler CropScaleDownSampler {
    Texture   = BackBufferTex;
    MinFilter = CROP_SCALE_DOWNFILTER;
    MagFilter = CROP_SCALE_DOWNFILTER;
    AddressU  = BORDER;
    AddressV  = BORDER;
};

sampler CropScaleUpSampler {
    Texture   = BackBufferTex;
    MinFilter = CROP_SCALE_UPFILTER;
    MagFilter = CROP_SCALE_UPFILTER;
    AddressU  = BORDER;
    AddressV  = BORDER;
};

void ScreenVS(
    in uint id : SV_VertexID,
    out float4 pos : SV_Position,
    out float2 uv : TEXCOORD)
{
    float2 vertices[3] = {
        float2(-1.0,  1.0),
        float2(-1.0, -3.0),
        float2( 3.0,  1.0)
    };

    float2 texcoords[3] = {
        float2(0.0, 0.0),
        float2(0.0, 2.0),
        float2(2.0, 0.0)
    };

    pos = float4(vertices[id], 0.0, 1.0);
    uv  = texcoords[id];
}



float4 CropDownSamplePS(float4 pos : SV_POSITION, float2 uv : TEXCOORD) : SV_Target
{
    float2 screenSize = float2(BUFFER_WIDTH, BUFFER_HEIGHT);
    float2 contentSize = float2(ContentX, ContentY);
    float2 outputSize = float2(fIntermediateResolutionX, fIntermediateResolutionY);
    float2 screenCenter = 0.5;

    float2 contentSizeUV = contentSize / screenSize;
    float2 contentMin = screenCenter - contentSizeUV * 0.5;

    float2 outputSizeUV = outputSize / screenSize;
    float2 outputMin = screenCenter - outputSizeUV * 0.5;
    float2 outputMax = screenCenter + outputSizeUV * 0.5;

    if (any(uv < outputMin) || any(uv > outputMax))
        return 0.0;

    float2 localUV = (uv - outputMin) / (outputMax - outputMin);
    float2 srcUV = contentMin + localUV * contentSizeUV;

    return tex2D(CropScaleDownSampler, srcUV);
}

float4 CropUpSamplePS(float4 pos : SV_POSITION, float2 uv : TEXCOORD) : SV_Target
{
    float2 screenSize = float2(BUFFER_WIDTH, BUFFER_HEIGHT);
    float2 inputSize = float2(fIntermediateResolutionX, fIntermediateResolutionY);
    float2 outputSize = float2(fFinalResolutionX, fFinalResolutionY);
    float2 screenCenter = 0.5;

    float2 inputSizeUV = inputSize / screenSize;
    float2 outputSizeUV = outputSize / screenSize;
    float2 outputMin = screenCenter - outputSizeUV * 0.5;
    float2 outputMax = screenCenter + outputSizeUV * 0.5;

    if (any(uv < outputMin) || any(uv > outputMax))
        return 0.0;

    float2 localUV = (uv - outputMin) / (outputMax - outputMin);
    float2 srcUV = screenCenter - inputSizeUV * 0.5 + localUV * inputSizeUV;

    return tex2D(CropScaleUpSampler, srcUV);
}

technique CropScale
{
    pass DownSample
    {
        VertexShader = ScreenVS;
        PixelShader  = CropDownSamplePS;
    }

    pass UpSample
    {
        VertexShader = ScreenVS;
        PixelShader  = CropUpSamplePS;
    }
}


