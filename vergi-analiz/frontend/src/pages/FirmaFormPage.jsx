import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { ChevronLeft } from 'lucide-react'
import api from '../utils/api'

const ILLER = [
  'Adana','Adıyaman','Afyonkarahisar','Ağrı','Amasya','Ankara','Antalya','Artvin',
  'Aydın','Balıkesir','Bilecik','Bingöl','Bitlis','Bolu','Burdur','Bursa','Çanakkale',
  'Çankırı','Çorum','Denizli','Diyarbakır','Edirne','Elazığ','Erzincan','Erzurum',
  'Eskişehir','Gaziantep','Giresun','Gümüşhane','Hakkari','Hatay','Isparta','İçel',
  'İstanbul','İzmir','Kars','Kastamonu','Kayseri','Kırklareli','Kırşehir','Kocaeli',
  'Konya','Kütahya','Malatya','Manisa','Kahramanmaraş','Mardin','Muğla','Muş',
  'Nevşehir','Niğde','Ordu','Rize','Sakarya','Samsun','Siirt','Sinop','Sivas',
  'Tekirdağ','Tokat','Trabzon','Tunceli','Şanlıurfa','Uşak','Van','Yozgat',
  'Zonguldak','Aksaray','Bayburt','Karaman','Kırıkkale','Batman','Şırnak','Bartın',
  'Ardahan','Iğdır','Yalova','Karabük','Kilis','Osmaniye','Düzce',
]

export default function FirmaFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEdit = Boolean(id)
  const [loading, setLoading] = useState(false)

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    defaultValues: { mukellef_turu: 'sirket', vergilendirme_sekli: 'gercek_usul' }
  })

  const mukellefTuru = watch('mukellef_turu')

  useEffect(() => {
    if (isEdit) {
      api.get(`/api/firmalar/${id}`).then(r => {
        Object.entries(r.data).forEach(([k, v]) => v !== null && setValue(k, v))
      }).catch(() => toast.error('Firma bilgileri yüklenemedi'))
    }
  }, [id])

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      if (isEdit) {
        await api.put(`/api/firmalar/${id}`, data)
        toast.success('Firma güncellendi')
      } else {
        const res = await api.post('/api/firmalar/', data)
        toast.success('Firma oluşturuldu')
        navigate(`/firmalar/${res.data.id}`)
        return
      }
      navigate(`/firmalar/${id}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'İşlem başarısız')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <Link to="/firmalar" className="text-gray-400 hover:text-gray-600">
          <ChevronLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            {isEdit ? 'Firma Düzenle' : 'Yeni Firma Ekle'}
          </h1>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">

        {/* Temel Bilgiler */}
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Temel Bilgiler</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="label">Firma / Mükellef Unvanı *</label>
              <input className="input" placeholder="ABC Ticaret Ltd. Şti."
                {...register('unvan', { required: 'Unvan zorunludur' })} />
              {errors.unvan && <p className="text-danger-500 text-xs mt-1">{errors.unvan.message}</p>}
            </div>

            <div>
              <label className="label">Mükellef Türü *</label>
              <select className="input" {...register('mukellef_turu', { required: true })}>
                <option value="sirket">Şirket</option>
                <option value="sahis">Şahıs / Gerçek Kişi</option>
              </select>
            </div>

            {mukellefTuru === 'sirket' && (
              <div>
                <label className="label">Şirket Türü</label>
                <select className="input" {...register('sirket_turu')}>
                  <option value="">Seçiniz</option>
                  <option value="anonim_sirket">Anonim Şirket (A.Ş.)</option>
                  <option value="limited_sirket">Limited Şirket (Ltd. Şti.)</option>
                  <option value="kolektif_sirket">Kolektif Şirket</option>
                  <option value="komandit_sirket">Komandit Şirket</option>
                  <option value="kooperatif">Kooperatif</option>
                  <option value="diger">Diğer</option>
                </select>
              </div>
            )}

            {mukellefTuru === 'sahis' && (
              <div>
                <label className="label">Vergilendirme Şekli</label>
                <select className="input" {...register('vergilendirme_sekli')}>
                  <option value="gercek_usul">Gerçek Usul</option>
                  <option value="basit_usul">Basit Usul</option>
                  <option value="goturu">Götürü</option>
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Vergi / Ticaret Bilgileri */}
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Vergi & Ticaret Bilgileri</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Vergi Kimlik No (VKN) *</label>
              <input className="input font-mono" placeholder="1234567890"
                {...register('vergi_no', { required: 'VKN zorunludur', minLength: { value: 10, message: '10 haneli VKN giriniz' } })} />
              {errors.vergi_no && <p className="text-danger-500 text-xs mt-1">{errors.vergi_no.message}</p>}
            </div>
            <div>
              <label className="label">Vergi Dairesi *</label>
              <input className="input" placeholder="Kadıköy VD"
                {...register('vergi_dairesi', { required: 'Vergi dairesi zorunludur' })} />
              {errors.vergi_dairesi && <p className="text-danger-500 text-xs mt-1">{errors.vergi_dairesi.message}</p>}
            </div>
            <div>
              <label className="label">Ticaret Sicil No</label>
              <input className="input" placeholder="123456" {...register('ticaret_sicil_no')} />
            </div>
            <div>
              <label className="label">MERSİS No</label>
              <input className="input font-mono" placeholder="0123456789012345" {...register('mersis_no')} />
            </div>
          </div>
        </div>

        {/* İletişim */}
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">İletişim Bilgileri</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="label">Adres</label>
              <textarea className="input" rows={2} placeholder="Tam adres..." {...register('adres')} />
            </div>
            <div>
              <label className="label">İl</label>
              <select className="input" {...register('il')}>
                <option value="">Seçiniz</option>
                {ILLER.map(il => <option key={il} value={il}>{il}</option>)}
              </select>
            </div>
            <div>
              <label className="label">İlçe</label>
              <input className="input" placeholder="İlçe" {...register('ilce')} />
            </div>
            <div>
              <label className="label">Telefon</label>
              <input className="input" placeholder="0212 000 00 00" {...register('telefon')} />
            </div>
            <div>
              <label className="label">E-posta</label>
              <input type="email" className="input" placeholder="info@firma.com" {...register('email')} />
            </div>
          </div>
        </div>

        {/* Faaliyet */}
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Faaliyet Bilgileri</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="label">Faaliyet Konusu</label>
              <textarea className="input" rows={2} placeholder="Toptan gıda ürünleri ticareti..." {...register('faaliyet_konusu')} />
            </div>
            <div>
              <label className="label">NACE Kodu</label>
              <input className="input font-mono" placeholder="46.39" {...register('nace_kodu')} />
            </div>
            <div>
              <label className="label">Kuruluş Tarihi</label>
              <input type="date" className="input" {...register('kurulis_tarihi')} />
            </div>
            <div className="col-span-2">
              <label className="label">Notlar</label>
              <textarea className="input" rows={2} {...register('notlar')} />
            </div>
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <Link to={isEdit ? `/firmalar/${id}` : '/firmalar'} className="btn-secondary">
            İptal
          </Link>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Kaydediliyor...' : (isEdit ? 'Güncelle' : 'Firmayı Kaydet')}
          </button>
        </div>
      </form>
    </div>
  )
}
