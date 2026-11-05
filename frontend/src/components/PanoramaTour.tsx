import { useEffect, useRef } from 'react'
import 'pannellum/build/pannellum.css'
import 'pannellum'

declare global {
  interface Window {
    pannellum?: {
      viewer: (container: HTMLElement, config: Record<string, unknown>) => { destroy: () => void }
    }
  }
}

interface PanoramaTourProps {
  imageUrl: string
  title: string
}

export function PanoramaTour({ imageUrl, title }: PanoramaTourProps) {
  const viewerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!viewerRef.current || !window.pannellum) return
    const viewer = window.pannellum.viewer(viewerRef.current, {
      type: 'equirectangular',
      panorama: imageUrl,
      autoLoad: true,
      showControls: true,
      compass: false,
      hfov: 100,
      minHfov: 50,
      maxHfov: 120,
    })
    return () => viewer.destroy()
  }, [imageUrl])

  return <div ref={viewerRef} role="img" aria-label={`360 degree virtual tour of ${title}`} className="h-72 w-full overflow-hidden rounded-2xl bg-stone-200 sm:h-96" />
}
