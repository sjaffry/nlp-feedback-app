import React, { useState, useEffect } from 'react';

function AudioRecorder() {
  const [recorder, setRecorder] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);

  useEffect(() => {
    // Check if the MediaRecorder API is supported by the browser
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.log('The MediaRecorder API is not supported by your browser.');
      return;
    }

    // Request access to the user's microphone
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then(stream => {
        // Create a new MediaRecorder instance
        const mediaRecorder = new MediaRecorder(stream);
        setRecorder(mediaRecorder);

        // Set up an event listener to handle the dataavailable event
        mediaRecorder.ondataavailable = event => {
          // The audio data is contained in the event's data property
          setAudioBlob(event.data);
        };
      })
      .catch(err => {
        // Handle error
        console.log(err);
      });
  }, []);

  const startRecording = () => {
    if (recorder) {
      recorder.start();
    }
  };

  const stopRecording = () => {
    if (recorder) {
      recorder.stop();
    }
  };

  return (
    <>
      <button onClick={startRecording}>Start recording</button>
      <button onClick={stopRecording}>Stop recording</button>
      {audioBlob ? <audio src={URL.createObjectURL(audioBlob)} controls /> : null}
    </>
  );
}