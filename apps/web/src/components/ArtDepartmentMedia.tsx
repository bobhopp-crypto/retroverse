import { useEffect, useState } from 'react'

type ArtDepartmentMediaProps = {
  src: string | null
  alt: string
  fallbackLabel: string
}

export default function ArtDepartmentMedia({ src, alt, fallbackLabel }: ArtDepartmentMediaProps) {
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    setFailed(false)
  }, [src])

  if (!src || failed) {
    return (
      <div className="art-media-fallback" aria-label={alt}>
        <span>{fallbackLabel}</span>
      </div>
    )
  }

  return <img src={src} alt={alt} loading="lazy" onError={() => setFailed(true)} />
}
