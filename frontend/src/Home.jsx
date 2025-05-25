import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import './Home.css'
import Chatbot from './components/Chatbot'

const Home = () => {
  const navigate = useNavigate()
  const [isChatbotVisible, setIsChatbotVisible] = useState(false)

  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:8000/auth/logout')
      localStorage.removeItem('token')
      navigate('/login')
    } catch (error) {
      console.error('Error logging out:', error)
    }
  }

  return (
    <div className="home-container">
      <div className="header">
        <h1>Hospital Appointment System</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>
      
      <div className="main-content">
        <div className="features">
          <button onClick={() => navigate('/appointments')}>
            View Appointments
          </button>
          <button onClick={() => navigate('/doctors')}>
            Find Doctors
          </button>
          <button onClick={() => setIsChatbotVisible(!isChatbotVisible)}>
            {isChatbotVisible ? 'Hide Assistant' : 'Talk to Assistant'}
          </button>
        </div>

        {isChatbotVisible && (
          <div className="chatbot-wrapper">
            <Chatbot />
          </div>
        )}
      </div>
    </div>
  )
}

export default Home
