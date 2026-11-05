import { useMemo } from 'react'

interface RnplSimulatorProps {
  monthlyRent: number
  serviceFeePercent: number
  onServiceFeeChange: (fee: number) => void
}

const formatGhs = (amount: number) => `GH₵${Math.round(amount).toLocaleString()}`

export function RnplSimulator({ monthlyRent, serviceFeePercent, onServiceFeeChange }: RnplSimulatorProps) {
  const comparison = useMemo(() => ({
    upfront: monthlyRent * 24,
    monthlyTotal: monthlyRent * (1 + serviceFeePercent / 100),
    total: monthlyRent * (1 + serviceFeePercent / 100) * 24,
  }), [monthlyRent, serviceFeePercent])

  return (
    <section className="rounded-3xl border border-forest/10 bg-white p-6 shadow-card">
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">Your rent, made flexible</p>
      <h3 className="mt-2 text-2xl font-semibold text-ink">See the full picture</h3>
      <p className="mt-2 text-sm leading-6 text-muted">Compare a typical 2-year advance with monthly RentEase payments. Estimates only; final terms depend on your lease.</p>
      <label className="mt-6 block text-sm font-medium text-ink" htmlFor="service-fee">Service fee: {serviceFeePercent}%</label>
      <input id="service-fee" type="range" min="8" max="10" value={serviceFeePercent} onChange={(event) => onServiceFeeChange(Number(event.target.value))} className="mt-2 w-full accent-forest" />
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl bg-canvas p-4">
          <p className="text-sm text-muted">2-year upfront</p>
          <p className="mt-1 text-xl font-bold text-ink">{formatGhs(comparison.upfront)}</p>
          <p className="mt-1 text-xs text-muted">Typically paid before move-in</p>
        </div>
        <div className="rounded-2xl bg-lime/40 p-4">
          <p className="text-sm text-ink">RentEase monthly</p>
          <p className="mt-1 text-xl font-bold text-ink">{formatGhs(comparison.monthlyTotal)}<span className="text-sm font-medium"> / mo</span></p>
          <p className="mt-1 text-xs text-muted">{formatGhs(comparison.total)} over 24 months incl. fee</p>
        </div>
      </div>
      <p className="mt-4 text-xs leading-5 text-muted">Monthly schedule adds {serviceFeePercent}% to rent and may cost more overall than paying upfront. No financial or credit approval is implied.</p>
    </section>
  )
}
