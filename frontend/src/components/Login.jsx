import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import '../styles/Login.css'
import logo from '../assets/VOICEBOT_Logo.png'

export default function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await login(formData)
      if (result.success) {
        // Use navigate instead of window.location for smoother transition
        navigate('/dashboard', { replace: true })
      } else {
        setError(typeof result.error === 'object' ? result.error.message : result.error)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="logo-section">
        <img src={logo} alt="VOICEBOT AI Logo" className="project-logo" />
        <div className="project-tagline">
          AI that speaks health!!
        </div>
      </div>
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Welcome Back</h2>
        {error && <div className="error-message">{error}</div>}
        
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
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <div className="auth-links">
          Don't have an account? <Link to="/register">Register here</Link>
        </div>
      </form>
    </div>
  )
} 