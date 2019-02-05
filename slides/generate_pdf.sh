#!/bin/bash
#npm start&
#sleep $5
`npm bin`/decktape automatic http://localhost:8000/ "digital_audio.pdf" -s 1920x1080
#kill $!