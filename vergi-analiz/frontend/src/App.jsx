import { Routes, Route, Navigate } from 'react-router-dom'
import useAuthStore from './store/authStore'
import Layout from './components/ui/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import FirmaListPage from './pages/FirmaListPage'
import FirmaFormPage from './pages/FirmaFormPage'
import FirmaDetayPage from './pages/FirmaDetayPage'
import MizanYuklePage from './pages/MizanYuklePage'
import RaporPage from './pages/RaporPage'

function ProtectedRoute({ children }) {
  const token = useAuthStore((s) => s.token)
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="firmalar" element={<FirmaListPage />} />
        <Route path="firmalar/yeni" element={<FirmaFormPage />} />
        <Route path="firmalar/:id" element={<FirmaDetayPage />} />
        <Route path="firmalar/:id/duzenle" element={<FirmaFormPage />} />
        <Route path="firmalar/:id/mizan-yukle" element={<MizanYuklePage />} />
        <Route path="raporlar/:id" element={<RaporPage />} />
      </Route>
    </Routes>
  )
}
