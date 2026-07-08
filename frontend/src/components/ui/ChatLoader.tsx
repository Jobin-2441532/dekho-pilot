import styles from './ChatLoader.module.css'

export default function ChatLoader() {
  return (
    <div className={styles.loaderContainer}>
      <div className={styles.loader}>
        <div className={styles.box}></div>
        <svg width="0" height="0" viewBox="0 0 100 100">
          <mask id="clipping">
            <rect width="100" height="100" fill="white" />
            <polygon points="20,20 80,20 50,80" fill="black" />
            <polygon points="20,80 80,80 50,20" fill="black" />
            <polygon points="0,50 50,100 100,50 50,0" fill="black" />
            <polygon points="20,20 80,80 20,80" fill="black" />
            <polygon points="20,20 80,80 80,20" fill="black" />
            <polygon points="10,50 50,90 90,50" fill="black" />
            <polygon points="50,10 90,50 10,50" fill="black" />
          </mask>
        </svg>
      </div>
    </div>
  )
}
