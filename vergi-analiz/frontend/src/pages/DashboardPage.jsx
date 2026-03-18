import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Building2, FileText, TrendingUp, AlertTriangle, Plus } from 'lucide-react'
import api from '../utils/api'

export default function DashboardPage() {
  const [firmalar, setFirmalar] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/firmalar/').then(r => { setFirmalar(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const stats = [
    { label: 'Toplam Firma', value: firmalar.length, icon: Building2, color: 'text-primary-600 bg-primary-50' },
    { label: 'Kayıtlı Mükellef', value: firmalar.filter(f => f.mukellef_turu === 'sirket').length, icon: FileText, color: 'text-success-700 bg-success-50' },
    { label: 'Şahıs Firması', value: firmalar.filter(f => f.mukellef_turu === 'sahis').length, icon: TrendingUp, color: 'text-warning-700 bg-warning-50' },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Vergi ve finansal analiz platformuna hoş geldiniz</p>
        </div>
        <Link to="/firmalar/yeni" className="btn-primary">
          <Plus size={16} /> Yeni Firma
        </Link>
      </div>

      {/* İstatistik kartları */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="card p-6 flex items-center gap-4">
            <div className={`p-3 rounded-xl ${s.color}`}>
              <s.icon size={24} />
            </div>
            <div>
              <p className="text-2xl font-semibold text-gray-900">{s.value}</p>
              <p className="text-sm text-gray-500">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Son firmalar */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="font-semibold text-gray-900">Son Eklenen Firmalar</h2>
          <Link to="/firmalar" className="text-sm text-primary-600 hover:underline">Tümünü gör</Link>
        </div>
        {loading ? (
          <div className="px-6 py-8 text-center text-gray-400">Yükleniyor...</div>
        ) : firmalar.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <Building2 size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 mb-4">Henüz firma eklenmemiş</p>
            <Link to="/firmalar/yeni" className="btn-primary">İlk Firmayı Ekle</Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {firmalar.slice(0, 8).map((f) => (
              <Link key={f.id} to={`/firmalar/${f.id}`}
                className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors">
                <div>
                  <p className="font-medium text-gray-900">{f.unvan}</p>
                  <p className="text-sm text-gray-500">VKN: {f.vergi_no} · {f.il || '—'}</p>
                </div>
                <span className={`badge ${f.mukellef_turu === 'sirket' ? 'badge-blue' : 'badge-green'}`}>
                  {f.mukellef_turu === 'sirket' ? 'Şirket' : 'Şahıs'}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
