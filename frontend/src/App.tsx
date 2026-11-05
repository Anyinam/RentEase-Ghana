import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowDownUp, ArrowRight, Check, ChevronDown, LayoutGrid, List, MapPin, Menu, Search, X } from 'lucide-react'
import { searchProperties } from './lib/api'
import type { Property } from './types'
import { PropertyCard } from './components/PropertyCard'
import { PanoramaTour } from './components/PanoramaTour'
import { RnplSimulator } from './components/RnplSimulator'
import { CheckoutDrawer } from './components/CheckoutDrawer'
import { FieldAgentOnboarding } from './components/FieldAgentOnboarding'

const neighborhoods = ['All neighborhoods', 'East Legon', 'Spintex', 'Tema', 'Osu', 'Cantonments', 'Kumasi']

export default function App() {
  const [neighborhood, setNeighborhood] = useState('All neighborhoods')
  const [virtualTourOnly, setVirtualTourOnly] = useState(false)
  const [view, setView] = useState<'grid' | 'list'>('grid')
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null)
  const [checkoutOpen, setCheckoutOpen] = useState(false)
  const [agentFormOpen, setAgentFormOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [serviceFeePercent, setServiceFeePercent] = useState(9)

  const query = useMemo(() => {
    const params = new URLSearchParams({ per_page: '24' })
    if (neighborhood !== 'All neighborhoods') params.set('neighborhood', neighborhood)
    if (virtualTourOnly) params.set('virtual_tour', 'true')
    if (search.trim()) params.set('q', search.trim())
    return params
  }, [neighborhood, virtualTourOnly, search])

  const propertiesQuery = useQuery({
    queryKey: ['properties', query.toString()],
    queryFn: ({ signal }) => searchProperties(query, signal),
  })

  const tour = selectedProperty?.media.find((media) => media.media_type === 'PANORAMA')

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <header className="sticky top-0 z-30 border-b border-black/5 bg-canvas/90 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8" aria-label="Main navigation">
          <a href="#" className="flex items-center gap-2.5" aria-label="RentEase Ghana home">
            <span className="grid h-10 w-10 place-items-center rounded-2xl bg-forest text-lg font-bold text-lime">R</span>
            <span className="text-lg font-bold tracking-tight">rentease<span className="text-forest">.</span><span className="ml-1 text-xs font-semibold text-muted">GHANA</span></span>
          </a>
          <div className="hidden items-center gap-8 text-sm font-medium text-muted md:flex"><a href="#homes" className="text-ink">Find a home</a><a href="#how-it-works">How it works</a><button onClick={() => setAgentFormOpen(true)}>Field agent portal</button></div>
          <button onClick={() => setAgentFormOpen(true)} className="hidden rounded-full bg-forest px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-ink md:block">Agent portal <ArrowRight size={15} className="ml-2 inline" /></button>
          <button onClick={() => setAgentFormOpen(true)} className="rounded-lg p-2 text-ink md:hidden" aria-label="Open menu"><Menu /></button>
        </nav>
      </header>

      <main>
        <section className="relative overflow-hidden bg-forest">
          <div className="absolute -right-32 -top-56 h-[36rem] w-[36rem] rounded-full border border-white/10" /><div className="absolute -right-8 -top-32 h-[28rem] w-[28rem] rounded-full border border-white/10" />
          <div className="relative mx-auto grid max-w-7xl items-center gap-10 px-5 py-16 sm:py-24 lg:grid-cols-[1.05fr_.95fr] lg:px-8 lg:py-28">
            <div className="max-w-2xl text-white">
              <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-lime"><span className="h-1.5 w-1.5 rounded-full bg-lime" /> A better way home in Ghana</span>
              <h1 className="mt-6 text-5xl font-semibold leading-[1.06] tracking-tight sm:text-6xl">Find your place.<br /><span className="text-lime">Pay your way.</span></h1>
              <p className="mt-6 max-w-lg text-base leading-7 text-white/75">A home you love, without the two-year advance. Explore verified homes and pay monthly with Mobile Money.</p>
              <div className="mt-8 flex flex-wrap gap-3 text-sm text-white/80"><span className="flex items-center gap-2"><Check size={16} className="text-lime" /> Verified homes</span><span className="flex items-center gap-2"><Check size={16} className="text-lime" /> Flexible monthly rent</span><span className="flex items-center gap-2"><Check size={16} className="text-lime" /> MoMo-friendly</span></div>
            </div>
            <div className="relative hidden lg:block">
              <div className="absolute -left-7 top-12 z-10 rounded-2xl bg-white p-4 shadow-xl"><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-full bg-lime/60"><MapPin size={18} /></span><div><p className="text-xs text-muted">Popular neighborhood</p><p className="text-sm font-semibold">East Legon, Accra</p></div></div></div>
              <img src="https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=85" alt="Warm modern living room in a Ghanaian home" className="h-[390px] w-full rounded-[2rem] object-cover" />
              <div className="absolute -bottom-5 right-5 rounded-2xl bg-white p-4 shadow-xl"><p className="text-xs text-muted">Homes move-in ready</p><p className="mt-1 text-xl font-bold text-ink">Your next chapter <span className="text-forest">starts here.</span></p></div>
            </div>
          </div>
        </section>

        <section id="homes" className="mx-auto max-w-7xl px-5 py-14 lg:px-8 lg:py-20">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
            <div><p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">Homes for your next chapter</p><h2 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Find a place to call home</h2><p className="mt-3 text-muted">Handpicked and verified homes across Ghana.</p></div>
            <div className="flex items-center gap-2 rounded-full bg-white p-1 shadow-sm" aria-label="Property display mode"><button onClick={() => setView('grid')} aria-label="Grid view" aria-pressed={view === 'grid'} className={`rounded-full p-2.5 ${view === 'grid' ? 'bg-forest text-white' : 'text-muted'}`}><LayoutGrid size={17} /></button><button onClick={() => setView('list')} aria-label="List view" aria-pressed={view === 'list'} className={`rounded-full p-2.5 ${view === 'list' ? 'bg-forest text-white' : 'text-muted'}`}><List size={17} /></button></div>
          </div>
          <div className="mt-8 flex flex-col gap-3 rounded-2xl border border-black/5 bg-white p-3 sm:flex-row">
            <label className="flex flex-1 items-center gap-3 px-3"><Search size={19} className="shrink-0 text-muted" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search neighborhoods or regions" className="w-full py-2 text-sm outline-none placeholder:text-muted" aria-label="Search regions" /></label>
            <span className="hidden w-px bg-stone-200 sm:block" />
            <label className="flex items-center gap-2 px-3 text-sm text-ink"><MapPin size={17} className="text-forest" /><select value={neighborhood} onChange={(event) => setNeighborhood(event.target.value)} className="min-w-40 bg-transparent py-2 outline-none">{neighborhoods.map((item) => <option key={item}>{item}</option>)}</select><ChevronDown size={15} className="text-muted" /></label>
            <button onClick={() => setVirtualTourOnly((value) => !value)} aria-pressed={virtualTourOnly} className={`flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition ${virtualTourOnly ? 'bg-lime text-ink' : 'bg-canvas text-muted'}`}><ArrowDownUp size={15} /> 360° tours</button>
          </div>
          <div className="mt-7 flex items-center justify-between"><p className="text-sm text-muted">{propertiesQuery.data ? `${propertiesQuery.data.total} homes` : 'Explore verified homes'} <span className="hidden sm:inline"> · Monthly pricing, no surprises</span></p><span className="rounded-full bg-lime/50 px-3 py-1 text-xs font-semibold text-ink">Prices in GHS</span></div>

          {propertiesQuery.isLoading && <div className="mt-7 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map((item) => <div key={item} className="aspect-[1.1] animate-pulse rounded-3xl bg-white" />)}</div>}
          {propertiesQuery.isError && <div role="alert" className="mt-7 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-amber-950">We couldn’t connect to the homes service. Please try again in a moment.</div>}
          {propertiesQuery.data && propertiesQuery.data.items.length === 0 && <div className="mt-7 rounded-3xl border border-dashed border-stone-300 bg-white p-12 text-center"><Search className="mx-auto text-muted" /><h3 className="mt-4 text-lg font-semibold">No homes found just yet</h3><p className="mt-2 text-sm text-muted">Try another neighborhood or check back soon.</p></div>}
          {propertiesQuery.data && propertiesQuery.data.items.length > 0 && <div className={`mt-7 gap-5 ${view === 'grid' ? 'grid sm:grid-cols-2 lg:grid-cols-3' : 'grid'}`}>{propertiesQuery.data.items.map((property) => <PropertyCard key={property.id} property={property} onSelect={setSelectedProperty} />)}</div>}
        </section>

        <section id="how-it-works" className="border-y border-black/5 bg-white">
          <div className="mx-auto grid max-w-7xl gap-10 px-5 py-14 lg:grid-cols-[.8fr_1.2fr] lg:px-8 lg:py-20">
            <div><p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">Renting, reimagined</p><h2 className="mt-2 text-3xl font-semibold tracking-tight">More home.<br />Less upfront.</h2><p className="mt-4 max-w-md text-sm leading-6 text-muted">Landlords get the certainty of an advance from RentEase. You get a professionally managed home and the option to pay rent monthly.</p></div>
            <div className="grid gap-4 sm:grid-cols-3">{[['01', 'Explore', 'Find a verified home that fits your life.'], ['02', 'Get verified', 'Complete a transparent affordability review.'], ['03', 'Move in', 'Sign your lease and pay monthly with MoMo.']].map(([number, title, copy]) => <article key={number} className="rounded-2xl bg-canvas p-5"><span className="text-sm font-bold text-forest">{number}</span><h3 className="mt-5 font-semibold">{title}</h3><p className="mt-2 text-sm leading-6 text-muted">{copy}</p></article>)}</div>
          </div>
        </section>
      </main>

      <footer className="mx-auto flex max-w-7xl flex-col gap-3 px-5 py-8 text-sm text-muted sm:flex-row sm:items-center sm:justify-between lg:px-8"><span>© {new Date().getFullYear()} RentEase Ghana</span><span>Clear terms. Verified homes. Your home, your way.</span></footer>

      {selectedProperty && <div className="fixed inset-0 z-40 overflow-y-auto bg-ink/50 p-4 sm:p-8" onMouseDown={(event) => event.target === event.currentTarget && setSelectedProperty(null)}><div className="mx-auto max-w-4xl rounded-3xl bg-canvas p-5 shadow-2xl sm:p-8"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-medium text-forest">{selectedProperty.neighborhood}, {selectedProperty.region}</p><h2 className="mt-1 text-2xl font-semibold">{selectedProperty.title}</h2><p className="mt-2 text-muted">GH₵{selectedProperty.monthly_rent_ghs.toLocaleString()} per month before service fee</p></div><button onClick={() => setSelectedProperty(null)} className="rounded-full bg-white p-2" aria-label="Close property details"><X /></button></div><div className="mt-6 grid gap-5 lg:grid-cols-2">{tour ? <PanoramaTour imageUrl={tour.url} title={selectedProperty.title} /> : <img src={selectedProperty.media[0]?.url ?? 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=85'} alt={selectedProperty.title} className="h-72 w-full rounded-2xl object-cover sm:h-96" />}      <div className="space-y-5"><RnplSimulator monthlyRent={selectedProperty.monthly_rent_ghs} serviceFeePercent={serviceFeePercent} onServiceFeeChange={setServiceFeePercent} /><button onClick={() => setCheckoutOpen(true)} className="w-full rounded-xl bg-forest px-5 py-3.5 font-semibold text-white hover:bg-ink">Explore monthly payments <ArrowRight size={16} className="ml-2 inline" /></button></div></div></div></div>}
      <CheckoutDrawer open={checkoutOpen} amount={selectedProperty ? Math.round(selectedProperty.monthly_rent_ghs * (1 + serviceFeePercent / 100)) : 0} onClose={() => setCheckoutOpen(false)} />
      {agentFormOpen && <FieldAgentOnboarding onClose={() => setAgentFormOpen(false)} />}
    </div>
  )
}
