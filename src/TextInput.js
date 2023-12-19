import React, { useState, useEffect } from 'react';
import './App.css';
import axios from "axios";
import { Button, TextArea, Form } from 'semantic-ui-react';
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/js/all.js';
import { RotatingSquare } from  'react-loader-spinner'


const TextInput = () => {
  const [showSpinner, setShowSpinner] = useState(false);
  const [textInput, setTextInput] = useState('');
  
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

    // Create a JSON file from the text input in the same format as the audio transcription job for code reusability downstream
    const jsonObject = { "results": { "transcripts": [ { "transcript": textInput } ] } };
    const jsonBlob = new Blob([JSON.stringify(jsonObject)], { type: 'application/json' });
    const jsonFile = new File([jsonBlob], 'feedback.json');
    const queryParams = new URLSearchParams(window.location.search);
    const business_name = queryParams.get("business_name");
    const file_name = `${generateRandomNumber()}.json`;
    const fileType = "binary/octet-stream";
    const url = "https://mvqwikiek9.execute-api.us-east-1.amazonaws.com/prod?"
    const signUrl = url.concat("business_name="+business_name+"&file_name="+file_name+"&upload_type=text");
    axios.get(signUrl)
    .then(response => {
      var signedRequest = response.data.uploadURL;
      var options = {
        headers: {
          'Content-Type': fileType,
        }
      };
      setShowSpinner(true);
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
      </header>
    </div>
  );
}

export default TextInput;