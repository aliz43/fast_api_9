'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

const API_URL = 'http://localhost:8000/api';

export default function AdminPage() {
  const [adminMessage, setAdminMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userRole = localStorage.getItem('user_role');
    
    if (!token) {
      router.push('/login');
      return;
    }

    if (userRole !== 'admin') {
      router.push('/dashboard');
      return;
    }

    const fetchAdminData = async () => {
      try {
        const response = await axios.get(`${API_URL}/admin-data`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAdminMessage(response.data.admin_message);
      } catch (error) {
        router.push('/dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchAdminData();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_role');
    router.push('/login');
  };

  if (loading) {
    return <p className="text-center mt-10">Загрузка...</p>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Админ Панель</h1>
      <p className="mt-4 text-xl p-4 bg-purple-100 border border-purple-400 rounded-md">{adminMessage}</p>
      
      <div className="mt-4">
        <a href="/dashboard" className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 inline-block mr-2">
          Назад к панели
        </a>
        <button onClick={handleLogout} className="bg-red-500 text-white p-2 rounded hover:bg-red-600">
          Выйти
        </button>
      </div>
    </div>
  );
} 