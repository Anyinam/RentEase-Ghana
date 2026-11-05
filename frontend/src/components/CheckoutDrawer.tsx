import { useState, type FormEvent } from 'react'
import { X, ShieldCheck, Smartphone } from 'lucide-react'

interface CheckoutDrawerProps {
  open: boolean
  amount: number
  onClose: () => void
}

export function CheckoutDrawer({ open, amount, onClose }: CheckoutDrawerProps) {
  const [provider, setProvider] = useState('MTN MoMo')
  const [phone, setPhone] = useState('')
  const [consent, setConsent] = useState(false)
  const [message, setMessage] = useState('')

  if (!open) return null

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!consent) {
      setMessage('Please review and accept the recurring payment mandate.')
      return
    }
    setMessage('Payment setup is not connected yet. No payment or authorization has been requested.')
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-ink/40" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <aside className="h-full w-full max-w-md overflow-y-auto bg-white p-6 shadow-2xl" aria-label="Mobile Money checkout">
        <div className="flex items-center justify-between">
          <div><p className="text-sm font-semibold text-forest">SECURE CHECKOUT</p><h2 className="mt-1 text-2xl font-semibold text-ink">Set up your rent</h2></div>
          <button onClick={onClose} className="rounded-full p-2 text-muted hover:bg-canvas" aria-label="Close checkout"><X /></button>
        </div>
        <div className="mt-6 rounded-2xl bg-canvas p-4"><p className="text-sm text-muted">Monthly installment</p><p className="mt-1 text-2xl font-bold text-ink">GH₵{amount.toLocaleString()}</p></div>
        <form onSubmit={submit} className="mt-6 space-y-5">
          <label className="block text-sm font-medium text-ink">Mobile Money network
            <select value={provider} onChange={(event) => setProvider(event.target.value)} className="mt-2 w-full rounded-xl border border-stone-200 bg-white px-4 py-3">
              <option>MTN MoMo</option><option>Telecel Cash</option><option>AT Money</option>
            </select>
          </label>
          <label className="block text-sm font-medium text-ink">MoMo phone number
            <span className="mt-2 flex items-center gap-2 rounded-xl border border-stone-200 px-4"><Smartphone size={18} className="text-muted" /><input value={phone} onChange={(event) => setPhone(event.target.value)} type="tel" required placeholder="e.g. 024 000 0000" className="w-full py-3 outline-none" /></span>
          </label>
          <label className="flex items-start gap-3 text-sm leading-6 text-muted"><input checked={consent} onChange={(event) => setConsent(event.target.checked)} type="checkbox" className="mt-1 accent-forest" /><span>I authorize RentEase and its payment provider to request the monthly rent amount from my selected MoMo wallet, subject to my signed lease and provider confirmation.</span></label>
          {message && <p role="status" className="rounded-xl bg-amber-50 p-3 text-sm text-amber-900">{message}</p>}
          <button type="submit" className="w-full rounded-xl bg-forest px-5 py-3.5 font-semibold text-white hover:bg-ink">Continue with {provider}</button>
        </form>
        <p className="mt-5 flex items-center gap-2 text-xs leading-5 text-muted"><ShieldCheck size={16} className="shrink-0" /> Your MoMo PIN is entered only in your network provider's secure prompt. RentEase will never ask for your PIN.</p>
      </aside>
    </div>
  )
}
