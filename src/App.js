import React, { useState, useEffect } from 'react';
import './App.css';
import axios from "axios";
import { Link } from 'react-router-dom';
import MicRecorder from 'mic-recorder-to-mp3';
import { Button, Icon } from 'semantic-ui-react';
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/js/all.js';
import { RotatingSquare } from  'react-loader-spinner'
import { useNavigate } from "react-router-dom";
import foothillslogo from './images/foothillslogowhite.svg';

const Mp3Recorder = new MicRecorder({ bitRate: 128 });

const App = () => {

  const [isRecording, setIsRecording] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [isUploadable, setIsUploadable] = useState(false);
  const [isBlocked, setIsBlocked] = useState(false);
  const [showSpinner, setShowSpinner] = useState(false);
  const [file, setFile] = useState('');
  const queryParams = new URLSearchParams(window.location.search);
  const queryString = queryParams.get("qs"); 
  const textInputPage = `/TextInput/?qs=${queryString}`;
  const navigate = useNavigate();

  const handleMicClick = () => {
    if (isRecording) {
      setIsRecording(false);
      setIsFinished(true);
      // Stop recording and start processing
      stop();
      }
    else {
      setIsRecording(true);
      // Start recording
      start();
    }
  };
  
  const start = () => {
    if (isBlocked) {
      console.log('Microphone Permission Denied');
    } else {
      Mp3Recorder
        .start()
        .then(() => {
          setIsRecording(true);
        }).catch((e) => console.error(e));
    }
  };

  const stop = () => {
    Mp3Recorder
      .stop()
      .getMp3()
      .then(([buffer, blob]) => {
        let d = new Date();
        setFile(new File([blob],d.valueOf().toString(),{ type:"application/octet-stream" }));
        setIsRecording(false);
        setIsUploadable(true);
      }).catch((e) => console.log(e));
  };
  
  const generateRandomNumber = () => {
    const min = 10000000;
    const max = 99999999;
    const randomNumber = Math.floor(Math.random() * (max - min + 1)) + min;
    return randomNumber;
  }
  
  const handleSubmit = () => {
    // Form validation
    if (!isUploadable) {
      alert('Please finish recording feedback first!');
      return;
    }
    setShowSpinner(true);
    const fileName = generateRandomNumber();
    const fileType = file.type;
    const url = "https://mvqwikiek9.execute-api.us-east-1.amazonaws.com/prod?"
    const signUrl = url.concat("qs="+queryString+"&file_name="+fileName+"&upload_dir=audio");    
    axios.get(signUrl)
    .then(response => {
      var signedRequest = response.data.uploadURL;
      var options = {
        headers: {
          'Content-Type': fileType,
        }
      };
      axios.put(signedRequest,file,options)
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

  const goToTextInput = () => {
      navigate(textInputPage);
  }

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(() => {
        console.log('Microphone Permission Granted');
        setIsBlocked(false);
      })
      .catch((error) => {
        console.error('Error accessing microphone:', error);
        setIsBlocked(true);
        goToTextInput();
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <div className="top-section">
          <img src={foothillslogo} alt="Organization logo" />
        </div>
        <button 
          className={`mic-button ${isRecording ? 'recording' : (isFinished ? 'finished' : '')}`} 
          onClick={handleMicClick}>
          <i className="fas fa-microphone fa-5x"></i>
        </button>
        <p></p>
        <Button icon  size='massive' onClick={handleSubmit}>
          Submit
        </Button>
        {showSpinner && <RotatingSquare color="#d5d4d4" />}
        <p></p>
        <Link to={textInputPage} style={{ color: 'white', textDecoration: 'none' }}>
          Switch to text input
       </Link>
      </header>
    </div>
  );
}

export default App;