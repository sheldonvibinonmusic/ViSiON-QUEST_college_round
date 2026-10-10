import { useState } from 'react'

const VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260808_112712_da9d53df-6d27-4b12-bdf6-aa9dc2622bdf.mp4'

// Fallback high-contrast dark poster frame svg data URL representing the portal doorway in mist
const POSTER_DATA_URI =
  'data:image/svg+xml;charset=utf-8,' +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1492 1054" width="100%" height="100%">
      <rect width="100%" height="100%" fill="#050505"/>
      <radialGradient id="portalGlow" cx="50%" cy="45%" r="35%">
        <stop offset="0%" stop-color="#ffffff" stop-opacity="0.35"/>
        <stop offset="30%" stop-color="#888888" stop-opacity="0.12"/>
        <stop offset="100%" stop-color="#050505" stop-opacity="0"/>
      </radialGradient>
      <rect width="100%" height="100%" fill="url(#portalGlow)"/>
      <rect x="735" y="280" width="22" height="340" fill="#ffffff" opacity="0.9" filter="drop-shadow(0 0 16px rgba(255,255,255,0.8))"/>
      <ellipse cx="746" cy="625" rx="160" ry="14" fill="#ffffff" opacity="0.18"/>
    </svg>
  `)

export function VideoPlate() {
  const [videoError, setVideoError] = useState(false)

  return (
    <div className="plate" aria-hidden="true">
      {!videoError ? (
        <video
          className="plate-video"
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          poster={POSTER_DATA_URI}
          onError={() => setVideoError(true)}
        >
          <source src={VIDEO_URL} type="video/mp4" />
        </video>
      ) : (
        <img
          src={POSTER_DATA_URI}
          alt=""
          className="plate-video object-cover"
          aria-hidden="true"
        />
      )}
    </div>
  )
}
