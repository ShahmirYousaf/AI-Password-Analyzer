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
      const response = await axios.post('http://localhost:5000/analyze_password', { password });
      if (response.data) {
        setPasswordStrength(response.data.strength);
        setAnalysisResults(response.data); 
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
      {analysisResults.feedback && (
        <div className="additional-results">
          <p>Suggestions: {analysisResults.suggestions}</p>
          <p>Feedback: {analysisResults.feedback}</p>
          <p>Levenshtein Distance: {analysisResults.levenshtein_distance} </p>
          <p>Most Similar Password: {analysisResults.most_similar_password}</p>
          <p>Status: {analysisResults.status}</p>
        </div>
      )}
    </div>
      );
}

export default PasswordStrengthAnalyzer