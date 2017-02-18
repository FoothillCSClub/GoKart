//------------------------------------------------------------------------------
// <copyright file="Depth-D3D.h" company="Microsoft">
//     Copyright (c) Microsoft Corporation.  All rights reserved.
// </copyright>
//------------------------------------------------------------------------------

#pragma once

#include <windows.h>

// This file requires the installation of the DirectX SDK, a link for which is included in the Toolkit Browser
#include <d3d11.h>
#include <DirectXMath.h>
#include <DirectXPackedVector.h>

#include "NuiApi.h"

#include "Camera.h"
#include "DX11Utils.h"
#include "resource.h"

using namespace DirectX;

static const int		    		    _MaxPlayerIndices = 8;

/// <summary>
/// Constant buffer for shader
/// </summary>
struct CBChangesEveryFrame
{
    XMMATRIX ViewProjection;
    XMVECTOR PlayerDepthMinMax[_MaxPlayerIndices];

    XMFLOAT4 XYScale;
};

class CDepthD3D
{
    static const NUI_IMAGE_RESOLUTION   cDepthResolution = NUI_IMAGE_RESOLUTION_640x480;

public:
    /// <summary>
    /// Constructor
    /// </summary>
    CDepthD3D();

    /// <summary>
    /// Destructor
    /// </summary>
    ~CDepthD3D();

    /// <summary>
    /// Register class and create window
    /// </summary>
    /// <returns>S_OK for success, or failure code</returns>
    HRESULT                             InitWindow(HINSTANCE hInstance, int nCmdShow);

    /// <summary>
    /// Create Direct3D device and swap chain
    /// </summary>
    /// <returns>S_OK for success, or failure code</returns>
    HRESULT                             InitDevice();

    /// <summary>
    /// Create the first connected Kinect found 
    /// </summary>
    /// <returns>S_OK on success, otherwise failure code</returns>
    HRESULT                             CreateFirstConnected();
 
    /// <summary>
    /// Renders a frame
    /// </summary>
    /// <returns>S_OK for success, or failure code</returns>
    HRESULT                             Render();

    /// <summary>
    /// Handles window messages, used to process input
    /// </summary>
    /// <param name="hWnd">window message is for</param>
    /// <param name="uMsg">message</param>
    /// <param name="wParam">message data</param>
    /// <param name="lParam">additional message data</param>
    /// <returns>result of message processing</returns>
    LRESULT HandleMessages(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

private:
    // 3d camera
    CCamera                             m_camera;

    HINSTANCE                           m_hInst;
    HWND                                m_hWnd;
    D3D_FEATURE_LEVEL                   m_featureLevel;
    ID3D11Device*                       m_pd3dDevice;
    ID3D11DeviceContext*                m_pImmediateContext;
    IDXGISwapChain*                     m_pSwapChain;
    ID3D11RenderTargetView*             m_pRenderTargetView;
    ID3D11Texture2D*                    m_pDepthStencil;
    ID3D11DepthStencilView*             m_pDepthStencilView;
    ID3D11InputLayout*                  m_pVertexLayout;
    ID3D11Buffer*                       m_pVertexBuffer;
    ID3D11Buffer*                       m_pCBChangesEveryFrame;
    XMMATRIX                            m_projection;

    ID3D11VertexShader*                 m_pVertexShader;
    ID3D11PixelShader*                  m_pPixelShader;
    ID3D11GeometryShader*               m_pGeometryShader;

    LONG                                m_depthWidth;
    LONG                                m_depthHeight;
    
    float                               m_xyScale;

    // Initial window resolution
    int                                 m_windowResX;
    int                                 m_windowResY;

    // Kinect
    INuiSensor*                         m_pNuiSensor;
    HANDLE                              m_hNextDepthFrameEvent;
    HANDLE                              m_pDepthStreamHandle;

    float						   	    m_minPlayerDepth[_MaxPlayerIndices];
    float								m_maxPlayerDepth[_MaxPlayerIndices];

    // for passing depth data as a texture
    ID3D11Texture2D*                    m_pDepthTexture2D;
    ID3D11ShaderResourceView*           m_pDepthTextureRV;

    bool                                m_bNearMode;

    // if the application is paused, for example in the minimized case
    bool                                m_bPaused;

    /// <summary>
    /// Toggles between near and default mode
    /// Does nothing on a non-Kinect for Windows device
    /// </summary>
    /// <returns>S_OK for success, or failure code</returns>
    HRESULT                             ToggleNearMode();

    /// <summary>
    /// Process depth data received from Kinect
    /// </summary>
    /// <returns>S_OK for success, or failure code</returns>
    HRESULT                             ProcessDepth();

    /// <summary>
    /// Compile and set layout for shaders
    /// </summary>
    /// <returns>S_OK for success, or failure code</returns>
    HRESULT                             LoadShaders();
};