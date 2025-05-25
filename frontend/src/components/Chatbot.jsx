import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Chatbot.css';

const LoadingIndicator = () => (
  <div className="loading-indicator">
    <div className="loading-dots">
      <div className="dot"></div>
      <div className="dot"></div>
      <div className="dot"></div>
    </div>
  </div>
);

const formatBotResponse = (text) => {
  if (text.includes('Your appointments:')) {
    const [header, ...appointments] = text.split('\n');
    return (
      <div className="structured-response">
        <div className="response-header">{header}</div>
        <ul className="response-list">
          {appointments.map((apt, index) => (
            <li key={index}>{apt}</li>
          ))}
        </ul>
      </div>
    );
  }

  if (text.includes('appointment') && (text.includes('booked') || text.includes('scheduled'))) {
    return (
      <div className="structured-response">
        <div className="response-header">Appointment Confirmation</div>
        <p>{text}</p>
      </div>
    );
  }

  return <p>{text}</p>;
};

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text) => {
    if (!text.trim()) return;

    const userMessage = { text, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);

    try {
      const response = await axios.post('http://localhost:8000/agent/chat', {
        message: text
      });

      const botMessage = { text: response.data.response, sender: 'bot' };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { text: 'Sorry, I encountered an error. Please try again.', sender: 'bot' };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('file', audioBlob);

        try {
          const response = await axios.post('http://localhost:8000/whisper/transcribe', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });

          if (response.data && response.data.transcription) {
            await handleSend(response.data.transcription);
          } else {
            const errorMessage = { text: 'Sorry, I could not understand what you said. Please try again.', sender: 'bot' };
            setMessages((prev) => [...prev, errorMessage]);
          }
        } catch (error) {
          console.error('Error transcribing audio:', error);
          const errorMessage = { text: 'Sorry, there was an error processing your voice input. Please try again.', sender: 'bot' };
          setMessages((prev) => [...prev, errorMessage]);
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorderRef.current.start();
      setIsListening(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      const errorMessage = { text: 'Error accessing microphone. Please check your browser permissions.', sender: 'bot' };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      setIsListening(false);
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <span className="bot-icon">🤖</span>
        <span>AI Assistant</span>
      </div>
      <div className="chatbot-messages">
        <div className="welcome-message">
          Hello! I'm your voice-enabled AI assistant. I can help you:
          <ul>
            <li>Schedule appointments</li>
            <li>Check your existing appointments</li>
            <li>Reschedule or cancel appointments</li>
          </ul>
          Just type your message or click the microphone to speak!
        </div>
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            {message.sender === 'bot' ? formatBotResponse(message.text) : <p>{message.text}</p>}
          </div>
        ))}
        {isProcessing && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      <div className="chatbot-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend(input)}
          placeholder="Type your message..."
          disabled={isProcessing || isListening}
        />
        <button
          onClick={() => handleSend(input)}
          disabled={isProcessing || !input.trim() || isListening}
        >
          Send
        </button>
        <button
          onClick={isListening ? stopRecording : startRecording}
          className={isListening ? 'recording' : 'voice-button'}
          disabled={isProcessing}
        >
          {isListening ? 'Stop' : 'Speak'}
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
