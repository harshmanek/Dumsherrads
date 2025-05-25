import React, { useState } from 'react'
import './Home.css'
import Chatbot from './components/Chatbot'
import Sidebar from './components/Sidebar'

const Home = () => {
  const [active, setActive] = useState('home')

  return (
    <div className="main-layout">
      <Sidebar onSelect={setActive} active={active} />
      <div className="main-content-area">
        {active === 'home' && <Chatbot />}
      </div>
    </div>
  )
}

export default Home
