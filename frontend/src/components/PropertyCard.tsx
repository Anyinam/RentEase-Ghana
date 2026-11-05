import { Bath, BedDouble, BadgeCheck, Camera } from 'lucide-react'
import type { Property } from '../types'

interface PropertyCardProps {
  property: Property
  onSelect: (property: Property) => void
}

const fallbackImage = 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=85'

export function PropertyCard({ property, onSelect }: PropertyCardProps) {
  const image = property.media.find((item) => item.is_primary && item.media_type === 'IMAGE')
    ?? property.media.find((item) => item.media_type === 'IMAGE')
  const availableDate = property.available_from ? new Date(`${property.available_from}T00:00:00`) : null
  const availableLabel = availableDate && availableDate > new Date(new Date().setHours(0, 0, 0, 0))
    ? `Available ${new Intl.DateTimeFormat('en-GH', { day: 'numeric', month: 'short' }).format(availableDate)}`
    : 'Available now'

  return (
    <article className="group overflow-hidden rounded-3xl border border-black/5 bg-white shadow-card transition hover:-translate-y-1">
      <button className="relative block aspect-[1.35] w-full overflow-hidden bg-stone-100 text-left" onClick={() => onSelect(property)} aria-label={`View ${property.title}`}>
        <img src={image?.url ?? fallbackImage} alt={property.title} className="h-full w-full object-cover transition duration-500 group-hover:scale-105" />
        <span className="absolute left-4 top-4 rounded-full bg-white/95 px-3 py-1.5 text-xs font-semibold text-forest">{availableLabel}</span>
        {property.has_virtual_tour && <span className="absolute bottom-4 left-4 inline-flex items-center gap-1.5 rounded-full bg-ink/80 px-3 py-1.5 text-xs font-semibold text-white"><Camera size={14} /> 360° tour</span>}
        <span className="absolute right-4 top-4 rounded-full bg-white/90 p-2 text-forest"><BadgeCheck size={18} fill="currentColor" className="text-forest" /><span className="sr-only">Verified property</span></span>
      </button>
      <button onClick={() => onSelect(property)} className="block w-full p-5 text-left">
        <div className="mb-2 flex items-start justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-muted">{property.neighborhood}, {property.region}</p>
            <h3 className="mt-1 text-lg font-semibold tracking-tight text-ink">{property.title}</h3>
          </div>
          <p className="shrink-0 text-right text-lg font-bold text-ink">GH₵{property.monthly_rent_ghs.toLocaleString()}<span className="block text-xs font-medium text-muted">/ month</span></p>
        </div>
        <div className="mt-4 flex items-center gap-4 border-t border-stone-100 pt-4 text-sm text-muted">
          <span className="inline-flex items-center gap-1.5"><BedDouble size={16} /> {property.bedrooms} beds</span>
          <span className="inline-flex items-center gap-1.5"><Bath size={16} /> {property.bathrooms} baths</span>
          <span className="ml-auto font-medium text-forest">See details</span>
        </div>
      </button>
    </article>
  )
}
