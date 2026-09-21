import axios from 'axios';

const getBaseURL = () => {
  if (typeof window !== 'undefined' && window.location) {
    return `http://${window.location.hostname}:8085/api`;
  }
  return 'http://localhost:8085/api';
};

const api = axios.create({
  baseURL: getBaseURL(),
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
