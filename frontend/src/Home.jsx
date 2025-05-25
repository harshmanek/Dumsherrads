import React from 'react'
import Chatbot from './components/Chatbot'
import Sidebar from './components/Sidebar'
import './Home.css'

const Home = () => {
  return (
    <div className="main-layout">
      <Sidebar />
      <div className="main-content chatbot-main-content">
        <Chatbot />
      </div>
    </div>
  )
}

export default Home
