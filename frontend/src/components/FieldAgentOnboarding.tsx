import { useState, type FormEvent } from 'react'
import { getApiUrl } from '../lib/api'

interface FieldAgentOnboardingProps {
  onClose: () => void
}

export function FieldAgentOnboarding({ onClose }: FieldAgentOnboardingProps) {
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setMessage('')
    const form = new FormData(event.currentTarget)
    const token = localStorage.getItem('rentease_access_token')
    if (!token) {
      setMessage('Sign in with a field-agent account before submitting an inspection.')
      setBusy(false)
      return
    }

    const amenities = String(form.get('amenities') ?? '')
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
    const payload = Object.fromEntries(form.entries())
    delete payload.amenities
    delete payload.media
    delete payload.media_type
    try {
      const response = await fetch(`${getApiUrl()}/master-leases/onboard`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ...payload, amenities }),
      })
      const result = await response.json() as { error?: string; property?: { id: number } }
      if (!response.ok || !result.property) throw new Error(result.error ?? 'Unable to save property onboarding.')

      const media = form.get('media')
      if (media instanceof File && media.size > 0) {
        const upload = new FormData()
        upload.set('file', media)
        upload.set('media_type', String(form.get('media_type') ?? 'IMAGE'))
        const uploadResponse = await fetch(`${getApiUrl()}/properties/${result.property.id}/media`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: upload,
        })
        if (!uploadResponse.ok) {
          const error = await uploadResponse.json() as { error?: string }
          throw new Error(`Property saved, but media upload failed: ${error.error ?? 'Upload error'}`)
        }
      }
      setMessage('Inspection and master lease saved. Add a signed lease document to activate the listing.')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Something went wrong while saving.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-40 overflow-y-auto bg-ink/50 p-4 sm:p-8">
      <section className="mx-auto max-w-3xl rounded-3xl bg-white p-6 shadow-2xl sm:p-9">
        <div className="flex items-start justify-between gap-5">
          <div><p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">RentEase field team</p><h2 className="mt-2 text-3xl font-semibold text-ink">Property inspection</h2><p className="mt-2 text-sm leading-6 text-muted">Capture landlord and property details. Landlords do not need to create platform accounts.</p></div>
          <button onClick={onClose} className="rounded-full px-3 py-2 text-sm font-medium text-muted hover:bg-canvas">Close</button>
        </div>
        <form onSubmit={submit} className="mt-7 grid gap-4 sm:grid-cols-2">
          <Field label="Property title" name="title" placeholder="Bright 2-bed apartment" required />
          <Field label="Region" name="region" placeholder="Greater Accra" required />
          <Field label="Neighborhood" name="neighborhood" placeholder="East Legon" required />
          <Field label="Street address" name="address" placeholder="Address for inspection" required />
          <Field label="Monthly rent (GHS)" name="monthly_rent_ghs" type="number" min="1" required />
          <Field label="Bedrooms" name="bedrooms" type="number" min="0" defaultValue="2" required />
          <Field label="Bathrooms" name="bathrooms" type="number" min="0" defaultValue="1" required />
          <Field label="Available / lease start" name="start_date" type="date" required />
          <Field label="Master lease end" name="end_date" type="date" required />
          <Field label="Advance paid (GHS)" name="advance_paid_ghs" type="number" min="1" required />
          <Field label="Landlord discount (%)" name="discount_percent" type="number" min="5" max="10" step="0.1" required />
          <Field label="Landlord full name" name="landlord_name" placeholder="Managed by field agent" required />
          <Field label="Landlord phone" name="landlord_phone" placeholder="+233 ..." />
          <Field label="Amenities (comma separated)" name="amenities" placeholder="Parking, generator, furnished" />
          <label className="text-sm font-medium text-ink sm:col-span-2">Signed master-lease document URL (optional)
            <input name="contract_document_url" type="url" placeholder="https://secure-document-storage/..." className="mt-2 w-full rounded-xl border border-stone-200 px-4 py-3 font-normal outline-none transition focus:border-forest" />
            <span className="mt-1 block text-xs font-normal text-muted">Providing the signed agreement marks the listing verified and available.</span>
          </label>
          <label className="text-sm font-medium text-ink sm:col-span-2">Inspection photo or 360° panorama
            <input name="media" type="file" accept="image/jpeg,image/png,image/webp" className="mt-2 block w-full rounded-xl border border-stone-200 p-3 text-sm text-muted" />
            <span className="mt-1 block text-xs font-normal text-muted">JPEG, PNG or WebP, max 16 MB. Add a signed lease document separately before activation.</span>
          </label>
          <label className="text-sm font-medium text-ink">Media type
            <select name="media_type" className="mt-2 w-full rounded-xl border border-stone-200 bg-white px-4 py-3"><option value="IMAGE">Standard photo</option><option value="PANORAMA">360° equirectangular panorama</option></select>
          </label>
          {message && <p role="status" className="rounded-xl bg-canvas p-4 text-sm text-ink sm:col-span-2">{message}</p>}
          <div className="flex justify-end gap-3 pt-2 sm:col-span-2"><button type="button" onClick={onClose} className="rounded-xl px-5 py-3 font-semibold text-muted">Cancel</button><button disabled={busy} className="rounded-xl bg-forest px-6 py-3 font-semibold text-white disabled:opacity-60">{busy ? 'Saving…' : 'Save inspection & lease'}</button></div>
        </form>
      </section>
    </div>
  )
}

interface FieldProps {
  label: string
  name: string
  type?: string
  placeholder?: string
  min?: string
  max?: string
  step?: string
  required?: boolean
  defaultValue?: string
}

function Field({ label, name, type = 'text', ...inputProps }: FieldProps) {
  return <label className="text-sm font-medium text-ink">{label}<input name={name} type={type} {...inputProps} className="mt-2 w-full rounded-xl border border-stone-200 px-4 py-3 font-normal outline-none transition focus:border-forest" /></label>
}
