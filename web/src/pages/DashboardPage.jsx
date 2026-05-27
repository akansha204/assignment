
import React, { useEffect } from 'react';
import useActivityStore from '../store/activityStore';
import styles from './DashboardPage.module.css';

const columns = [
  { key: 'source_type', label: 'Source' },
  { key: 'activity_type', label: 'Activity Type' },
  { key: 'scope', label: 'Scope' },
  { key: 'quantity', label: 'Quantity' },
  { key: 'unit', label: 'Unit' },
  { key: 'review_status', label: 'Review Status' },
  { key: 'suspicious', label: 'Suspicious' },
  { key: 'flag_reason', label: 'Flag Reason' },
];

const DashboardPage = () => {
  const { activities, loading, error, fetchActivities } = useActivityStore();

  useEffect(() => {
    fetchActivities();
    // eslint-disable-next-line
  }, []);

  return (
    <div className={styles.dashboardBg}>
      <div className={styles.title}>ESG Activity Dashboard</div>
      <div className={styles.tableWrap}>
        {loading ? (
          <div className={styles.loading}>Loading activities...</div>
        ) : error ? (
          <div className={styles.error}>Error loading activities.</div>
        ) : activities && activities.length === 0 ? (
          <div className={styles.empty}>No activities found.</div>
        ) : (
          <table className={styles.table}>
            <thead className={styles.thead}>
              <tr>
                {columns.map(col => (
                  <th key={col.key}>{col.label}</th>
                ))}
              </tr>
            </thead>
            <tbody className={styles.tbody}>
              {activities.map((row, idx) => (
                <tr key={row.id || idx}>
                  {columns.map(col => (
                    <td key={col.key}>
                      {col.key === 'suspicious'
                        ? row[col.key] ? 'Yes' : 'No'
                        : row[col.key] ?? ''}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
