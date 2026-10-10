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
      stars = Array.from({ length: Math.max(72, Math.min(150, Math.floor(width * height / 10500))) }, (_, index) => {
        const seed = (index * 9301 + 49297) % 233280
        return {
          x: ((seed / 233280) * width),
          y: (((seed * 17 % 233280) / 233280) * height),
          radius: 0.35 + ((seed * 29 % 100) / 100) * 0.8,
          alpha: 0.22 + ((seed * 13 % 100) / 100) * 0.52,
          speed: 2 + ((seed * 7 % 100) / 100) * 5,
        }
      })
      draw(0)
    }

    const draw = (elapsed: number) => {
      if (!context) return
      const delta = Math.min(elapsed, 40) / 1000
      context.fillStyle = '#050505'
      context.fillRect(0, 0, width, height)
      for (const star of stars) {
        if (!reducedMotion && active) star.y = (star.y + star.speed * delta) % Math.max(height, 1)
        context.globalAlpha = star.alpha
        context.fillStyle = '#e9eef2'
        context.beginPath()
        context.arc(star.x, star.y, star.radius, 0, Math.PI * 2)
        context.fill()
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
