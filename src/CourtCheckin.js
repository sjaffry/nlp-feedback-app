import React, { useState, useEffect } from 'react';
import './App.css';
import axios from "axios";
import { Button, TextArea, Form } from 'semantic-ui-react';
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/js/all.js';
import { RotatingSquare } from  'react-loader-spinner';
import foothillslogo from './images/foothillslogowhite.svg';
import Cookies from 'js-cookie';

const CourtCheckin = () => {
  const [buttonColor, setButtonColor] = useState('blue');
  const [showSpinner, setShowSpinner] = useState(false);
  const [checkinStatusText, setCheckinStatusText] = useState('Tap to Check-in');
  const [playerName, setPlayerName] = useState('');
  const [checkinName, setCheckinName] = useState('');
  const [checkinTimestamp, setCheckinTimestamp] = useState('');
  const queryParams = new URLSearchParams(window.location.search);
  const courtNumber = queryParams.get("court_number");
  const businessName = queryParams.get("business_name");
  const inputHashToken = queryParams.get("t");
  const [rememberMe, setRememberMe] = useState(false);
  const [memberNames, setMemberNames] = useState([]);
  
  var cookieData = {
    username: playerName,
    rememberMe: rememberMe
  };
  

  const getUnixTime = () => {
    const now = new Date(); 
    return Math.floor(now.getTime() / 1000);
  }
  
  const roundedTS = (unixTimestamp) => {
    // Convert Unix timestamp to milliseconds
    const date = new Date(unixTimestamp * 1000);
    let minutes = date.getMinutes();
    minutes = minutes >= 30 ? 30 : 0;
    date.setMinutes(minutes, 0, 0);

    // Convert back to Unix timestamp
    return Math.floor(date.getTime() / 1000);
  };

  const roundedDate = (date) => {
    const minutes = date.getMinutes();
    const roundedMinutes = minutes >= 30 ? 30 : 0; 

    date.setMinutes(roundedMinutes); 
    date.setSeconds(0);
    date.setMilliseconds(0);

    return Math.floor(date.getTime() / 1000);  // Returning unix ts rounded to prior 30min mark
  };

  function unixTimeToDate(unixTime) {

    if (unixTime == '') {
      return '';
    }
    // Convert Unix timestamp to milliseconds (Unix time is in seconds)
    const date = new Date(unixTime * 1000);

    const months = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"];
    
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
    const now = new Date(); 
    const roundedUnixTime = roundedDate(now);
    try {
      const res = await axios.get('https://oqr6og2tf5.execute-api.us-west-2.amazonaws.com/Prod', {
        params: {
          court_number: courtNumber,
          checkin_timestamp: roundedUnixTime,
          business_name: businessName
        },           
        headers: {
        },
      });
      setCheckinTimestamp(res.data['checkin_timestamp']);
      setCheckinName(res.data['player_name']);
    } catch (error) {
      console.error('Error:', error);
      alert('Unexpected error. Please report it to front office');        
    }
  };

  const fetchMemberNames = async (firstNamePrefix) => {
    const now = new Date(); 
    const roundedUnixTime = roundedDate(now);
    try {
      const res = await axios.get('https://3zvcqe01h8.execute-api.us-west-2.amazonaws.com/Prod', {
        params: {
          court_number: courtNumber,
          first_name_prefix: firstNamePrefix,
          business_name: businessName,
          input_hash_token: inputHashToken
        },           
        headers: {
        },
      });
      const members = (res.data);
      setMemberNames(members);
    } catch (error) {
      console.error('Error:', error);
      alert('Unexpected error. Please report it to front office');        
    }
  };

  // Fetch the cookie data once on component mount
  useEffect(() => {
    const storedCookie = Cookies.get('userData');
    if (storedCookie) {
      const cookieData = JSON.parse(storedCookie);
      if (cookieData.rememberMe && cookieData.playerName) {
        setPlayerName(cookieData.playerName);
        setRememberMe(true);
      }
    }
  }, []);

  // Fetch member names when playerName changes
  useEffect(() => {
    if (playerName.length >= 2) {
      fetchMemberNames(playerName.substring(0, 2));
    } else {
      setMemberNames([]);
    }
    fetchCourtCheckin();
  }, [playerName]);

  const handleSubmit = async() => {

    const now = new Date(); 
    const roundedUnixTime = roundedDate(now);
    // If the checkin is within the current 30min window then it's not allowed
    if (roundedUnixTime == roundedTS(checkinTimestamp)) {
      alert('Court has already been checked in. See last checkin!')
      return;
    }

    setShowSpinner(true);
    setButtonColor('green');
    if (rememberMe) {
      cookieData = {
        playerName: playerName,
        rememberMe: rememberMe
      }
      const serializedData = JSON.stringify(cookieData);
      Cookies.set('userData', serializedData, { expires: 30 });
    }
    else {
      Cookies.remove('userData');
    }
    // Call saveCheckin API
    const res = await axios.put('https://oqr6og2tf5.execute-api.us-west-2.amazonaws.com/Prod', {}, {
      params: {
        business_name: businessName,
        court_number: courtNumber,
        checkin_timestamp: getUnixTime(),
        player_name: playerName,
        keep_warm: 'false'
      },
      headers: {
        'Content-Type': 'application/json'
      }
  });
      setShowSpinner(false);
      setCheckinStatusText('Check-in complete!')
      fetchCourtCheckin();
    };

  // Split playerName into first name and last name
  const [firstName, lastName] = playerName.split(' ');

  // Check if the entered name matches any of the member names
  const nameExists = memberNames.some(
    member => member.first_name === firstName && member.last_name === lastName
  );
  
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
              value={playerName}
              rows="1" 
              cols="30"
              style={{ textAlign: 'center' }}
              onChange={(e) => setPlayerName(e.target.value)} 
            />
            {memberNames.length > 0 && !nameExists && (
              <ul style={{ listStyleType: 'none', padding: 0 }}>
                {memberNames.map((memberNames, index) => (
                  <li key={index} onClick={() => setPlayerName(`${memberNames.first_name} ${memberNames.last_name}`)}
                  style={{
                    border: '1px solid #ccc', 
                    padding: '5px', 
                    margin: '5px 0',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    backgroundColor: '#fae4b1',
                    color: 'black'
                  }}
                  >
                    {memberNames.first_name} {memberNames.last_name}
                  </li>
                ))}
              </ul>
            )}
            <div style={{ margin: '10px 0' }}>
              <label>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  style={{ marginRight: '8px', verticalAlign: 'middle' }}
                />
                 <span style={{ verticalAlign: 'middle' }}>Remember me</span>
              </label>
            </div>
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
              disabled={!nameExists}
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
            Check-in by: {checkinName}
          </div>
        </header>
      </div>
    );
  };
  
  export default CourtCheckin;
  