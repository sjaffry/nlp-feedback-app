import React from 'react';
import './App.css';
import axios from "axios";
import MicRecorder from 'mic-recorder-to-mp3';
import logo from "./logo.svg";
//import "@aws-amplify/ui-react/styles.css";

const Mp3Recorder = new MicRecorder({ bitRate: 128 });
let file;

class App extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      isRecording: false,
      isUploadable: false,
      blobURL: '',
      isBlocked: false,
    };
  }

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

  handleAudioFile(){
    const fileType = file.type;
    const url = 'https://mvqwikiek9.execute-api.us-east-1.amazonaws.com/prod';
    axios.get(url)
    .then(response => {
      var signedRequest = response.data.uploadURL;
      var options = {
        headers: {
          'Content-Type': fileType,
        }
      };
      axios.put(signedRequest,file,options)
      .then(result => { alert("audio uploaded") })
      .catch(error => {
        alert("ERROR " + JSON.stringify(error));
      })
    })
    .catch(error => {
      alert(JSON.stringify(error));
    })
    };

  componentDidMount() {
    navigator.getUserMedia({ audio: true },
      () => {
        console.log('Permission Granted');
        this.setState({ isBlocked: false });
      },
      () => {
        console.log('Permission Denied');
        this.setState({ isBlocked: true })
      },
    );
  }

  render(){
    return (
      <div className="App">
        <header className="App-header">
          <button onClick={this.start} disabled={this.state.isRecording}>Record</button>
          <button onClick={this.stop} disabled={!this.state.isRecording}>Stop</button>
          <button onClick={this.handleAudioFile} disabled={!this.state.isUploadable}>Upload</button>
          <p>
          </p>
          <audio src={this.state.blobURL} controls="controls" />
        </header>
      </div>
    );
  }
}

export default App;