import React from 'react';
import { motion } from 'framer-motion';
import styles from './ExpenseInsightCard.module.css';

interface ExpenseInsightCardProps {
  isLoading: boolean;
  mood?: string;
  headline?: string;
  subtext?: string;
  potentialSavings?: number;
}

export const ExpenseInsightCard: React.FC<ExpenseInsightCardProps> = ({
  isLoading,
  mood = 'balanced',
  headline,
  subtext,
  potentialSavings = 0,
}) => {
  const MOOD_ICONS: Record<string, string> = {
    housing_spike: '🏠',
    food_spike: '🍴',
    transport_spike: '🚗',
    shopping_spike: '🛍️',
    balanced: '⚖️',
    low_spend: '🍃',
    empty: '✨'
  };

  const skeletonClass = isLoading ? styles.skeleton : '';

  return (
    <motion.div

      className={styles.aiCard}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut', delay: 0.15 }}
    >
      <div className={styles.aiWatermark}>{MOOD_ICONS[mood] || '✨'}</div>

      <p className={styles.aiCardLabel}>INSIGHT</p>
      
      <div className={styles.aiCardContent}>
        <motion.p
          className={`${styles.aiCardTitle} ${skeletonClass}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.25 }}
        >
          {isLoading ? 'Loading insight...' : headline}
        </motion.p>
      </div>

      <motion.p
        className={`${styles.aiCardSub} ${skeletonClass}`}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.35 }}
      >
        {isLoading ? 'Analyzing your spending chapters for the month...' : subtext}
      </motion.p>

      <div className={styles.aiTarget}>
        <div className={styles.aiTargetHeader}>
          <span>Potential breathing room</span>
          <span>₹{potentialSavings.toLocaleString('en-IN')}</span>
        </div>
        <div className={styles.aiTargetTrack}>
          <motion.div
            className={styles.aiTargetFill}
            initial={{ width: 0 }}
            animate={{ width: '25%' }} // Static representation or dynamic if needed
            transition={{ duration: 0.6, delay: 0.4 }}
          />
        </div>
      </div>
    </motion.div>
  );
};
