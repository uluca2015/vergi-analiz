import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { ChevronLeft, Upload, FileSpreadsheet, Loader } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'

export default function MizanYuklePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: { donem_yili: new Date().getFullYear() }
  })
  const [dosya, setDosya] = useState(null)
  const [loading, setLoading] = useState(false)
  const [sonuc, setSonuc] = useState(null)
  const [raporOlusturuluyor, setRaporOlusturuluyor] = useState(false)

  const onSubmit = async (data) => {
    if (!dosya) { toast.error('Excel dosyası seçiniz'); return }
    setLoading(true)
    try {
      const form = new FormData()
      form.append('dosya', dosya)
      form.append('mizan_tarihi', data.mizan_tarihi)
      form.append('vergilendirme_donemi', data.vergilendirme_donemi)
      form.append('donem_yili', data.donem_yili)
      if (data.notlar) form.append('notlar', data.notlar)

      const res = await api.post(`/api/mizanlar/yukle/${id}`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSonuc(res.data)
      toast.success(`Mizan yüklendi — ${res.data.kalem_sayisi} hesap okundu`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Yükleme başarısız')
    } finally {
      setLoading(false)
    }
  }

  const handleRaporOlustur = async () => {
    if (!sonuc?.mizan_id) return
    setRaporOlusturuluyor(true)
    try {
      const res = await api.post(`/api/raporlar/olustur/${sonuc.mizan_id}`)
      toast.success('Rapor oluşturuldu!')
      navigate(`/raporlar/${res.data.rapor_id}`)
    } catch (err) {
      toast.error('Rapor oluşturulamadı')
    } finally {
      setRaporOlusturuluyor(false)
    }
  }

  const fmt = (n) => n?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) ?? '—'
  const pct = (n) => n != null ? `%${(n * 100).toFixed(1)}` : '—'

  return (
    <div className="max-w-4xl">
      <div className="flex items-center gap-3 mb-6">
        <Link to={`/firmalar/${id}`} className="text-gray-400 hover:text-gray-600">
          <ChevronLeft size={20} />
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">Mizan Yükle & Analiz Et</h1>
      </div>

      {!sonuc ? (
        <div className="card p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Dosya seçimi */}
            <div>
              <label className="label">Excel Mizan Dosyası (.xlsx) *</label>
              <div
                className="mt-1 border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
                onClick={() => document.getElementById('dosya-input').click()}
              >
                <FileSpreadsheet size={36} className="mx-auto text-gray-400 mb-3" />
                {dosya ? (
                  <div>
                    <p className="font-medium text-gray-900">{dosya.name}</p>
                    <p className="text-sm text-gray-500 mt-1">{(dosya.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-600">Dosya seçmek için tıklayın</p>
                    <p className="text-sm text-gray-400 mt-1">Excel (.xlsx, .xls) desteklenir</p>
                  </div>
                )}
                <input
                  id="dosya-input"
                  type="file"
                  accept=".xlsx,.xls"
                  className="hidden"
                  onChange={e => setDosya(e.target.files[0])}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="label">Mizan Tarihi *</label>
                <input type="date" className="input"
                  {...register('mizan_tarihi', { required: 'Tarih zorunludur' })} />
                {errors.mizan_tarihi && <p className="text-danger-500 text-xs mt-1">{errors.mizan_tarihi.message}</p>}
              </div>
              <div>
                <label className="label">Vergilendirme Dönemi *</label>
                <select className="input" {...register('vergilendirme_donemi', { required: true })}>
                  <option value="Q1">1. Çeyrek (Ocak–Mart)</option>
                  <option value="Q2">2. Çeyrek (Nisan–Haziran)</option>
                  <option value="Q3">3. Çeyrek (Temmuz–Eylül)</option>
                  <option value="Q4">4. Çeyrek (Ekim–Aralık)</option>
                  <option value="YILLIK">Yıllık</option>
                </select>
              </div>
              <div>
                <label className="label">Dönem Yılı *</label>
                <input type="number" className="input" min="2000" max="2030"
                  {...register('donem_yili', { required: true, valueAsNumber: true })} />
              </div>
            </div>

            <div>
              <label className="label">Notlar</label>
              <textarea className="input" rows={2} {...register('notlar')} />
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? (
                <><Loader size={16} className="animate-spin" /> Mizan okunuyor ve analiz ediliyor...</>
              ) : (
                <><Upload size={16} /> Mizanı Yükle ve Analiz Et</>
              )}
            </button>
          </form>
        </div>
      ) : (
        /* Analiz Sonuçları */
        <div className="space-y-6">
          {/* Özet */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Net Satışlar', value: fmt(sonuc.ozet?.net_satislar) + ' ₺' },
              { label: 'Dönem Kârı', value: fmt(sonuc.ozet?.donem_kari) + ' ₺' },
              { label: 'Vergi Yükü', value: fmt(sonuc.vergi_hesaplama?.toplam_vergi_yuku) + ' ₺' },
              { label: 'Toplam Aktif', value: fmt(sonuc.ozet?.toplam_aktif) + ' ₺' },
            ].map(s => (
              <div key={s.label} className="card p-4">
                <p className="text-xs text-gray-500 mb-1">{s.label}</p>
                <p className="text-lg font-semibold text-gray-900">{s.value}</p>
              </div>
            ))}
          </div>

          {/* Finansal oranlar */}
          <div className="card p-5">
            <h3 className="font-semibold text-gray-900 mb-4">Finansal Oranlar</h3>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Cari Oran', val: sonuc.finansal_oranlar?.cari_oran?.toFixed(2) },
                { label: 'Asit Test', val: sonuc.finansal_oranlar?.asit_test_orani?.toFixed(2) },
                { label: 'Borç/Özkaynak', val: sonuc.finansal_oranlar?.borc_oz_kaynak?.toFixed(2) },
                { label: 'Brüt Kâr Marjı', val: pct(sonuc.finansal_oranlar?.brut_kar_marji) },
                { label: 'Net Kâr Marjı', val: pct(sonuc.finansal_oranlar?.net_kar_marji) },
                { label: 'Özkaynak Kârl.', val: pct(sonuc.finansal_oranlar?.oz_kaynak_karlilik) },
              ].map(o => (
                <div key={o.label} className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">{o.label}</p>
                  <p className="text-base font-semibold text-gray-900 mt-1">{o.val ?? '—'}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Risk skoru */}
          <div className="grid grid-cols-2 gap-4">
            <div className="card p-5">
              <h3 className="font-semibold text-gray-900 mb-3">Vergi Risk Skoru</h3>
              <div className="flex items-end gap-3 mb-3">
                <span className="text-4xl font-bold text-gray-900">{sonuc.vergi_risk?.skor}</span>
                <span className="text-gray-400 mb-1">/100</span>
                <span className={`badge mb-1 ${sonuc.vergi_risk?.skor >= 60 ? 'badge-red' : sonuc.vergi_risk?.skor >= 30 ? 'badge-yellow' : 'badge-green'}`}>
                  {sonuc.vergi_risk?.seviye}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div
                  className={`h-2 rounded-full ${sonuc.vergi_risk?.skor >= 60 ? 'bg-danger-500' : sonuc.vergi_risk?.skor >= 30 ? 'bg-warning-500' : 'bg-success-500'}`}
                  style={{ width: `${sonuc.vergi_risk?.skor}%` }}
                />
              </div>
              {sonuc.vergi_risk?.riskler?.map((r, i) => (
                <div key={i} className="text-xs text-gray-600 mb-1">
                  <span className={`badge mr-1 ${r.risk === 'Yüksek' ? 'badge-red' : 'badge-yellow'}`}>{r.risk}</span>
                  {r.kategori}
                </div>
              ))}
            </div>
            <div className="card p-5">
              <h3 className="font-semibold text-gray-900 mb-3">Kredi Uygunluk Skoru</h3>
              <div className="flex items-end gap-3 mb-3">
                <span className="text-4xl font-bold text-gray-900">{sonuc.kredi_uygunluk?.skor}</span>
                <span className="text-gray-400 mb-1">/100</span>
                <span className={`badge mb-1 ${sonuc.kredi_uygunluk?.skor >= 70 ? 'badge-green' : sonuc.kredi_uygunluk?.skor >= 40 ? 'badge-yellow' : 'badge-red'}`}>
                  {sonuc.kredi_uygunluk?.sonuc}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div
                  className={`h-2 rounded-full ${sonuc.kredi_uygunluk?.skor >= 70 ? 'bg-success-500' : sonuc.kredi_uygunluk?.skor >= 40 ? 'bg-warning-500' : 'bg-danger-500'}`}
                  style={{ width: `${sonuc.kredi_uygunluk?.skor}%` }}
                />
              </div>
              <p className="text-xs text-gray-600">{sonuc.kredi_uygunluk?.sonuc_aciklama}</p>
            </div>
          </div>

          {/* Rapor oluştur */}
          <div className="card p-6 text-center">
            <h3 className="font-semibold text-gray-900 mb-2">AI Destekli Tam Rapor</h3>
            <p className="text-sm text-gray-500 mb-4">
              Claude AI ile vergi riskleri, finansal analiz ve kredi önerileri içeren kapsamlı raporu oluşturun
            </p>
            <button
              onClick={handleRaporOlustur}
              disabled={raporOlusturuluyor}
              className="btn-primary"
            >
              {raporOlusturuluyor ? (
                <><Loader size={16} className="animate-spin" /> Rapor oluşturuluyor (15-30 sn)...</>
              ) : (
                'AI Raporu Oluştur'
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
