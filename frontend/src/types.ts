export interface PropertyMedia {
  id: number
  url: string
  media_type: 'IMAGE' | 'PANORAMA'
  mime_type: string
  is_primary: boolean
}

export interface Property {
  id: number
  title: string
  description: string
  region: string
  neighborhood: string
  address: string
  bedrooms: number
  bathrooms: number
  amenities: string[]
  monthly_rent_ghs: number
  available_from: string | null
  is_verified: boolean
  is_available: boolean
  has_virtual_tour: boolean
  media: PropertyMedia[]
}

export interface PropertySearchResponse {
  items: Property[]
  page: number
  per_page: number
  total: number
  pages: number
}
