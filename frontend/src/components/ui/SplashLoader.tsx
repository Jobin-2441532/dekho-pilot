import { motion } from 'framer-motion'
import styles from './SplashLoader.module.css'

export default function SplashLoader() {
  return (
    <motion.div
      className={styles.loaderScreen}
      initial={{ opacity: 1 }}
      exit={{ 
        opacity: 0, 
        y: -40, 
        transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } 
      }}
    >
      <div className={styles.logoColumn}>
        <div className={styles.logoWrap}>
          <svg viewBox="0 0 400 400" width="220" height="220" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="walnutGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#5C3A21" />
                <stop offset="100%" stopColor="#B8834E" />
              </linearGradient>
            </defs>

            {/* Outer D arc */}
            <g className={`${styles.piece} ${styles.outerArc}`}>
              <path d="M 175 90
                       L 175 310
                       C 260 310, 320 265, 320 200
                       C 320 135, 260 90, 175 90 Z"
                    fill="none" stroke="url(#walnutGradient)" strokeWidth="26" strokeLinejoin="round"/>
            </g>

            {/* Inner D arc */}
            <g className={`${styles.piece} ${styles.innerArc}`}>
              <path d="M 195 130
                       L 195 270
                       C 245 270, 280 240, 280 200
                       C 280 160, 245 130, 195 130 Z"
                    fill="none" stroke="url(#walnutGradient)" strokeWidth="14" strokeLinejoin="round"/>
            </g>

            {/* Vertical spine */}
            <g className={`${styles.piece} ${styles.spine}`}>
              <rect x="163" y="90" width="24" height="220" fill="url(#walnutGradient)" rx="4"/>
            </g>

            {/* Top-left flourish */}
            <g className={`${styles.piece} ${styles.flourish}`}>
              <rect x="110" y="140" width="14" height="70" fill="url(#walnutGradient)" rx="4"/>
              <rect x="88" y="192" width="90" height="16" fill="url(#walnutGradient)" rx="4"/>
            </g>

            {/* Bottom-left foot */}
            <g className={`${styles.piece} ${styles.foot}`}>
              <rect x="118" y="255" width="60" height="16" fill="url(#walnutGradient)" rx="4"/>
            </g>

            {/* Center dot */}
            <g className={`${styles.piece} ${styles.dot}`}>
              <circle cx="223" cy="200" r="15" fill="#5C3A21"/>
            </g>
          </svg>
        </div>
        <div className={styles.tagline}>the habit is the plan</div>
      </div>
    </motion.div>
  )
}
