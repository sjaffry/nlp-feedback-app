import React, { useState, useEffect } from 'react';
import './App.css';
import axios from "axios";
import { Button, TextArea, Form } from 'semantic-ui-react';
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/js/all.js';
import { RotatingSquare } from  'react-loader-spinner';
import foothillslogo from './images/foothillslogowhite.svg';
import { Link } from 'react-router-dom';

const CourtCheckin = () => {
  const [buttonColor, setButtonColor] = useState('blue');
  const [showSpinner, setShowSpinner] = useState(false);
  const [checkinStatusText, setCheckinStatusText] = useState('Tap to Check-in');
  const [playerName, setPlayerName] = useState('');
  const [textInput, setTextInput] = useState('');
  const [checkinTimestamp, setCheckinTimestamp] = useState('');
  const queryParams = new URLSearchParams(window.location.search);
  const courtNumber = queryParams.get("court_number");

  const getUnixTime = () => {
    const now = new Date(); 
    const minutes = now.getMinutes();
    const roundedMinutes = minutes >= 30 ? 30 : 0;  // We're rounding to the nearest 30mins prior

    now.setMinutes(roundedMinutes); 
    now.setSeconds(0);
    now.setMilliseconds(0);

    return Math.floor(now.getTime() / 1000);  // Convert to Unix time
  };

  function unixTimeToDate(unixTime) {

    if (unixTime == '') {
      return '';
    }
    // Convert Unix timestamp to milliseconds (Unix time is in seconds)
    const date = new Date(unixTime * 1000);

    const months = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"];
    
    // Rounding the minutes might require changing the hour and even the day
    date.setSeconds(0); // Reset seconds to 0
    date.setMilliseconds(0); // Reset milliseconds to 0

    // Format date to a readable string, only up to minutes
    const month = months[date.getMonth()];
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');

    return `${month}-${day} ${hours}:${minutes}`;
  }

  const fetchCourtCheckin = async () => {
    try {
      const res = await axios.get('https://oqr6og2tf5.execute-api.us-west-2.amazonaws.com/Prod', {
        params: {
          court_number: courtNumber,
          checkin_timestamp: getUnixTime()
        },           
        headers: {
        },
      });
      setCheckinTimestamp(res.data['checkin_timestamp']);
      setPlayerName(res.data['player_name']);
    } catch (error) {
      console.error('Error:', error);
      alert('Unexpected error. Please report it to front office');        
    }
  };

  // Call retrieve checkin API
  useEffect(() => {
    fetchCourtCheckin();
  }, []);

  const handleSubmit = async() => {

    // If the checkin is within the current 30min window then it's not allowed
    if (getUnixTime() == checkinTimestamp) {
      alert('Court has already been checked in. See last checkin!')
      return;
    }

    setShowSpinner(true);
    setButtonColor('green');

    // Call saveCheckin API
    const res = await axios.put('https://oqr6og2tf5.execute-api.us-west-2.amazonaws.com/Prod', {}, {
    params: {
      court_number: courtNumber,
      checkin_timestamp: getUnixTime(),
      player_name: textInput
    },
    headers: {
      'Content-Type': 'application/json'
    }
});
    setShowSpinner(false);
    setCheckinStatusText('Check-in complete!')
    fetchCourtCheckin();
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="top-section" style={{ marginBottom: '30px' }}>
          <img src={foothillslogo} alt="Organization logo" />
        </div>
        <h1 style={{ marginBottom: '20px' }}>Court {courtNumber} Check-in</h1>
        <div style={{ marginBottom: '10px' }}>
          Member full name
        </div>
        <Form>
          <TextArea 
            rows="1" 
            cols="30"
            onChange={(e) => setTextInput(e.target.value)} />
        </Form>
        <p></p>
        <Form>
          <Button 
            icon="check" 
            circular 
            size="massive"
            style={{
              backgroundColor: buttonColor, 
              color: 'white', 
              fontSize: '48px',
              padding: '30px 60px'
            }}
            onClick={handleSubmit}
          />
        </Form>
        {showSpinner && <RotatingSquare color="#d5d4d4" />}
        <p></p>
        <div style={{ marginBottom: '30px' }}>
        {checkinStatusText}
        </div>
        <p></p>
        <div style={{
          marginBottom: '10px',
          backgroundColor: 'blue',
          padding: '10px', 
          borderRadius: '5px' 
        }}>
        Last Check-in: {unixTimeToDate(checkinTimestamp)}
        <p></p>
        Check-in by: {playerName}
        </div>
      </header>
    </div>
  );
}

export default CourtCheckin;
