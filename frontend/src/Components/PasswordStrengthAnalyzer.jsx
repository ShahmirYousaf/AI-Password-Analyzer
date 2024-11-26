import React, { useState } from "react";
import AIlogo from "./logo.png";
import "./Styles.css";
import axios from "axios";

const PasswordStrengthAnalyzer = () => {
  const [password, setPassword] = useState("");
  const [passwordStrength, setPasswordStrength] = useState("");
  const [styleCheck, setStyleCheck] = useState(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [analysisResults, setAnalysisResults] = useState({});
  const [additionalSuggestions, setAdditionalSuggestions] = useState([]);

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const togglePasswordVisibility = () => {
    setIsPasswordVisible(!isPasswordVisible);
  };

  const checkPasswordStrength = async () => {
    try {
      const response = await axios.post(
        "http://localhost:5000/analyze_password",
        { password }
      );
      if (response.data) {
        setPasswordStrength(response.data.strength);
        setStyleCheck(true);
        setAnalysisResults(response.data);
      }
    } catch (error) {
      console.error("Failed to analyze password:", error);
      setPasswordStrength("Error analyzing password");
    }
  };

  const fetchMoreSuggestions = async () => {
    try {
      const response = await axios.get(
        "http://localhost:5000/password_suggestions"
      );
      if (response.data) {
        console.log(response.data.suggested_passwords)
        setAdditionalSuggestions(response.data.suggested_passwords);
        setStyleCheck(false);
        setAnalysisResults({});
      }
    } catch (error) {
      console.error("Failed to fetch more suggestions:", error);
    }
  };

  return (
    <div className={`password-container ${styleCheck ? 'password-filled' : 'password-empty'}`}>
      <img className="logo" alt="Error" src={AIlogo} />
      <h1 className="main-heading">AI Password Strength Analyzer</h1>
      <div className="password-input-wrapper">
        <input
          type={isPasswordVisible ? "text" : "password"}
          placeholder="Enter your password"
          value={password}
          onChange={handlePasswordChange}
          className="password-input"
        />
        <span onClick={togglePasswordVisibility} className="eye-icon">
          {isPasswordVisible ? "🙈" : "👁️"}
        </span>
        <button onClick={checkPasswordStrength}>Check</button>
      </div>

      {passwordStrength && (
        <div className="password-strength">
          <p>Password Strength: {passwordStrength}</p>
        </div>
      )}

      {Object.keys(analysisResults).length > 0 && (
        <div className="additional-results">
          <h2>Analysis Results</h2>

          <div className="suggestions-section">
            <h3>Suggestions:</h3>
            <ul className="suggestions-list">
              {analysisResults.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>

          <div className="feedback-section">
            <h3>Feedback:</h3>
            <ul className="feedback-list">
              {analysisResults.feedback.split(". ").map((feedback, index) => (
                <li key={index}>{feedback.trim()}</li>
              ))}
            </ul>
          </div>

          <div className="details-section">
            <p>
              <strong>Levenshtein Distance:</strong>{" "}
              {analysisResults.levenshtein_distance}
            </p>
            <p>
              <strong>Most Similar Compromised Password:</strong>{" "}
              {analysisResults.most_similar_password}
            </p>
            <p>
              <strong>Status:</strong> {analysisResults.status}
            </p>
          </div>

          <button className="suggestions-btn" onClick={fetchMoreSuggestions}>
            Want more suggestions?
          </button>
        </div>
      )}

      {additionalSuggestions.length > 0 && (
        <div className="additional-results">
          <h2>Additional Suggestions</h2>
          <ul className="suggestions-list">
            {additionalSuggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PasswordStrengthAnalyzer;
