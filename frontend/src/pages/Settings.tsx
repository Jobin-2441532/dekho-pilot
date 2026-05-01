import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Moon, Sun, ChevronRight, User, LogOut } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'
import styles from './Settings.module.css'

export default function Settings() {
  const navigate = useNavigate()
  const { theme, toggleTheme } = useTheme()

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate(-1)} aria-label="Back">
          <ArrowLeft size={20} strokeWidth={1.75} />
        </button>
        <p className={styles.headerTitle}>Settings</p>
        <div style={{ width: 36 }} />
      </div>

      <div className={styles.px}>
        <div className={styles.profileSection}>
          <div className={styles.avatar}>
            <User size={32} />
          </div>
          <div>
            <h2 className={styles.userName}>Aarav Kumar</h2>
            <p className={styles.userPhone}>+91 98765 43210</p>
          </div>
        </div>
      </div>

      <div className={styles.px}>
        <div className={styles.section}>
          <p className={styles.sectionTitle}>Preferences</p>
          <div className={styles.card}>
            <div className={styles.row}>
              <div className={styles.rowLeft}>
                {theme === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
                <span>Dark Mode</span>
              </div>
              <label className={styles.switch}>
                <input type="checkbox" checked={theme === 'dark'} onChange={toggleTheme} />
                <span className={styles.slider}></span>
              </label>
            </div>
          </div>
        </div>

        <div className={styles.section}>
          <p className={styles.sectionTitle}>Highlights</p>
          <div className={styles.card}>
            <button className={styles.rowBtn} onClick={() => navigate('/monthly-wrap')}>
              <div className={styles.rowLeft}>
                <span>Monthly Wrap</span>
              </div>
              <ChevronRight size={20} className={styles.chevron} />
            </button>
          </div>
        </div>

        <div className={styles.section} style={{ marginTop: 'var(--space-6)' }}>
          <div className={styles.card}>
            <button className={styles.rowBtn} onClick={() => {
              localStorage.clear();
              navigate('/login');
            }} style={{ color: 'var(--color-negative)' }}>
              <div className={styles.rowLeft}>
                <LogOut size={20} />
                <span>Sign Out</span>
              </div>
            </button>
          </div>
        </div>

        <div className={styles.versionInfo}>
          <p>Dekho v1.0.0</p>
        </div>
      </div>
    </div>
  )
}
