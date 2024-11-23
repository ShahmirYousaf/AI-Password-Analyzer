import React , { useState } from 'react'
import AIlogo from './logo.png'
import './Styles.css';
import axios from 'axios';


const PasswordStrengthAnalyzer = () => {
  const [password, setPassword] = useState('');
  const [passwordStrength, setPasswordStrength] = useState('');
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [analysisResults, setAnalysisResults] = useState({});

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const togglePasswordVisibility = () => {
    setIsPasswordVisible(!isPasswordVisible);
  };

  const checkPasswordStrength = async () => {
    try {
      // Replace 'http://localhost:5000/analyze_password' with your actual Flask server URL
      const response = await axios.post('http://localhost:5000/analyze_password', { password });
      if (response.data) {
        setPasswordStrength(response.data.strength);
        setAnalysisResults(response.data); // Store all data if you want to display more info
      }
    } catch (error) {
      console.error('Failed to analyze password:', error);
      setPasswordStrength('Error analyzing password');
    }
  };

    return (
      <div className="password-container">
      <img className='logo' alt='Error' src={AIlogo} />
      <h1>AI Password Strength Analyzer</h1>
      <div className="password-input-wrapper">
        <input
          type={isPasswordVisible ? "text" : "password"}
          placeholder="Enter your password"
          value={password}
          onChange={handlePasswordChange}
          className="password-input"
        />
        <span onClick={togglePasswordVisibility} className="eye-icon">
          {isPasswordVisible ? '🙈' : '👁️'}
        </span>
        <button onClick={checkPasswordStrength}>Check</button>
      </div>
      {passwordStrength && (
        <div className="password-strength">
          <p>Password Strength: {passwordStrength}</p>
        </div>
      )}
      {/* Optionally display more results from analysis */}
      {analysisResults.feedback && (
        <div className="additional-results">
          <p>Feedback: {analysisResults.feedback}</p>
          {/* Add more display elements as needed based on your API response */}
        </div>
      )}
    </div>
      );
}

export default PasswordStrengthAnalyzer