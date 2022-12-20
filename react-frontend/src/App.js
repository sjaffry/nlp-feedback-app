import React from 'react';
import './App.css';
import MicRecorder from 'mic-recorder-to-mp3';
import fileUploader from './aws-s3'

const Mp3Recorder = new MicRecorder({ bitRate: 128 });

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
        const file = new File([blob],d.valueOf().toString(),{ type:"audio/wav" });
        this.setState({ blobURL, isRecording: false, isUploadable: true });
        this.setState({ blob, file });
      }).catch((e) => console.log(e));
  };

  handleAudioFile = () => {
    const file = this.state.file;
    const fileName = file.name.concat('.mp3');
    const fileType = file.type;
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
          {this.state.blobURL}
          </p>
          <audio src={this.state.blobURL} controls="controls" />
        </header>
      </div>
    );
  }
}
//          <button onClick={this.handleaudiofile(fileBlob={this.state.blob})} disabled={this.state.isRecording}>Submit</button>
export default App;