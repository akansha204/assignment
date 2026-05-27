

import React, { useEffect, useState } from 'react';
import useActivityStore from '../store/activityStore';
import styles from './DashboardPage.module.css';

const columns = [
  { key: 'source_type', label: 'Source' },
  { key: 'activity_type', label: 'Activity Type' },
  { key: 'scope', label: 'Scope' },
  { key: 'quantity', label: 'Quantity' },
  { key: 'unit', label: 'Unit' },
  { key: 'normalized_quantity', label: 'Norm. Qty' },
  { key: 'normalized_unit', label: 'Norm. Unit' },
  { key: 'review_status', label: 'Review Status' },
  { key: 'suspicious', label: 'Suspicious' },
  { key: 'flag_reason', label: 'Flag Reason' },
];

function StatusBadge({ status }) {
  if (status === 'approved') return <span className={`${styles.badge} ${styles.approved}`}>Approved</span>;
  if (status === 'rejected') return <span className={`${styles.badge} ${styles.rejected}`}>Rejected</span>;
  return <span className={`${styles.badge} ${styles.pending}`}>Pending</span>;
}

function EditModal({ open, onClose, onSave, row }) {
  const [form, setForm] = useState({
    quantity: row?.quantity ?? '',
    unit: row?.unit ?? '',
    normalized_quantity: row?.normalized_quantity ?? '',
    normalized_unit: row?.normalized_unit ?? '',
    flag_reason: row?.flag_reason ?? '',
  });
  useEffect(() => {
    if (open) {
      setForm({
        quantity: row?.quantity ?? '',
        unit: row?.unit ?? '',
        normalized_quantity: row?.normalized_quantity ?? '',
        normalized_unit: row?.normalized_unit ?? '',
        flag_reason: row?.flag_reason ?? '',
      });
    }
  }, [open, row]);
  if (!open) return null;
  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modal}>
        <div className={styles.modalTitle}>Edit Activity</div>
        <form className={styles.modalForm} onSubmit={e => { e.preventDefault(); onSave(form); }}>
          <label className={styles.modalLabel}>Quantity</label>
          <input className={styles.modalInput} type="number" value={form.quantity} onChange={e => setForm(f => ({ ...f, quantity: e.target.value }))} />
          <label className={styles.modalLabel}>Unit</label>
          <input className={styles.modalInput} type="text" value={form.unit} onChange={e => setForm(f => ({ ...f, unit: e.target.value }))} />
          <label className={styles.modalLabel}>Normalized Quantity</label>
          <input className={styles.modalInput} type="number" value={form.normalized_quantity} onChange={e => setForm(f => ({ ...f, normalized_quantity: e.target.value }))} />
          <label className={styles.modalLabel}>Normalized Unit</label>
          <input className={styles.modalInput} type="text" value={form.normalized_unit} onChange={e => setForm(f => ({ ...f, normalized_unit: e.target.value }))} />
          <label className={styles.modalLabel}>Flag Reason</label>
          <input className={styles.modalInput} type="text" value={form.flag_reason} onChange={e => setForm(f => ({ ...f, flag_reason: e.target.value }))} />
          <div className={styles.modalActions}>
            <button type="button" className={styles.modalCancel} onClick={onClose}>Cancel</button>
            <button type="submit" className={styles.modalSave}>Save</button>
          </div>
        </form>
      </div>
    </div>
  );
}

const DashboardPage = () => {
  const { activities, loading, error, fetchActivities, approveActivity, rejectActivity, editActivity } = useActivityStore();
  const [editId, setEditId] = useState(null);
  const [editRow, setEditRow] = useState(null);
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    fetchActivities();
    // eslint-disable-next-line
  }, []);

  const handleApprove = async (id) => {
    setActionLoading(l => ({ ...l, [id]: true }));
    await approveActivity(id);
    setActionLoading(l => ({ ...l, [id]: false }));
  };
  const handleReject = async (id) => {
    setActionLoading(l => ({ ...l, [id]: true }));
    await rejectActivity(id);
    setActionLoading(l => ({ ...l, [id]: false }));
  };
  const handleEdit = (row) => {
    setEditId(row.id);
    setEditRow(row);
  };
  const handleSaveEdit = async (form) => {
    setActionLoading(l => ({ ...l, [editId]: true }));
    await editActivity(editId, form);
    setActionLoading(l => ({ ...l, [editId]: false }));
    setEditId(null);
    setEditRow(null);
  };
  const handleCloseEdit = () => {
    setEditId(null);
    setEditRow(null);
  };

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
                <th>Actions</th>
              </tr>
            </thead>
            <tbody className={styles.tbody}>
              {activities.map((row, idx) => {
                const isSuspicious = row.suspicious;
                return (
                  <tr key={row.id || idx} className={isSuspicious ? styles.suspiciousRow : ''}>
                    {columns.map(col => (
                      <td key={col.key}>
                        {col.key === 'review_status' ? (
                          <StatusBadge status={row[col.key]} />
                        ) : col.key === 'suspicious' ? (
                          row[col.key] ? 'Yes' : 'No'
                        ) : row[col.key] ?? ''}
                      </td>
                    ))}
                    <td>
                      <div className={styles.actions}>
                        <button
                          className={`${styles.actionBtn} ${styles.approve}`}
                          disabled={row.review_status === 'approved' || actionLoading[row.id]}
                          onClick={() => handleApprove(row.id)}
                        >
                          Approve
                        </button>
                        <button
                          className={`${styles.actionBtn} ${styles.reject}`}
                          disabled={row.review_status === 'rejected' || actionLoading[row.id]}
                          onClick={() => handleReject(row.id)}
                        >
                          Reject
                        </button>
                        <button
                          className={`${styles.actionBtn} ${styles.edit}`}
                          disabled={actionLoading[row.id]}
                          onClick={() => handleEdit(row)}
                        >
                          Edit
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
      <EditModal
        open={!!editId}
        onClose={handleCloseEdit}
        onSave={handleSaveEdit}
        row={editRow}
      />
    </div>
  );
};

export default DashboardPage;
