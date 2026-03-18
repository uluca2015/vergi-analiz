import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, Edit, Upload, FileText, Calendar, TrendingUp } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'

const MUKELLEF_LABEL = { sirket: 'Şirket', sahis: 'Şahıs / Gerçek Kişi' }
const SIRKET_LABEL = {
  anonim_sirket: 'Anonim Şirket', limited_sirket: 'Limited Şirket',
  kolektif_sirket: 'Kolektif Şirket', komandit_sirket: 'Komandit Şirket',
  kooperatif: 'Kooperatif', serbest_meslek: 'Serbest Meslek', diger: 'Diğer',
}
const DONEM_LABEL = { Q1: '1. Çeyrek (Oca–Mar)', Q2: '2. Çeyrek (Nis–Haz)', Q3: '3. Çeyrek (Tem–Eyl)', Q4: '4. Çeyrek (Eki–Ara)', YILLIK: 'Yıllık' }

function InfoRow({ label, value }) {
  if (!value) return null
  return (
    <div className="flex py-2 border-b border-gray-100 last:border-0">
      <span className="w-44 text-sm text-gray-500 flex-shrink-0">{label}</span>
      <span className="text-sm text-gray-900">{value}</span>
    </div>
  )
}

export default function FirmaDetayPage() {
  const { id } = useParams()
  const [firma, setFirma] = useState(null)
  const [mizanlar, setMizanlar] = useState([])
  const [raporlar, setRaporlar] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get(`/api/firmalar/${id}`),
      api.get(`/api/mizanlar/firma/${id}`),
      api.get(`/api/raporlar/firma/${id}`),
    ]).then(([f, m, r]) => {
      setFirma(f.data)
      setMizanlar(m.data)
      setRaporlar(r.data)
    }).catch(() => toast.error('Veriler yüklenemedi'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="py-12 text-center text-gray-400">Yükleniyor...</div>
  if (!firma) return <div className="py-12 text-center text-gray-400">Firma bulunamadı</div>

  const riskRenk = (skor) => {
    if (!skor) return 'badge-blue'
    if (skor >= 60) return 'badge-red'
    if (skor >= 30) return 'badge-yellow'
    return 'badge-green'
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link to="/firmalar" className="text-gray-400 hover:text-gray-600">
            <ChevronLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">{firma.unvan}</h1>
            <p className="text-gray-500 mt-1">
              {MUKELLEF_LABEL[firma.mukellef_turu]}
              {firma.sirket_turu ? ` · ${SIRKET_LABEL[firma.sirket_turu]}` : ''}
              {' · '}VKN: {firma.vergi_no}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link to={`/firmalar/${id}/mizan-yukle`} className="btn-primary">
            <Upload size={16} /> Mizan Yükle
          </Link>
          <Link to={`/firmalar/${id}/duzenle`} className="btn-secondary">
            <Edit size={16} /> Düzenle
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Sol — Firma bilgileri */}
        <div className="col-span-1 space-y-6">
          <div className="card p-5">
            <h2 className="font-semibold text-gray-900 mb-3">Vergi Bilgileri</h2>
            <InfoRow label="Vergi No" value={firma.vergi_no} />
            <InfoRow label="Vergi Dairesi" value={firma.vergi_dairesi} />
            <InfoRow label="Ticaret Sicil No" value={firma.ticaret_sicil_no} />
            <InfoRow label="MERSİS No" value={firma.mersis_no} />
            <InfoRow label="Vergilendirme" value={firma.vergilendirme_sekli?.replace('_', ' ')} />
          </div>
          <div className="card p-5">
            <h2 className="font-semibold text-gray-900 mb-3">İletişim</h2>
            <InfoRow label="Adres" value={firma.adres} />
            <InfoRow label="İl / İlçe" value={[firma.il, firma.ilce].filter(Boolean).join(' / ')} />
            <InfoRow label="Telefon" value={firma.telefon} />
            <InfoRow label="E-posta" value={firma.email} />
          </div>
          {(firma.faaliyet_konusu || firma.nace_kodu) && (
            <div className="card p-5">
              <h2 className="font-semibold text-gray-900 mb-3">Faaliyet</h2>
              <InfoRow label="Faaliyet Konusu" value={firma.faaliyet_konusu} />
              <InfoRow label="NACE Kodu" value={firma.nace_kodu} />
              <InfoRow label="Kuruluş" value={firma.kurulis_tarihi} />
            </div>
          )}
        </div>

        {/* Sağ — Mizanlar + Raporlar */}
        <div className="col-span-2 space-y-6">
          {/* Mizanlar */}
          <div className="card">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                <Calendar size={18} className="text-gray-400" /> Yüklenen Mizanlar
              </h2>
              <Link to={`/firmalar/${id}/mizan-yukle`} className="btn-secondary text-xs py-1">
                <Upload size={14} /> Yeni Yükle
              </Link>
            </div>
            {mizanlar.length === 0 ? (
              <div className="py-8 text-center text-gray-400 text-sm">
                Henüz mizan yüklenmemiş
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {mizanlar.map(m => (
                  <div key={m.id} className="px-6 py-4 flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm text-gray-900">
                        {m.donem_yili} · {DONEM_LABEL[m.vergilendirme_donemi]}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Mizan tarihi: {m.mizan_tarihi} · {m.dosya_adi || 'Excel'}
                      </p>
                    </div>
                    <Link to={`/firmalar/${id}/mizan-yukle`}
                      state={{ mizan_id: m.id }}
                      className="btn-secondary text-xs py-1">
                      <TrendingUp size={14} /> Analiz Et
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Raporlar */}
          <div className="card">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                <FileText size={18} className="text-gray-400" /> Oluşturulan Raporlar
              </h2>
            </div>
            {raporlar.length === 0 ? (
              <div className="py-8 text-center text-gray-400 text-sm">
                Henüz rapor oluşturulmamış — mizan yükleyip analiz ettirin
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {raporlar.map(r => (
                  <Link key={r.id} to={`/raporlar/${r.id}`}
                    className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors block">
                    <div>
                      <p className="font-medium text-sm text-gray-900">{r.baslik}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {new Date(r.created_at).toLocaleDateString('tr-TR')}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {r.vergi_risk_skoru !== null && (
                        <span className={`badge ${riskRenk(r.vergi_risk_skoru)}`}>
                          Risk: {r.vergi_risk_skoru}
                        </span>
                      )}
                      {r.kredi_uygunluk_skoru !== null && (
                        <span className="badge badge-blue">
                          Kredi: {r.kredi_uygunluk_skoru}
                        </span>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
