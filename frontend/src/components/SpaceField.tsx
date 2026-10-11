import { useEffect, useRef } from 'react'

interface SpaceFieldProps {
  active: boolean
}

interface Star {
  x: number
  y: number
  radius: number
  alpha: number
  speed: number
}

/** Phase 3(d): one low-detail Canvas 2D star layer; beat-specific space graphics follow in 3(e). */
export function SpaceField({ active }: SpaceFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const context = canvas?.getContext('2d', { alpha: false })
    if (!canvas || !context) return

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    let frameId = 0
    let width = 0
    let height = 0
    let lastFrame = 0
    let stars: Star[] = []

    const resize = () => {
      const bounds = canvas.getBoundingClientRect()
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5)
      width = bounds.width
      height = bounds.height
      canvas.width = Math.max(1, Math.round(width * ratio))
      canvas.height = Math.max(1, Math.round(height * ratio))
      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      stars = Array.from({ length: Math.max(80, Math.min(180, Math.floor(width * height / 9500))) }, (_, index) => {
        const seed = (index * 9301 + 49297) % 233280
        return {
          x: ((seed / 233280) * width),
          y: (((seed * 17 % 233280) / 233280) * height),
          radius: 0.35 + ((seed * 29 % 100) / 100) * 0.9,
          alpha: 0.22 + ((seed * 13 % 100) / 100) * 0.58,
          speed: 2 + ((seed * 7 % 100) / 100) * 6,
        }
      })
      draw(0)
    }

    const draw = (elapsed: number) => {
      if (!context) return
      const delta = Math.min(elapsed, 40) / 1000

      // Base space canvas: near-black
      context.fillStyle = '#030712'
      context.fillRect(0, 0, width, height)

      // Draw illuminated planetary curved horizon in lower-left
      const planetX = width * 0.15
      const planetY = height * 1.45
      const planetRadius = Math.max(width, height) * 0.92

      // Outer atmospheric Rayleigh scattering glow
      const glowGrad = context.createRadialGradient(
        planetX,
        planetY,
        planetRadius * 0.95,
        planetX,
        planetY,
        planetRadius * 1.18
      )
      glowGrad.addColorStop(0, 'rgba(56, 189, 248, 0.42)')
      glowGrad.addColorStop(0.25, 'rgba(14, 116, 144, 0.22)')
      glowGrad.addColorStop(0.65, 'rgba(8, 24, 58, 0.14)')
      glowGrad.addColorStop(1, 'rgba(3, 7, 18, 0)')

      context.fillStyle = glowGrad
      context.beginPath()
      context.arc(planetX, planetY, planetRadius * 1.18, 0, Math.PI * 2)
      context.fill()

      // Planet body: deep dark navy to orbital blue edge
      const planetGrad = context.createRadialGradient(
        planetX,
        planetY,
        planetRadius * 0.55,
        planetX,
        planetY,
        planetRadius
      )
      planetGrad.addColorStop(0, '#020611')
      planetGrad.addColorStop(0.85, '#040d21')
      planetGrad.addColorStop(0.96, '#082046')
      planetGrad.addColorStop(1, '#0e3a75')

      context.fillStyle = planetGrad
      context.beginPath()
      context.arc(planetX, planetY, planetRadius, 0, Math.PI * 2)
      context.fill()

      // Luminous ozone rim
      context.strokeStyle = 'rgba(125, 211, 252, 0.65)'
      context.lineWidth = 1.6
      context.beginPath()
      context.arc(planetX, planetY, planetRadius, 0, Math.PI * 2)
      context.stroke()

      // Horizontal star streaming (simulating spacecraft traveling leftward)
      for (const star of stars) {
        if (!reducedMotion && active) {
          star.x = (star.x + star.speed * delta * 20) % Math.max(width, 1)
        }
        context.globalAlpha = star.alpha
        context.fillStyle = '#e9eef2'
        context.beginPath()
        context.arc(star.x, star.y, star.radius, 0, Math.PI * 2)
        context.fill()

        // Subtle motion streak for foreground stars
        if (star.speed > 5) {
          context.strokeStyle = `rgba(229, 238, 245, ${star.alpha * 0.4})`
          context.lineWidth = star.radius * 0.8
          context.beginPath()
          context.moveTo(Math.max(0, star.x - star.speed * 2.2), star.y)
          context.lineTo(star.x, star.y)
          context.stroke()
        }
      }
      context.globalAlpha = 1
    }

    const animate = (now: number) => {
      if (document.hidden || !active || reducedMotion) {
        draw(0)
        frameId = 0
        return
      }
      const elapsed = lastFrame ? now - lastFrame : 16
      lastFrame = now
      draw(elapsed)
      frameId = window.requestAnimationFrame(animate)
    }

    const start = () => {
      if (document.hidden || !active || reducedMotion || frameId) return
      lastFrame = 0
      frameId = window.requestAnimationFrame(animate)
    }
    const onVisibilityChange = () => {
      if (document.hidden && frameId) {
        window.cancelAnimationFrame(frameId)
        frameId = 0
        draw(0)
      } else {
        start()
      }
    }
    const observer = new ResizeObserver(resize)
    observer.observe(canvas)
    document.addEventListener('visibilitychange', onVisibilityChange)
    resize()
    start()

    return () => {
      observer.disconnect()
      document.removeEventListener('visibilitychange', onVisibilityChange)
      if (frameId) window.cancelAnimationFrame(frameId)
    }
  }, [active])

  return <canvas ref={canvasRef} className="scene-space-canvas" aria-hidden="true" />
}
