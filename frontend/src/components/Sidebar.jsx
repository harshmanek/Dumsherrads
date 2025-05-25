import React from 'react';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/VOICEBOT_Logo.png';
import './Sidebar.css';

export default function Sidebar({ onSelect, active }) {
  const { logout } = useAuth();

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <img src={logo} alt="VOICEBOT Logo" />
      </div>
      <div className="sidebar-menu">
        <button
          className={`sidebar-item${active === 'home' ? ' active' : ''}`}
          onClick={() => onSelect('home')}
        >
          Home
        </button>
        <button
          className="sidebar-item"
          onClick={logout}
        >
          Logout
        </button>
      </div>
    </div>
  );
} 