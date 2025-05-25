import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Login.css';
import logo from '../assets/VOICEBOT_Logo.png';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'PATIENT'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { register: registerUser } = useAuth();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await registerUser(formData);
      if (result.success) {
        navigate('/login', { replace: true });
      } else {
        setError(typeof result.error === 'object' ? result.error.message : result.error);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during registration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="logo-section">
        <img src={logo} alt="VOICEBOT AI Logo" className="project-logo" />
        <div className="project-tagline">
          An AI voice assistant that books hospital appointments — faster, smarter, human-free.
        </div>
      </div>
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Create Account</h2>
        {error && <div className="error-message">{error}</div>}
        
        <input
          type="text"
          placeholder="First Name"
          name="first_name"
          value={formData.first_name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          placeholder="Last Name"
          name="last_name"
          value={formData.last_name}
          onChange={handleChange}
          required
        />
        <input
          type="email"
          placeholder="Email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          placeholder="Password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
        />

        <button type="submit" disabled={loading} className={loading ? 'loading' : ''}>
          {loading ? 'Registering...' : 'Register'}
        </button>

        <div className="auth-links">
          Already have an account? <Link to="/login">Login here</Link>
        </div>
      </form>
    </div>
  );
} 