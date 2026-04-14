import { useEffect, useMemo, useRef, useState } from 'react'
import axios from 'axios'
import mqtt from 'mqtt'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'

import './App.css'
import {
  apiBaseUrl,
  manualInputPath,
  mqttTopicAbsensi,
  mqttWsUrl,
  prayerTimePath,
  profilePath,
  reportPath,
  schoolDataPath,
  userManagementPath,
} from './config'
import { LoadingSpinner, Toast } from './components/Common'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import ManualInputPage from './pages/ManualInputPage'
import NotificationPage from './pages/NotificationPage'
import PrayerTimeSettingsPage from './pages/PrayerTimeSettingsPage'
import ProfilePage from './pages/ProfilePage'
import ReportPage from './pages/ReportPage'
import SchoolDataPage from './pages/SchoolDataPage'
import UserFormPage from './pages/UserFormPage'
import UserManagementPage from './pages/UserManagementPage'

function App() {
  const navigate = useNavigate()
  const location = useLocation()

  const [loginForm, setLoginForm] = useState({
    username: '',
    password: '',
  })

  const [registerForm, setRegisterForm] = useState({
    username: '',
    full_name: '',
    email: '',
    no_telp: '',
    role: 'siswa',
    password: '',
    confirmPassword: '',
  })

  const [loading, setLoading] = useState(false)
  const [checkingSession, setCheckingSession] = useState(true)
  const [dashboardLoading, setDashboardLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [authUser, setAuthUser] = useState(null)
  const [dashboardData, setDashboardData] = useState(null)
  const [realtimeStatus, setRealtimeStatus] = useState('offline')
  const [realtimeLastUpdate, setRealtimeLastUpdate] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [notificationLoading, setNotificationLoading] = useState(false)
  const [toast, setToast] = useState(null)
  const mqttRefreshTimerRef = useRef(null)
  const toastTimerRef = useRef(null)

  const api = useMemo(
    () =>
      axios.create({
        baseURL: apiBaseUrl,
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      }),
    [],
  )

  const clearSession = () => {
    localStorage.removeItem('sikap_token')
    localStorage.removeItem('sikap_token_type')
    localStorage.removeItem('sikap_expires_at')
    localStorage.removeItem('sikap_user')
    setAuthUser(null)
    setDashboardData(null)
    setNotifications([])
    setUnreadCount(0)
  }

  const getAuthHeaders = () => {
    const token = localStorage.getItem('sikap_token')
    const tokenType = localStorage.getItem('sikap_token_type') || 'Bearer'

    if (!token) {
      return null
    }

    return {
      Authorization: `${tokenType} ${token}`,
    }
  }

  const fetchCurrentUser = async () => {
    const headers = getAuthHeaders()

    if (!headers) {
      throw new Error('Token tidak ditemukan.')
    }

    const { data } = await api.get('/auth/me', { headers })

    if (!data?.success || !data?.data) {
      throw new Error('Respons profil user tidak valid.')
    }

    setAuthUser(data.data)
    localStorage.setItem('sikap_user', JSON.stringify(data.data))
    return data.data
  }

  const fetchDashboard = async ({ silent = false } = {}) => {
    const headers = getAuthHeaders()

    if (!headers) {
      throw new Error('Token tidak ditemukan.')
    }

    if (!silent) {
      setDashboardLoading(true)
    }
    try {
      const { data } = await api.get('/dashboard', { headers })

      if (!data?.success || !data?.data) {
        throw new Error('Respons dashboard tidak valid.')
      }

      setDashboardData(data.data)
      return data.data
    } finally {
      if (!silent) {
        setDashboardLoading(false)
      }
    }
  }

  const getNotificationPayload = (responseBody) => {
    const candidates = [responseBody?.data, responseBody?.message]
    return (
      candidates.find(
        (item) =>
          item &&
          typeof item === 'object' &&
          (Array.isArray(item.notifikasi) || typeof item.unread_count === 'number'),
      ) || {}
    )
  }

  const requestNotifikasi = async (method, path = '', config = {}) => {
    const candidates = [...new Set([`/api/notifikasi${path}`, `${apiBaseUrl}/notifikasi${path}`])]
    let lastError = null

    for (const url of candidates) {
      try {
        return await axios({
          method,
          url,
          timeout: 10000,
          ...config,
        })
      } catch (error) {
        const status = error?.response?.status
        if (status === 404 && url !== candidates[candidates.length - 1]) {
          lastError = error
          continue
        }
        throw error
      }
    }

    throw lastError || new Error('Gagal mengakses endpoint notifikasi.')
  }

  const fetchNotifications = async ({ silent = false } = {}) => {
    const headers = getAuthHeaders()

    if (!headers) {
      return
    }

    if (!silent) {
      setNotificationLoading(true)
    }

    try {
      const { data } = await requestNotifikasi('get', '', {
        headers,
        params: { page: 1, per_page: 20 },
      })
      const payload = getNotificationPayload(data)
      setNotifications(Array.isArray(payload.notifikasi) ? payload.notifikasi : [])
      setUnreadCount(Number(payload.unread_count || 0))
    } catch (requestError) {
      if (!silent) {
        const apiMessage =
          requestError?.response?.data?.message ||
          requestError?.response?.data?.error ||
          requestError?.message ||
          'Gagal memuat notifikasi.'
        setError(apiMessage)
      }
    } finally {
      if (!silent) {
        setNotificationLoading(false)
      }
    }
  }

  useEffect(() => {
    const bootstrapSession = async () => {
      const token = localStorage.getItem('sikap_token')

      if (!token) {
        setCheckingSession(false)
        return
      }

      try {
        const user = await fetchCurrentUser()
        setSuccessMessage(
          `Sesi aktif. Selamat datang kembali, ${user.full_name || user.username}.`,
        )
        try {
          await fetchDashboard()
        } catch (_dashboardError) {
          setError('Sesi login aktif, tetapi data dashboard belum berhasil dimuat.')
        }
        await fetchNotifications({ silent: true })
      } catch (_err) {
        clearSession()
      } finally {
        setCheckingSession(false)
      }
    }

    bootstrapSession()
  }, [])

  useEffect(() => {
    if (error) {
      setToast({ type: 'error', message: error })
      return
    }

    if (successMessage) {
      setToast({ type: 'success', message: successMessage })
    }
  }, [error, successMessage])

  useEffect(() => {
    if (!toast?.message) {
      return
    }

    if (toastTimerRef.current) {
      window.clearTimeout(toastTimerRef.current)
    }

    toastTimerRef.current = window.setTimeout(() => {
      setToast(null)
      toastTimerRef.current = null
    }, 3500)

    return () => {
      if (toastTimerRef.current) {
        window.clearTimeout(toastTimerRef.current)
      }
    }
  }, [toast])

  const handleLoginChange = (event) => {
    const { name, value } = event.target
    setLoginForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleRegisterChange = (event) => {
    const { name, value } = event.target
    setRegisterForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSwitchMode = (nextMode) => {
    setError('')
    setSuccessMessage('')
    navigate(nextMode === 'register' ? '/register' : '/login')
  }

  const handleLogin = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    if (!loginForm.username || !loginForm.password) {
      setError('Username dan password wajib diisi.')
      return
    }

    setLoading(true)

    try {
      const { data } = await api.post('/auth/login', loginForm)
      const responseData = data?.data

      if (!data?.success || !responseData?.access_token) {
        setError('Login gagal. Respons API tidak valid.')
        return
      }

      localStorage.setItem('sikap_token', responseData.access_token)
      localStorage.setItem('sikap_token_type', responseData.token_type || 'Bearer')
      localStorage.setItem('sikap_expires_at', String(responseData.expires_at || 0))

      const user = await fetchCurrentUser()
      try {
        await fetchDashboard()
      } catch (_dashboardError) {
        setError('Login berhasil, tetapi data dashboard belum berhasil dimuat.')
      }
      await fetchNotifications({ silent: true })

      const displayName = user?.full_name || user?.username || loginForm.username
      setSuccessMessage(`Login berhasil. Selamat datang, ${displayName}.`)
      setLoginForm((prev) => ({ ...prev, password: '' }))
      navigate('/dashboard', { replace: true })
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Terjadi kesalahan saat menghubungi server.'

      setError(apiMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    if (!registerForm.username || !registerForm.full_name || !registerForm.password) {
      setError('Username, nama lengkap, dan password wajib diisi.')
      return
    }

    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Konfirmasi password tidak sama.')
      return
    }

    const headers = getAuthHeaders()

    if (!headers) {
      setError('Login dulu sebagai admin untuk membuat user baru.')
      return
    }

    setLoading(true)

    try {
      const payload = {
        username: registerForm.username,
        full_name: registerForm.full_name,
        email: registerForm.email || null,
        no_telp: registerForm.no_telp || null,
        role: registerForm.role,
        password: registerForm.password,
      }

      const { data } = await api.post('/users', payload, { headers })

      if (!data?.success) {
        setError(data?.message || 'Registrasi gagal.')
        return
      }

      setSuccessMessage(data?.message || 'Registrasi berhasil.')
      setRegisterForm({
        username: '',
        full_name: '',
        email: '',
        no_telp: '',
        role: 'siswa',
        password: '',
        confirmPassword: '',
      })
    } catch (requestError) {
      const status = requestError?.response?.status
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Terjadi kesalahan saat menghubungi server.'

      if (status === 404) {
        setError('Endpoint registrasi (/api/v1/users) belum tersedia di backend saat ini.')
      } else if (status === 403) {
        setError('Akses ditolak. Registrasi user hanya untuk admin.')
      } else {
        setError(apiMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    const headers = getAuthHeaders()

    try {
      if (headers) {
        await api.post('/auth/logout', {}, { headers })
      }
    } catch (_err) {
      // Tetap lanjut clear session walaupun revoke token gagal.
    } finally {
      clearSession()
      setSuccessMessage('Logout berhasil.')
      setError('')
      navigate('/login', { replace: true })
    }
  }

  const handleRefreshDashboard = async () => {
    setError('')
    setSuccessMessage('')

    try {
      await fetchDashboard()
      setSuccessMessage('Dashboard berhasil diperbarui.')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Gagal memuat dashboard.'

      setError(apiMessage)
    }
  }

  const handleOpenNotifikasi = () => {
    setError('')
    setSuccessMessage('')
    void fetchNotifications({ silent: true })
    navigate('/notifikasi')
  }

  const handleRefreshNotifications = async () => {
    setError('')
    setSuccessMessage('')
    await fetchNotifications()
  }

  const handleMarkNotificationAsRead = async (notification) => {
    const notificationId = notification?.id_notifikasi || notification?.id
    if (!notificationId || notification?.is_read) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    try {
      await requestNotifikasi('put', `/${notificationId}/read`, { headers })
      setNotifications((prev) =>
        prev.map((item) =>
          (item.id_notifikasi || item.id) === notificationId
            ? { ...item, is_read: true, dibaca: true }
            : item,
        ),
      )
      setUnreadCount((prev) => Math.max(0, prev - 1))
      setSuccessMessage('Notifikasi ditandai sudah dibaca.')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Gagal menandai notifikasi.'
      setError(apiMessage)
    }
  }

  const handleOpenManualInput = () => {
    setError('')
    setSuccessMessage('')
    navigate(manualInputPath)
  }

  const handleOpenProfile = () => {
    setError('')
    setSuccessMessage('')
    navigate(profilePath)
  }

  const handleOpenSchoolData = () => {
    setError('')
    setSuccessMessage('')
    navigate(schoolDataPath)
  }

  const handleOpenPrayerTime = () => {
    setError('')
    setSuccessMessage('')
    navigate(prayerTimePath)
  }

  const handleOpenReport = () => {
    setError('')
    setSuccessMessage('')
    navigate(reportPath)
  }

  const handleOpenUserManagement = () => {
    setError('')
    setSuccessMessage('')
    navigate(userManagementPath)
  }

  const handleOpenAddUser = () => {
    navigate(`${userManagementPath}/new`)
  }

  const handleOpenEditUser = (userId) => {
    navigate(`${userManagementPath}/${userId}/edit`)
  }

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  const handleBackToUserManagement = () => {
    navigate(userManagementPath)
  }
  useEffect(() => {
    if (!authUser) {
      setRealtimeStatus('offline')
      setRealtimeLastUpdate(null)
      return
    }

    let isActive = true
    setRealtimeStatus('connecting')
    const client = mqtt.connect(mqttWsUrl, {
      reconnectPeriod: 5000,
      connectTimeout: 10000,
    })

    client.on('connect', () => {
      if (!isActive) {
        return
      }

      setRealtimeStatus('connected')
      client.subscribe(mqttTopicAbsensi, (subscribeError) => {
        if (subscribeError && isActive) {
          setRealtimeStatus('error')
        }
      })
    })

    client.on('reconnect', () => {
      if (isActive) {
        setRealtimeStatus('reconnecting')
      }
    })

    client.on('close', () => {
      if (isActive) {
        setRealtimeStatus('offline')
      }
    })

    client.on('error', () => {
      if (isActive) {
        setRealtimeStatus('error')
      }
    })

    client.on('message', (topic) => {
      if (topic !== mqttTopicAbsensi || !isActive) {
        return
      }

      if (mqttRefreshTimerRef.current) {
        window.clearTimeout(mqttRefreshTimerRef.current)
      }

      mqttRefreshTimerRef.current = window.setTimeout(async () => {
        try {
          await fetchDashboard({ silent: true })
          if (isActive) {
            setRealtimeLastUpdate(new Date().toISOString())
          }
        } catch (_err) {
          // Silent: tetap tunggu event berikutnya.
        }
      }, 350)
    })

    return () => {
      isActive = false
      if (mqttRefreshTimerRef.current) {
        window.clearTimeout(mqttRefreshTimerRef.current)
        mqttRefreshTimerRef.current = null
      }
      client.end(true)
    }
  }, [authUser])

  if (checkingSession) {
    return (
      <main className="login-page">
        <section className="login-card">
          <h1>SIKAP</h1>
          <LoadingSpinner label="Memeriksa sesi login dan menyiapkan dashboard..." />
        </section>
      </main>
    )
  }

  const authMode = location.pathname === '/register' ? 'register' : 'login'

  return (
    <>
      <Toast toast={toast} onClose={() => setToast(null)} />
      <Routes>
      <Route path="/" element={<Navigate to={authUser ? '/dashboard' : '/login'} replace />} />
      <Route
        path="/login"
        element={
          authUser ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <AuthPage
              mode={authMode}
              loading={loading}
              checkingSession={checkingSession}
              loginForm={loginForm}
              registerForm={registerForm}
              error={error}
              successMessage={successMessage}
              onLoginChange={handleLoginChange}
              onRegisterChange={handleRegisterChange}
              onLogin={handleLogin}
              onRegister={handleRegister}
              onSwitchMode={handleSwitchMode}
              apiBaseUrlValue={apiBaseUrl}
            />
          )
        }
      />
      <Route
        path="/register"
        element={
          authUser ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <AuthPage
              mode={authMode}
              loading={loading}
              checkingSession={checkingSession}
              loginForm={loginForm}
              registerForm={registerForm}
              error={error}
              successMessage={successMessage}
              onLoginChange={handleLoginChange}
              onRegisterChange={handleRegisterChange}
              onLogin={handleLogin}
              onRegister={handleRegister}
              onSwitchMode={handleSwitchMode}
              apiBaseUrlValue={apiBaseUrl}
            />
          )
        }
      />
      <Route
        path="/dashboard"
        element={
          authUser ? (
            <DashboardPage
              authUser={authUser}
              dashboardData={dashboardData}
              dashboardLoading={dashboardLoading}
              realtimeStatus={realtimeStatus}
              realtimeLastUpdate={realtimeLastUpdate}
              error={error}
              successMessage={successMessage}
              onRefresh={handleRefreshDashboard}
              onOpenNotifikasi={handleOpenNotifikasi}
              onOpenManualInput={handleOpenManualInput}
              onOpenProfile={handleOpenProfile}
              onOpenSchoolData={handleOpenSchoolData}
              onOpenPrayerTime={handleOpenPrayerTime}
              onOpenReport={handleOpenReport}
              onOpenUserManagement={handleOpenUserManagement}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={profilePath}
        element={
          authUser ? (
            <ProfilePage
              authUser={authUser}
              dashboardData={dashboardData}
              onBackToDashboard={handleBackToDashboard}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={schoolDataPath}
        element={
          authUser ? (
            <SchoolDataPage
              authUser={authUser}
              api={api}
              getAuthHeaders={getAuthHeaders}
              onBackToDashboard={handleBackToDashboard}
              onOpenNotifikasi={handleOpenNotifikasi}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={reportPath}
        element={
          authUser ? (
            ['admin', 'kepsek', 'wali_kelas'].includes(authUser.role) ? (
              <ReportPage
                authUser={authUser}
                api={api}
                apiBaseUrlValue={apiBaseUrl}
                getAuthHeaders={getAuthHeaders}
                onBackToDashboard={handleBackToDashboard}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={prayerTimePath}
        element={
          authUser ? (
            authUser.role === 'admin' ? (
              <PrayerTimeSettingsPage
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToDashboard={handleBackToDashboard}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/notifikasi"
        element={
          authUser ? (
            <NotificationPage
              authUser={authUser}
              notifications={notifications}
              unreadCount={unreadCount}
              loading={notificationLoading}
              error={error}
              successMessage={successMessage}
              onRefresh={handleRefreshNotifications}
              onMarkAsRead={handleMarkNotificationAsRead}
              onBackToDashboard={handleBackToDashboard}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={manualInputPath}
        element={
          authUser ? (
            authUser.role === 'guru_piket' ? (
              <ManualInputPage
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToDashboard={handleBackToDashboard}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={userManagementPath}
        element={
          authUser ? (
            authUser.role === 'admin' ? (
              <UserManagementPage
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToDashboard={handleBackToDashboard}
                onOpenAddUser={handleOpenAddUser}
                onOpenEditUser={handleOpenEditUser}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={`${userManagementPath}/new`}
        element={
          authUser ? (
            authUser.role === 'admin' ? (
              <UserFormPage
                mode="create"
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToUserManagement={handleBackToUserManagement}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={`${userManagementPath}/:userId/edit`}
        element={
          authUser ? (
            authUser.role === 'admin' ? (
              <UserFormPage
                mode="edit"
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToUserManagement={handleBackToUserManagement}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route path="*" element={<Navigate to={authUser ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </>
  )
}

export default App
