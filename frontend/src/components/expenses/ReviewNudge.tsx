import React from 'react';
import { motion } from 'framer-motion';
import { Tag } from 'lucide-react';
import styles from './ReviewNudge.module.css';

interface ReviewNudgeProps {
  count: number;
  onClick: () => void;
}

export const ReviewNudge: React.FC<ReviewNudgeProps> = ({ count, onClick }) => {
  if (count === 0) return null;

  return (
    <motion.div
      className={styles.card}
      onClick={onClick}
      animate={{
        boxShadow: [
          '0 2px 8px rgba(0,0,0,0.05)',
          '0 2px 12px rgba(139, 99, 71, 0.15)',
          '0 2px 8px rgba(0,0,0,0.05)',
        ],
      }}
      transition={{
        duration: 4,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    >
      <div className={styles.left}>
        <div className={styles.iconBox}>
          <Tag size={18} className={styles.tagIcon} />
        </div>
        <div className={styles.content}>
          <p className={styles.title}>
            Help Dekho learn {count} transaction{count !== 1 ? 's' : ''}
          </p>
          <p className={styles.micro}>
            Takes 10 seconds. Helps Dekho understand you better.
          </p>
        </div>
      </div>
      <div className={styles.chevron}>›</div>
    </motion.div>
  );
};
