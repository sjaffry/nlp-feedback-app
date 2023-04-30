import React from 'react';
import './App.css';
import axios from "axios";
import MicRecorder from 'mic-recorder-to-mp3';
import { Button, Icon } from 'semantic-ui-react';
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/js/all.js';
import { RotatingSquare } from  'react-loader-spinner'

const Mp3Recorder = new MicRecorder({ bitRate: 128 });
let file;
//<RotatingSquare 
//    height="500"
//    width="500"
//    color="#ffffff"
//    ariaLabel="rotating-square-loading"
//    strokeWidth="4"
//    wrapperStyle={{}}
 //   wrapperClass=""
//    visible={true}/>


class App extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      isRecording: false,
      isUploadable: false,
      isBlocked: false,
      showSpinner: false,
    };
  };

  handleMicClick = () => {
    if (this.state.isRecording) {
      this.setState({ isRecording: false });
      // Start processing the recording
      this.stop();
      }
    else if (!this.state.isRecording) {
      this.setState({ isRecording: true });
      // Start recording
      this.start();
    }
    else {}
  };
  
  start = () => {
    if (this.state.isBlocked) {
      console.log('Permission Denied');
    } else {
      Mp3Recorder
        .start()
        .then(() => {
          this.setState({ isRecording: true });
        }).catch((e) => console.error(e));
    }
  };

  stop = () => {
    Mp3Recorder
      .stop()
      .getMp3()
      .then(([buffer, blob]) => {
        const blobURL = URL.createObjectURL(blob);
        let d = new Date();
        file = new File([blob],d.valueOf().toString(),{ type:"application/octet-stream" });
        this.setState({ blobURL, isRecording: false, isUploadable: true });
        this.setState({ blob, file });
      }).catch((e) => console.log(e));
  };
  
  handleAudioFile = () => {
    const queryParams = new URLSearchParams(window.location.search);
    const business_name = queryParams.get("business_name");
    const email = queryParams.get("email");
    const fileType = file.type;
    const url = "https://mvqwikiek9.execute-api.us-east-1.amazonaws.com/prod?"
    const signUrl = url.concat("business_name="+business_name+"&email="+email);
    axios.get(signUrl)
    .then(response => {
      var signedRequest = response.data.uploadURL;
      var options = {
        headers: {
          'Content-Type': fileType,
        }
      };
      this.setState({ showSpinner: true });
      axios.put(signedRequest,file,options)
      .then(
        result => { 
          this.setState({ showSpinner: false });
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

  componentDidMount = () => {
    navigator.mediaDevices.getUserMedia({ audio: true },
      () => {
        console.log('Permission Granted');
        this.setState({ isBlocked: false });
      },
      () => {
        console.log('Permission Denied');
        this.setState({ isBlocked: true })
      },
    );
  };

  render = () => {
    return (
      <div className="App">
        <header className="App-header">
          <button 
            className={`mic-button ${this.state.isRecording ? 'recording' : ''}`} 
            onClick={this.handleMicClick}>
            <i className="fas fa-microphone fa-5x"></i>
          </button>
          <p></p>
          <audio src={this.state.blobURL} controls="controls"/>
          <p></p>
          <Button icon labelPosition='left' onClick={this.handleAudioFile} disabled={!this.state.isUploadable}>
            <Icon name='upload' />
            Upload
          </Button>
          {this.state.showSpinner && <RotatingSquare color="#d5d4d4" />}
        </header>
      </div>
    );
  };
};

export default App;