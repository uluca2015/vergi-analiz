import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Building2, Trash2, Eye } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'

const SIRKET_TURU_LABEL = {
  anonim_sirket: 'A.Ş.',
  limited_sirket: 'Ltd. Şti.',
  kolektif_sirket: 'Koll. Şti.',
  komandit_sirket: 'Kom. Şti.',
  kooperatif: 'Koop.',
  serbest_meslek: 'Serbest Meslek',
  diger: 'Diğer',
}

export default function FirmaListPage() {
  const [firmalar, setFirmalar] = useState([])
  const [filtered, setFiltered] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/firmalar/').then(r => {
      setFirmalar(r.data)
      setFiltered(r.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    const q = search.toLowerCase()
    setFiltered(firmalar.filter(f =>
      f.unvan.toLowerCase().includes(q) ||
      f.vergi_no.includes(q) ||
      (f.il || '').toLowerCase().includes(q)
    ))
  }, [search, firmalar])

  const handleDelete = async (id, unvan) => {
    if (!window.confirm(`"${unvan}" firmasını silmek istediğinizden emin misiniz?`)) return
    try {
      await api.delete(`/api/firmalar/${id}`)
      setFirmalar(prev => prev.filter(f => f.id !== id))
      toast.success('Firma silindi')
    } catch {
      toast.error('Silme işlemi başarısız')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Firmalar</h1>
          <p className="text-gray-500 mt-1">{firmalar.length} kayıtlı firma</p>
        </div>
        <Link to="/firmalar/yeni" className="btn-primary">
          <Plus size={16} /> Yeni Firma
        </Link>
      </div>

      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              className="input pl-9"
              placeholder="Firma adı, VKN veya il ara..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center text-gray-400">Yükleniyor...</div>
        ) : filtered.length === 0 ? (
          <div className="py-12 text-center">
            <Building2 size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">{search ? 'Arama sonucu bulunamadı' : 'Henüz firma eklenmemiş'}</p>
            {!search && (
              <Link to="/firmalar/yeni" className="btn-primary mt-4 inline-flex">
                <Plus size={16} /> İlk Firmayı Ekle
              </Link>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  {['Firma Unvanı', 'VKN', 'Tür', 'Vergi Dairesi', 'İl', 'İşlem'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map(f => (
                  <tr key={f.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <Link to={`/firmalar/${f.id}`} className="font-medium text-gray-900 hover:text-primary-600">
                        {f.unvan}
                      </Link>
                    </td>
                    <td className="px-4 py-3 font-mono text-gray-600">{f.vergi_no}</td>
                    <td className="px-4 py-3">
                      <span className={`badge ${f.mukellef_turu === 'sirket' ? 'badge-blue' : 'badge-green'}`}>
                        {f.mukellef_turu === 'sirket'
                          ? (SIRKET_TURU_LABEL[f.sirket_turu] || 'Şirket')
                          : 'Şahıs'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{f.vergi_dairesi}</td>
                    <td className="px-4 py-3 text-gray-600">{f.il || '—'}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Link to={`/firmalar/${f.id}`} className="btn-secondary py-1 px-2 text-xs">
                          <Eye size={14} /> Detay
                        </Link>
                        <button
                          onClick={() => handleDelete(f.id, f.unvan)}
                          className="btn-danger py-1 px-2 text-xs"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
