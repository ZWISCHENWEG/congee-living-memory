import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import updateLocale from 'dayjs/plugin/updateLocale';

dayjs.extend(relativeTime);
dayjs.extend(updateLocale);

export const formatDate = (date: string | Date, format = 'MMM D, YYYY') => {
  return dayjs(date).format(format);
};

export const formatRelativeTime = (date: string | Date) => {
  return dayjs(date).fromNow();
};

export const truncateText = (text: string, length: number) => {
  if (text.length <= length) return text;
  return `${text.slice(0, length)}...`;
};
