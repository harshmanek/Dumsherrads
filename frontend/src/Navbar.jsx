import React from 'react'
import { Link } from 'react-router-dom'
import './Navbar.css'
import { useAuth } from './context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="navbar">
      <div className="logo">VoiceBot</div>
      <div className="nav-links">
        {user ? (
          <>
            <Link to="/">Home</Link>
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </nav>
  )
}
