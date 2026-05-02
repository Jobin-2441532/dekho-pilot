import React from 'react';
import { motion } from 'framer-motion';
import styles from './TotalOutflowBadge.module.css';

interface TotalOutflowBadgeProps {
  percent: number;
  direction: 'up' | 'down' | 'flat';
}

export const TotalOutflowBadge: React.FC<TotalOutflowBadgeProps> = ({
  percent,
  direction,
}) => {
  let label = '';
  let variantClass = '';
  let icon = '';

  if (direction === 'up') {
    label = `${percent}% more than last month`;
    variantClass = styles.up;
    icon = '↑';
  } else if (direction === 'down') {
    label = `${percent}% less than last month`;
    variantClass = styles.down;
    icon = '↓';
  } else {
    label = 'Similar to last month';
    variantClass = styles.flat;
    icon = '•';
  }

  return (
    <motion.div
      className={`${styles.badge} ${variantClass}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2, delay: 0.1 }}
    >
      <span className={styles.icon}>{icon}</span>
      <span className={styles.label}>{label}</span>
    </motion.div>
  );
};
