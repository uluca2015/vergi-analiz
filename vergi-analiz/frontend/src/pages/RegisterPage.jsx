import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import useAuthStore from '../store/authStore'

export default function RegisterPage() {
  const { register: registerUser, loading } = useAuthStore()
  const navigate = useNavigate()
  const { register, handleSubmit, watch, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    const result = await registerUser(data.email, data.password, data.fullName)
    if (result.success) {
      toast.success('Kayıt başarılı!')
      navigate('/')
    } else {
      toast.error(result.error)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-gray-900">Hesap Oluştur</h1>
          <p className="text-gray-500 mt-2">Vergi Analiz Platformuna kayıt olun</p>
        </div>
        <div className="card p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="label">Ad Soyad</label>
              <input className="input" placeholder="Ahmet Yılmaz" {...register('fullName')} />
            </div>
            <div>
              <label className="label">E-posta</label>
              <input type="email" className="input" placeholder="ornek@firma.com"
                {...register('email', { required: 'E-posta zorunludur' })} />
              {errors.email && <p className="text-danger-500 text-xs mt-1">{errors.email.message}</p>}
            </div>
            <div>
              <label className="label">Şifre</label>
              <input type="password" className="input" placeholder="••••••••"
                {...register('password', { required: true, minLength: { value: 6, message: 'En az 6 karakter' } })} />
              {errors.password && <p className="text-danger-500 text-xs mt-1">{errors.password.message}</p>}
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading ? 'Kayıt yapılıyor...' : 'Kayıt Ol'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-6">
            Hesabınız var mı?{' '}
            <Link to="/login" className="text-primary-600 hover:underline font-medium">Giriş yapın</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
