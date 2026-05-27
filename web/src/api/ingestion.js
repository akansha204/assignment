import client from './client';

export function uploadSAP(file) {
  const formData = new FormData();
  formData.append('file', file);
  return client.post('/api/upload/sap', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export function uploadUtility(file) {
  const formData = new FormData();
  formData.append('file', file);
  return client.post('/api/upload/utility', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export function uploadTravel(file) {
  const formData = new FormData();
  formData.append('file', file);
  return client.post('/api/upload/travel', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export function fetchActivities() {
  return client.get('/api/activities');
}

export function approveActivity(id) {
  return client.patch(`/api/activities/${id}/approve`);
}

export function rejectActivity(id) {
  return client.patch(`/api/activities/${id}/reject`);
}

export function editActivity(id, payload) {
  return client.patch(`/api/activities/${id}/edit`, payload);
}
