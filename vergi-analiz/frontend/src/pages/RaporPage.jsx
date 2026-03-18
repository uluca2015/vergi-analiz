import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, AlertTriangle, CheckCircle, TrendingUp, FileText, Building2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar } from 'recharts'
import toast from 'react-hot-toast'
import api from '../utils/api'

const fmt = (n) => n != null ? n.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) : '—'
const pct = (n) => n != null ? `%${(n * 100).toFixed(1)}` : '—'
const pct2 = (n) => n != null ? `%${n.toFixed(1)}` : '—'

function SectionCard({ title, icon: Icon, children }) {
  return (
    <div className="card p-6">
      <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
        {Icon && <Icon size={18} className="text-gray-400" />}
        {title}
      </h2>
      {children}
    </div>
  )
}

function RiskBadge({ skor }) {
  if (skor == null) return null
  if (skor >= 60) return <span className="badge badge-red">Yüksek Risk · {skor}</span>
  if (skor >= 30) return <span className="badge badge-yellow">Orta Risk · {skor}</span>
  return <span className="badge badge-green">Düşük Risk · {skor}</span>
}

export default function RaporPage() {
  const { id } = useParams()
  const [rapor, setRapor] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/api/raporlar/${id}`)
      .then(r => setRapor(r.data))
      .catch(() => toast.error('Rapor yüklenemedi'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="py-12 text-center text-gray-400">Rapor yükleniyor...</div>
  if (!rapor) return <div className="py-12 text-center text-gray-400">Rapor bulunamadı</div>

  const gt = rapor.gelir_tablosu || {}
  const bl = rapor.bilanco || {}
  const or = rapor.finansal_oranlar || {}
  const vr = rapor.vergi_hesaplama || {}
  const risk = or.yorumlar || []

  const gelirChartData = [
    { name: 'Net Satışlar', tutar: gt.net_satislar || 0 },
    { name: 'Brüt Kâr', tutar: gt.brut_kar || 0 },
    { name: 'Faaliyet Kârı', tutar: gt.faaliyet_kari || 0 },
    { name: 'Dönem Kârı', tutar: gt.donem_kari || 0 },
  ]

  const radarData = [
    { subject: 'Likidite', A: Math.min((or.cari_oran || 0) * 25, 100) },
    { subject: 'Kârlılık', A: Math.min(((or.net_kar_marji || 0) * 100) * 5, 100) },
    { subject: 'Özkaynak', A: Math.min((or.oz_kaynak_orani || 0) * 100, 100) },
    { subject: 'Aktivite', A: Math.min((or.aktif_devir_hizi || 0) * 25, 100) },
    { subject: 'Kredi Uygn.', A: rapor.kredi_uygunluk_skoru || 0 },
  ]

  const krediKriterler = (rapor.finansal_oranlar && JSON.parse ? null : null)

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-start gap-3">
          <button onClick={() => window.history.back()} className="text-gray-400 hover:text-gray-600 mt-1">
            <ChevronLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{rapor.baslik}</h1>
            <p className="text-gray-500 text-sm mt-1">
              Oluşturulma: {new Date(rapor.created_at).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' })}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <RiskBadge skor={rapor.vergi_risk_skoru} />
          <span className={`badge ${(rapor.kredi_uygunluk_skoru || 0) >= 70 ? 'badge-green' : (rapor.kredi_uygunluk_skoru || 0) >= 40 ? 'badge-yellow' : 'badge-red'}`}>
            Kredi: {rapor.kredi_uygunluk_skoru}
          </span>
        </div>
      </div>

      <div className="space-y-6">
        {/* Vergi Hesaplama */}
        <SectionCard title="Vergi Hesaplama" icon={FileText}>
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Dönem Kârı', val: fmt(vr.donem_kari) + ' ₺' },
              { label: 'Vergi Yükü', val: fmt(vr.toplam_vergi_yuku) + ' ₺' },
              { label: 'Net Kâr (Sonrası)', val: fmt(vr.net_kar_vergi_sonrasi) + ' ₺' },
              { label: 'Mükellef Türü', val: vr.mukellef_turu === 'sahis' ? 'Gelir Vergisi' : 'Kurumlar Vergisi' },
            ].map(s => (
              <div key={s.label} className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">{s.label}</p>
                <p className="text-sm font-semibold text-gray-900 mt-1">{s.val}</p>
              </div>
            ))}
          </div>
          {vr.kurumlar_vergisi && (
            <div className="mt-4 p-3 bg-primary-50 rounded-lg text-sm">
              <p className="font-medium text-primary-700">Kurumlar Vergisi Detayı</p>
              <p className="text-primary-600 mt-1">
                Matrah: {fmt(vr.kurumlar_vergisi.matrah)} ₺ · Oran: {vr.kurumlar_vergisi.yuzde} · Vergi: {fmt(vr.kurumlar_vergisi.vergi)} ₺
                {vr.asgari_kv_uygulanir && (
                  <span className="ml-2 badge badge-yellow">Asgari KV uygulanıyor</span>
                )}
              </p>
            </div>
          )}
          {vr.gelir_vergisi && (
            <div className="mt-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Dilim Detayı</p>
              <div className="space-y-1">
                {vr.gelir_vergisi.dilim_detay?.map((d, i) => (
                  <div key={i} className="flex items-center justify-between text-xs bg-gray-50 rounded px-3 py-2">
                    <span className="text-gray-500">{d.dilim}</span>
                    <span className="font-medium">{d.oran}</span>
                    <span className="text-gray-600">{fmt(d.matrah)} ₺</span>
                    <span className="font-semibold text-primary-700">{fmt(d.vergi)} ₺</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </SectionCard>

        {/* Gelir Tablosu + Grafik */}
        <div className="grid grid-cols-2 gap-6">
          <SectionCard title="Gelir Tablosu" icon={TrendingUp}>
            <div className="space-y-2">
              {[
                { label: 'Net Satışlar', val: fmt(gt.net_satislar), bold: false },
                { label: 'Satışların Maliyeti (-)', val: fmt(gt.satislar_maliyeti), bold: false, indent: true },
                { label: 'Brüt Kâr', val: fmt(gt.brut_kar) + ` (${pct2(gt.brut_kar_marji_yuzde)})`, bold: true },
                { label: 'Faaliyet Giderleri (-)', val: fmt(gt.faaliyet_giderleri), bold: false, indent: true },
                { label: 'Faaliyet Kârı', val: fmt(gt.faaliyet_kari) + ` (${pct2(gt.faaliyet_kar_marji_yuzde)})`, bold: true },
                { label: 'Finansman Giderleri (-)', val: fmt(gt.finansman_giderleri), bold: false, indent: true },
                { label: 'Dönem Net Kârı', val: fmt(gt.donem_kari) + ` (${pct2(gt.net_kar_marji_yuzde)})`, bold: true, highlight: true },
              ].map(r => (
                <div key={r.label} className={`flex justify-between py-1.5 text-sm border-b border-gray-100 last:border-0 ${r.highlight ? 'bg-primary-50 px-2 rounded' : ''}`}>
                  <span className={`${r.indent ? 'pl-4 text-gray-500' : ''} ${r.bold ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>{r.label}</span>
                  <span className={r.bold ? 'font-semibold text-gray-900' : 'text-gray-600'}>{r.val} ₺</span>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Kâr Waterfall">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={gelirChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={v => (v / 1000000).toFixed(1) + 'M'} />
                <Tooltip formatter={v => fmt(v) + ' ₺'} />
                <Bar dataKey="tutar" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </SectionCard>
        </div>

        {/* Bilanço */}
        <SectionCard title="Bilanço Özeti" icon={Building2}>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">AKTİF</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between py-1 border-b border-gray-100">
                  <span className="text-gray-700">Dönen Varlıklar</span>
                  <span className="font-medium">{fmt(bl.aktif?.donen_varliklar?.toplam)} ₺</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100 pl-4 text-gray-500">
                  <span>Kasa / Banka</span>
                  <span>{fmt(bl.aktif?.donen_varliklar?.kasa_banka)} ₺</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100 pl-4 text-gray-500">
                  <span>Alıcılar</span>
                  <span>{fmt(bl.aktif?.donen_varliklar?.alicilar)} ₺</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100 pl-4 text-gray-500">
                  <span>Stoklar</span>
                  <span>{fmt(bl.aktif?.donen_varliklar?.stoklar)} ₺</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100">
                  <span className="text-gray-700">Duran Varlıklar</span>
                  <span className="font-medium">{fmt(bl.aktif?.duran_varliklar?.toplam)} ₺</span>
                </div>
                <div className="flex justify-between py-2 bg-gray-50 px-2 rounded font-semibold">
                  <span>Toplam Aktif</span>
                  <span>{fmt(bl.aktif?.toplam_aktif)} ₺</span>
                </div>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">PASİF</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between py-1 border-b border-gray-100">
                  <span className="text-gray-700">K.V. Yabancı Kaynaklar</span>
                  <span className="font-medium">{fmt(bl.pasif?.kvyk?.toplam)} ₺</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100 pl-4 text-gray-500">
                  <span>Satıcılar</span>
                  <span>{fmt(bl.pasif?.kvyk?.saticiler)} ₺</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100 pl-4 text-gray-500">
                  <span>Banka Kredileri</span>
                  <span>{fmt(bl.pasif?.kvyk?.banka_kredileri)} ₺</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100">
                  <span className="text-gray-700">U.V. Yabancı Kaynaklar</span>
                  <span className="font-medium">{fmt(bl.pasif?.uvyk?.toplam)} ₺</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100">
                  <span className="text-gray-700">Özkaynaklar</span>
                  <span className="font-medium">{fmt(bl.pasif?.ozkaynak?.toplam)} ₺</span>
                </div>
                <div className="flex justify-between py-2 bg-gray-50 px-2 rounded font-semibold">
                  <span>Toplam Pasif</span>
                  <span>{fmt(bl.pasif?.toplam_pasif)} ₺</span>
                </div>
              </div>
            </div>
          </div>
        </SectionCard>

        {/* Finansal Radar */}
        <div className="grid grid-cols-2 gap-6">
          <SectionCard title="Finansal Performans Radarı">
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
                <Radar name="Skor" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
              </RadarChart>
            </ResponsiveContainer>
          </SectionCard>

          <SectionCard title="Temel Finansal Oranlar">
            <div className="space-y-3">
              {[
                { label: 'Cari Oran', val: or.cari_oran?.toFixed(2), esik: '≥ 2.0 ideal' },
                { label: 'Asit Test Oranı', val: or.asit_test_orani?.toFixed(2), esik: '≥ 1.0 ideal' },
                { label: 'Borç / Özkaynak', val: or.borc_oz_kaynak?.toFixed(2), esik: '≤ 1.0 ideal' },
                { label: 'Net Kâr Marjı', val: pct(or.net_kar_marji), esik: '≥ %10 ideal' },
                { label: 'Özkaynak Kârlılığı', val: pct(or.oz_kaynak_karlilik), esik: 'Yüksek = iyi' },
                { label: 'Faiz Karşılama', val: or.faiz_karsilama?.toFixed(2) || '—', esik: '≥ 3.0 ideal' },
              ].map(o => (
                <div key={o.label} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{o.label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">{o.esik}</span>
                    <span className="font-semibold text-gray-900 w-16 text-right">{o.val ?? '—'}</span>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        {/* AI Raporu */}
        {rapor.ai_rapor && (
          <SectionCard title="AI Destekli Kapsamlı Analiz Raporu">
            <div className="prose prose-sm max-w-none">
              {rapor.ai_rapor.split('\n').map((line, i) => {
                if (line.startsWith('## ') || line.startsWith('**') && line.endsWith('**')) {
                  return <h3 key={i} className="font-semibold text-gray-900 mt-4 mb-2 text-base">{line.replace(/\*\*/g, '').replace(/## /g, '')}</h3>
                }
                if (line.startsWith('- ') || line.startsWith('* ')) {
                  return <p key={i} className="text-sm text-gray-700 pl-4 mb-1">• {line.slice(2)}</p>
                }
                if (line.trim() === '') return <br key={i} />
                return <p key={i} className="text-sm text-gray-700 mb-2">{line.replace(/\*\*/g, '')}</p>
              })}
            </div>
          </SectionCard>
        )}

        {/* AI Öneriler */}
        {rapor.ai_oneriler && (
          <SectionCard title="Acil Eylem Listesi" icon={CheckCircle}>
            <div className="space-y-2">
              {rapor.ai_oneriler.split('\n').filter(l => l.trim()).map((line, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-primary-50 rounded-lg text-sm">
                  <span className="w-5 h-5 rounded-full bg-primary-600 text-white text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <span className="text-gray-700">{line.replace(/^\d+\.\s*/, '')}</span>
                </div>
              ))}
            </div>
          </SectionCard>
        )}
      </div>
    </div>
  )
}
