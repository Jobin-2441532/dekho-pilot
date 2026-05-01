import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock } from 'lucide-react'
import Button from '../components/ui/Button'
import FloatingInput from '../components/ui/FloatingInput'
import styles from './Onboarding.module.css'

const API = import.meta.env.VITE_API_URL ?? `http://${window.location.hostname}:8000`

export default function Login() {
  const navigate = useNavigate()
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!email || !password || (!isLogin && !phone)) {
      setError('Please fill in all fields')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      if (isLogin) {
        // OAuth2 form-encoded login — our JWT backend expects form data
        const formData = new URLSearchParams()
        formData.append('username', email)
        formData.append('password', password)

        const res = await fetch(`${API}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData.toString()
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Login failed')

        // Store JWT token + mark onboarded
        localStorage.setItem('dekho_token', data.access_token)
        localStorage.setItem('dekho_onboarded', 'true')
      } else {
        // Register
        const res = await fetch(`${API}/api/v1/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, phone_number: phone })
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Registration failed')

        // Auto-login after register
        const formData = new URLSearchParams()
        formData.append('username', email)
        formData.append('password', password)
        const loginRes = await fetch(`${API}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData.toString()
        })
        const loginData = await loginRes.json()
        if (!loginRes.ok) throw new Error(loginData.detail || 'Auto-login after register failed')

        localStorage.setItem('dekho_token', loginData.access_token)
        localStorage.setItem('dekho_onboarded', 'true')
      }

      navigate('/home')
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.screen}>
      <div className={styles.inner}>
        <div className={styles.logo} style={{ marginBottom: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0px' }}>
          <img src="/logo-nobg.png" alt="Dekho Logo" style={{ width: 192, height: 192, objectFit: 'contain', marginBottom: '-40px' }} />
          <span className={styles.logoName}>Dekho</span>
        </div>

        <div className={styles.heading} style={{ marginBottom: '32px' }}>
          <h1>{isLogin ? 'Welcome back' : 'Create an account'}</h1>
          <p>Your calm finance companion</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginBottom: '32px' }}>
          <FloatingInput
            label="Email address"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
          {!isLogin && (
            <FloatingInput
              label="Phone number"
              type="tel"
              value={phone}
              onChange={e => setPhone(e.target.value)}
            />
          )}
          <FloatingInput
            label="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </div>

        {error && (
          <p style={{ color: 'var(--color-critical)', fontSize: '0.875rem', marginBottom: '16px', textAlign: 'center' }}>
            {error}
          </p>
        )}

        <div className={styles.navRow} style={{ flexDirection: 'column', gap: '16px' }}>
          <Button fullWidth onClick={handleSubmit} disabled={loading}>
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </Button>
          
          <button 
            style={{ background: 'none', border: 'none', color: 'var(--color-primary)', fontSize: '0.875rem', cursor: 'pointer', fontWeight: 500 }}
            onClick={() => {
              setIsLogin(!isLogin)
              setError('')
            }}
          >
            {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
          </button>
          
          <div className={styles.privacyNote} style={{ marginTop: '16px' }}>
            <Lock size={12} />
            <span>Secure authentication via FinanceAI.</span>
          </div>
        </div>
      </div>
    </div>
  )
}
