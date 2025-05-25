import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './Navbar.css'

export default function Navbar({ isAuthenticated, setIsAuthenticated }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    setIsAuthenticated(false)
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <div className="logo">VoiceBot</div>
      <div className="nav-links">
        {isAuthenticated ? (
          <>
            <Link to="/">Home</Link>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </nav>
  )
}
