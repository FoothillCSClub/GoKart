//------------------------------------------------------------------------------
// <copyright file="Camera.h" company="Microsoft">
//     Copyright (c) Microsoft Corporation.  All rights reserved.
// </copyright>
//------------------------------------------------------------------------------

#pragma once

#include <windows.h>
#include <DirectXMath.h>
#include <DirectXPackedVector.h>

using namespace DirectX;

class CCamera
{
public:
    XMMATRIX View;

    /// <summary>
    /// Constructor
    /// </summary>
    CCamera();

    /// <summary>
    /// Handles window messages, used to process input
    /// </summary>
    /// <param name="hWnd">window message is for</param>
    /// <param name="uMsg">message</param>
    /// <param name="wParam">message data</param>
    /// <param name="lParam">additional message data</param>
    /// <returns>result of message processing</returns>
    LRESULT HandleMessages(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

    /// <summary>
    /// Reset the camera state to initial values
    /// </summary>
    void Reset();

    /// <summary>
    /// Update the view matrix
    /// </summary>
    void Update();

    /// <summary>
    /// Get the camera's up vector
    /// </summary>
    /// <returns>camera's up vector</returns>
    XMVECTOR  GetUp() { return m_up; }

    /// <summary>
    /// Get the camera's right vector
    /// </summary>
    /// <returns>camera's right vector</returns>
    XMVECTOR  GetRight() { return m_right; }

    /// <summary>
    /// Get the camera's position vector
    /// </summary>
    /// <returns>camera's position vector</returns>
    XMVECTOR  GetEye() { return m_eye; }

private:
    float     m_rotationSpeed;
    float     m_movementSpeed;

    float     m_yaw;
    float     m_pitch;

    XMVECTOR  m_eye;
    XMVECTOR  m_at;
    XMVECTOR  m_up;
    XMVECTOR  m_forward;
    XMVECTOR  m_right;

    XMVECTOR  m_atBasis;
    XMVECTOR  m_upBasis;
};