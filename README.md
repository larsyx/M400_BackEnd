# M400_MIDI
Remote MIDI controller for the **Roland M-400 V-Mixer**.

---

## 🛠️ Setup Instructions

### 1. Create and activate a virtual environment

From the project root:

```bash
# Create the virtual environment
python -m venv venv

on Windows: .\venv\Scripts\activate
on macOs/Linux: source venv/bin/activate
```

### 2. install dependencies:
```bash
    pip install -r requirements.txt
```
### 3. create .env file on src directory

    #Midi setting
    Manufacturer_ID = 0x41
    Device_ID =
    Model_ID = 0x00, 0x00, 0x24
    Command_ID_Data_Set = 0x12
    Command_ID_Data_Request = 0x11
    Midi_Name = "RSS"

    #Main setting
    Main_Post_Fix_Fader = 0x00, 0x0E
    Main_Post_Fix_Switch = 0x00, 0x0C 
    Main_Pre_Fix = 0x06, 0x00

    #DCA setting
    Pre_Dca = 0x09
    Dca_Fader_Post = 0x00, 0x0A
    Dca_Switch_Post = 0x00, 0x08

    #Fader setting
    Fader_Post_Name = 0x00, 0x00
    Fader_Post_link = 0x00, 0x08

    #Preamp
    Preamp_Pre = 0x00
    Preamp_Post = 0x00, 0x01

    #EQ setting
    EQ_Post_Switch = 0x00, 0x50
    EQ_Post_Lo_Gain = 0x00, 0x53
    EQ_Post_Lo_Freq = 0x00, 0x55
    EQ_Post_Lo_Mid_Gain = 0x00, 0x58
    EQ_Post_Lo_Mid_Freq = 0x00, 0x5A
    EQ_Post_Lo_Mid_Q = 0x00, 0x5D
    EQ_Post_Mid_HI_Gain = 0x00, 0x5F
    EQ_Post_Mid_HI_Freq = 0x00, 0x61
    EQ_Post_Mid_HI_Q = 0x00, 0x64
    EQ_Post_Hi_Gain = 0x00, 0x66
    EQ_Post_Hi_Freq = 0x00, 0x68

    #Video Aux
    VIDEO_AUX_ID = 9

    #authentication setting
    AUTH_KEY = "your key"

    

### 4. Run the server
from src directory
```bash
    uvicorn app.main:app \
    --host 0.0.0.0 \
     --port 8000 \
     --app-dir . \
     --ssl-keyfile=PATH_TO_KEY.PEM \
     --ssl-certfile=PATH_TO_CERT.PEM
```