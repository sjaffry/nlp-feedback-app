import React, { useState, useEffect } from 'react';
import './App.css';
import axios from "axios";
import { Button, TextArea, Form } from 'semantic-ui-react';
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/js/all.js';
import { RotatingSquare } from  'react-loader-spinner'
import foothillslogo from './images/foothillslogowhite.svg';
import { Link } from 'react-router-dom';
import { useNavigate } from "react-router-dom";


const TextInput = () => {
  const [showSpinner, setShowSpinner] = useState(false);
  const [textInput, setTextInput] = useState('');
  const queryParams = new URLSearchParams(window.location.search);
  const queryString = queryParams.get("qs"); 
  const voiceInputPage = `/?qs=${queryString}`;
  
  const generateRandomNumber = () => {
    const min = 10000000;
    const max = 99999999;
    const randomNumber = Math.floor(Math.random() * (max - min + 1)) + min;
    return randomNumber;
  }
  
  const handleSubmit = () => {
    // Form validation
    if (!textInput) {
      alert('Please enter feedback first!');
      return;
    }
    setShowSpinner(true);
    // Create a JSON file from the text input in the same format as the audio transcription job for code reusability downstream
    const jsonObject = { "results": { "transcripts": [ { "transcript": textInput } ] } };
    const jsonBlob = new Blob([JSON.stringify(jsonObject)], { type: 'application/json' });
    const jsonFile = new File([jsonBlob], 'feedback.json');
    const queryParams = new URLSearchParams(window.location.search);
    const businessName = queryParams.get("business_name");
    const fileName = `${generateRandomNumber()}.json`;
    const queryString = queryParams.get("qs");
    const fileType = "binary/octet-stream";
    const url = "https://mag7w370mh.execute-api.us-west-2.amazonaws.com/Prod?"
    const signUrl = url.concat("qs="+queryString+"&file_name="+fileName+"&upload_dir=transcribe-output");    
    axios.get(signUrl)
    .then(response => {
      var signedRequest = response.data.uploadURL;
      var options = {
        headers: {
          'Content-Type': fileType,
        }
      };
      axios.put(signedRequest,jsonFile,options)
      .then(
        result => { 
          setShowSpinner(false);
          alert("Thank you for your feedback!") 
        })
      .catch(error => {
        alert("ERROR " + JSON.stringify(error));
      })
    })
    .catch(error => {
      alert(JSON.stringify(error));
    })
  };

  useEffect(() => {
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <div className="top-section">
          <img src={foothillslogo} alt="Organization logo" />
        </div>
        <Form>
          <TextArea 
            placeholder='Your feedback..' 
            rows="5" 
            cols="40"
            onChange={(e) => setTextInput(e.target.value)} />
        </Form>
        <p></p>
        <Button icon  size='massive' onClick={handleSubmit}>
          Submit
        </Button>
        {showSpinner && <RotatingSquare color="#d5d4d4" />}
        <p></p>
        <Link to={voiceInputPage} style={{ color: 'white', textDecoration: 'none' }}>
          Switch to voice feedback
       </Link>
      </header>
    </div>
  );
}

export default TextInput;