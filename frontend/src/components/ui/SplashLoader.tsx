import { motion } from 'framer-motion'
import styles from './SplashLoader.module.css'

export default function SplashLoader() {
  return (
    <motion.div
      className={styles.splashOverlay}
      initial={{ opacity: 1 }}
      exit={{ 
        opacity: 0,
        y: -40,
        transition: { duration: 0.5, ease: [0.4, 0, 0.2, 1] } 
      }}
    >
      <div className={styles.glowBg} />
      <div className={styles.splashContent}>
        {/* Animated Logo */}
        <motion.div
          className={styles.logoWrapper}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ 
            scale: 1, 
            opacity: 1,
            transition: { 
              duration: 0.8, 
              ease: [0.34, 1.56, 0.64, 1] // elastic scale-in
            } 
          }}
        >
          <img src="/logo-nobg.png" alt="Dekho Logo" className={styles.logoImg} />
        </motion.div>

        {/* Animated Brand Text */}
        <motion.h1
          className={styles.brandTitle}
          initial={{ opacity: 0, y: 15 }}
          animate={{ 
            opacity: 1, 
            y: 0,
            transition: { delay: 0.3, duration: 0.6, ease: 'easeOut' }
          }}
        >
          DEKHO
        </motion.h1>

        {/* Elegant Micro-Spinner */}
        <motion.div
          className={styles.spinnerWrapper}
          initial={{ opacity: 0 }}
          animate={{ 
            opacity: 1,
            transition: { delay: 0.5, duration: 0.4 }
          }}
        >
          <div className={styles.spinner} />
        </motion.div>
      </div>
    </motion.div>
  )
}
