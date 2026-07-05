import { Variants } from 'framer-motion';

const transition = {
  type: 'spring' as const,
  stiffness: 400,
  damping: 30,
};

export const fadeAnimation: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition },
  exit: { opacity: 0, transition },
};

export const slideUpAnimation: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition },
  exit: { opacity: 0, y: -10, transition },
};

export const scaleAnimation: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1, transition },
  exit: { opacity: 0, scale: 0.95, transition },
};

export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: 0.05,
    },
  },
};

export const staggerItem: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition },
};

export const dialogAnimation: Variants = {
  initial: { opacity: 0, scale: 0.95, y: 10 },
  animate: { opacity: 1, scale: 1, y: 0, transition },
  exit: { opacity: 0, scale: 0.95, y: 10, transition },
};
