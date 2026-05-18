import asyncio
import math
import threading
import mido
from dotenv import load_dotenv
import os
from enum import Enum
import time

load_dotenv()
Manufacturer_ID = int(os.getenv("MANUFACTURER_ID"), 0)
Device_ID = int(os.getenv("DEVICE_ID"), 0)
Model_ID = [int(val,0) for val in os.getenv("MODEL_ID").split(",")]
Command_ID_Set = int(os.getenv("Command_ID_Data_Set"), 0)
Command_ID_Request = int(os.getenv("Command_ID_Data_Request"), 0)
midi_name = os.getenv("Midi_Name")

fader_post = [int(val,0) for val in os.getenv("Main_Post_Fix_Fader").split(",")]
switch_post = [int(val,0) for val in os.getenv("Main_Post_Fix_Switch").split(",")]
preMain = os.getenv("Main_Pre_Fix")

# dca
preDca = [int(os.getenv("Pre_Dca"), 0)]
dca_fader_post = [int(val,0) for val in os.getenv("Dca_Fader_Post").split(",")]
dca_switch_post = [int(val,0) for val in os.getenv("Dca_Switch_Post").split(",")]


header = [int(Manufacturer_ID), int(Device_ID)] + [int(a) for a in Model_ID] 

# eq 
eq_low_gain = [int(val,0) for val in os.getenv("EQ_Post_Lo_Gain").split(",")]
eq_low_freq = [int(val,0) for val in os.getenv("EQ_Post_Lo_Freq").split(",")]

eq_low_mid_gain = [int(val,0) for val in os.getenv("EQ_Post_Lo_Mid_Gain").split(",")]
eq_low_mid_freq = [int(val,0) for val in os.getenv("EQ_Post_Lo_Mid_Freq").split(",")]
eq_low_mid_q = [int(val,0) for val in os.getenv("EQ_Post_Lo_Mid_Q").split(",")]

eq_mid_hi_gain = [int(val,0) for val in os.getenv("EQ_Post_Mid_HI_Gain").split(",")]
eq_mid_hi_freq = [int(val,0) for val in os.getenv("EQ_Post_Mid_HI_Freq").split(",")]
eq_mid_hi_q = [int(val,0) for val in os.getenv("EQ_Post_Mid_HI_Q").split(",")]

eq_high_gain = [int(val,0) for val in os.getenv("EQ_Post_Hi_Gain").split(",")]
eq_high_freq = [int(val,0) for val in os.getenv("EQ_Post_Hi_Freq").split(",")]

class MidiController: 
    def __init__(self):
        for port in mido.get_output_names():
            if midi_name in port:
                self.ped = port
                break

        if not self.ped:
            raise Exception("Nessuna porta midi trovata.\nConnetti il pc al mixer e riprova.")

    def send_command(self, address, data, token_user):
        sysex_msg = build_sysex(address, Command_ID_Set, data)

        msg = mido.Message('sysex', data=sysex_msg)

        with mido.open_output(self.ped) as outport:
            outport.send(msg)

        try:
            multiplexer = get_midi_multiplexer()
            multiplexer._dispatch_send(msg, token_user) 
        except Exception as e:
            print(f"[DEBUG] Errore durante la dispatch_sysex del messaggio MIDI: {e}")
    
    @staticmethod
    def convert_fader_to_hex(value):
        if value == 0:
            return [0x78, 0x76]
        if value >=75:
            newvalue = ((value-75)/25)*100 
            return [0x00, int(newvalue)]
        
        #conversione in db
        decibel = 0
        if value >= 50:
            decibel = (((value-50)*10)/25) -10

        if value < 50 and value >= 20:
            decibel = value - 60

        if value < 20 and value >= 10:
            decibel = ((value-10)*2) -60

        if value < 10 and value >= 1:
            decibel = ((value-1)*(29.6/9))-89.6
        


        decibel += 0.1
        decibel *= -10
        decibel = int(decibel)
        first_value = 127 - int((decibel / 128))
        second_value = 127 - (decibel % 128)

        return [first_value, second_value]

    # @staticmethod
    # def convert_fader_to_hex(value):
    #     if value == 0:
    #         return [0x78, 0x76]
            
    #     BASE = 120 * 128 + 125      
    #     OFFSET = value - 1               

    #     total = (BASE + OFFSET) % 16384

    #     a = total // 128
    #     b = total % 128
    #     return [a, b]

    @staticmethod
    def convert_switch_to_hex(switch):
        return [0x00] if switch else [0x01] 

    def request_value(self, address):
        data = [0x00, 0x00, 0x00, 0x06]
        sysex_msg = build_sysex(address, Command_ID_Request, data)

        msg = mido.Message('sysex', data=sysex_msg)

        with mido.open_output(self.ped) as outport:
            outport.send(msg)

    def load_scene(self, scene_number):
        channel, program_number = MidiController.convert_fader_to_hexScene(scene_number=scene_number)
        msg = mido.Message('program_change', program=program_number, channel=channel)
        with mido.open_output(self.ped) as outport:
            outport.send(msg)

    @staticmethod
    def convert_fader_to_hexScene(scene_number):
        if not 0 <= scene_number <= 299:
            return None

        if scene_number <= 127:
            channel = 0x0  
            program_number = scene_number
        elif scene_number <= 255:
            channel = 0x1  
            program_number = scene_number - 128
        else:
            channel = 0x2  
            program_number = scene_number - 256


        return channel, program_number

    @staticmethod
    def convert_freq_to_hex(freq):
        if 20 <= freq <= 20000:
            b1 = (freq >> 14) & 0x7F  
            b2 = (freq >> 7) & 0x7F
            b3 = freq & 0x7F   
            return [b1, b2, b3]
        
        return None

    @staticmethod
    def convert_q_to_hex(q):
        if 0.36 <= q <= 16:
            q *= 100
            first_value = int(q / 128)
            second_value = int(q % 128)

            return [first_value, second_value]
        return None

    @staticmethod
    def convert_gain_to_hex(gain):
        if -15 <= gain <= 15:
            if gain >= 0:
                gain *= 10 
                gain = int(gain)
                first_value = int(gain / 128)
                second_value = gain % 128

                return [first_value, second_value]
            else:
                gain += 0.1
                gain *= -10
                gain = int(gain)
                first_value = 127 - int((gain / 128))
                second_value = 127 - (gain % 128)

                return [first_value, second_value]
        
        return None


def roland_checksum(address_bytes, data_bytes):
    total = sum(address_bytes) + sum(data_bytes)
    checksum = (128 - (total % 128)) % 128
    return checksum  

def build_sysex(address, command, data):
    checksum = roland_checksum(address, data)
    return header + [command] + address + data + [checksum]

   
class call_type(Enum):
    CHANNEL = "channel"
    SWITCH = "switch"
    Q = "Q"
    FREQ = "freq"
    GAIN = "gain"
    PREAMP = "preamp"
    NAME = "name"
    PATCH_CHANNEL = "patch_channel"

class MidiListener:
    def __init__(self, midi_addresses, calltype):
        self.midi_addresses = [tuple(addr) for addr in midi_addresses]
        self.received = {}
        self.lock = threading.Lock()
        self.running = True

        match calltype:
            case call_type.CHANNEL: 
                callfn = self.callback_channel
            case call_type.SWITCH:
                callfn = self.callback_switch
            case call_type.Q:
                callfn = self.callback_q
            case call_type.FREQ:
                callfn = self.callback_freq
            case call_type.GAIN:
                callfn = self.callback_gain
            case call_type.PREAMP:
                callfn = self.callback_preamp
            case call_type.NAME:
                callfn = self.callback_name
            case call_type.PATCH_CHANNEL:
                callfn = self.callback_patchbay_channel

        self.callback = callfn

        get_midi_multiplexer().register(self.callback)

    def callback_channel(self, msg, token=None):
        if not self.running:
            return
        if msg.type == 'sysex' and token==None:
            data = tuple(msg.data)
            key = data[6:10]
            with self.lock:
                if key in self.midi_addresses and key not in self.received:
                    self.received[key] = MidiListener.convert_hex_to_fader(data[10], data[11])

    def callback_switch(self, msg, token=None):
        if not self.running:
            return
        if msg.type == 'sysex' and token==None:
            data = tuple(msg.data)
            key = data[6:10]
            with self.lock:
                if key in self.midi_addresses and key not in self.received:
                    self.received[key] = MidiListener.convert_hex_to_switch(data[10])

    def callback_q(self, msg, token=None):
        if not self.running:
            return 
        if msg.type == 'sysex' and token==None:
            data = tuple(msg.data)
            key = data[6:10]
            with self.lock:
                if key in self.midi_addresses and key not in self.received:
                    self.received[key] = MidiListener.convert_hex_to_Q(data[10], data[11])

    def callback_freq(self, msg, token=None):
        if not self.running:
            return 
        if msg.type == 'sysex' and token==None:
            data = tuple(msg.data)
            key = data[6:10]
            with self.lock:
                if key in self.midi_addresses and key not in self.received:
                    self.received[key] = MidiListener.convert_hex_to_freq(data[10], data[11], data[12])

    def callback_gain(self, msg, token=None):
        if not self.running:
            return 
        if msg.type == 'sysex' and token==None:
            data = tuple(msg.data)
            key = data[6:10]
            with self.lock:
                if key in self.midi_addresses and key not in self.received:
                    self.received[key] = MidiListener.convert_hex_to_gain(data[10], data[11])
                    
    def callback_preamp(self, msg, token=None):
        if not self.running:
            return
        if msg.type == 'sysex' and token==None:
            data = tuple(msg.data)
            key = data[6:10]
            with self.lock:
                if key in self.midi_addresses and key not in self.received:
                    self.received[key] = data[10]

    def callback_name(self, msg, token=None):
        if not self.running:
            return
        if msg.type == 'sysex' and token==None: 
            data = tuple(msg.data)
            key = data[6:10]
            with self.lock:
                if key in self.midi_addresses and key not in self.received:
                    str_hex = ''.join(f'{byte:02X}' for byte in data[10:16])
                    self.received[key] = MidiListener.convert_hex_to_str(str_hex)

    def callback_patchbay_channel(self, msg, token=None):
        if not self.running:
            return
        if msg.type == 'sysex' and token==None:
            data = tuple(msg.data)
            key = data[6:10]
            with self.lock:
                if key in self.midi_addresses and key not in self.received:
                    str_hex = ''.join(f'{byte:02X}' for byte in data[10:16])
                    self.received[key] = data[10]

    def stop(self):
        self.running = False
        get_midi_multiplexer().unregister(self.callback)

    def has_received_all(self):
        with self.lock:
            return len(self.received) == len(self.midi_addresses)
    
    def get_results(self):
        with self.lock:
            return dict(self.received)
        
    @staticmethod
    def convert_hex_to_fader(firstValue, secondValue):
        try:
            if firstValue == 0x00:
                value = (secondValue / 100) * 25 + 75
                return round(value)
            elif firstValue == 0x78:
                return 0
            elif firstValue == 0x79 or firstValue == 0x7A:
                norm = round(((secondValue/127) * 4) + 1)
                return norm if firstValue == 0x79 else norm + 4
            elif firstValue == 0x7B:
                norm = round((secondValue/127) * 6) 
                return norm + 9
            elif firstValue == 0x7C:
                norm = round((secondValue/127) * 6)
                return norm + 15
            elif firstValue == 0x7D:
                norm = round((secondValue/127) * 12)
                return norm + 22
            elif firstValue == 0x7E:
                norm = round((secondValue/127) * 12)
                return norm + 35
            elif firstValue == 0x7F:
                norm = round((secondValue/127) * 24)
                return norm + 48
            
            return 0
        except Exception as e:
            print(f"errore: {e}")

    # @staticmethod
    # def convert_hex_to_fader(a: int, b: int):
    #     if not (0 <= a <= 127 and 0 <= b <= 127):
    #         raise ValueError("a e b devono essere compresi tra 0 e 127")

    #     if (a, b) == (0x78, 0x76):
    #         return 0

    #     BASE = 120 * 128 + 125  
    #     MODULO = 128 * 128     

    #     total = a * 128 + b
    #     diff = (total - BASE) % MODULO

    #     n = diff + 1

    #     if not 1 <= n <= 1000:
    #         raise ValueError(f"La coppia ({a}, {b}) non è nella sequenza da 0 a 1000")

    #     return n
    
    @staticmethod
    def convert_hex_to_switch(value):
        return False if value == 0x01 else True

    @staticmethod
    def convert_hex_to_Q(first_value, second_value):
        if 0 <= first_value <= 12 and  0 <= second_value <= 127:
            q_times_100 = first_value * 128 + second_value
            q = q_times_100 / 100
            if q > 16:
                return 16
            if q < 0.36:
                return 0.36
            return q

    @staticmethod
    def convert_hex_to_freq(first_value, second_value, third_value):
        if 0 <= first_value <= 1 and 0 <= second_value <= 127 and 0 <= third_value <= 127:
            freq = (first_value << 14) | (second_value << 7) | third_value
            if freq < 20:
                return 20
            if freq > 20000:
                return 20000
            return freq

        return None
        
    @staticmethod
    def convert_hex_to_gain(first_value, second_value):
        if 0 <= second_value <= 127:
            if 0 <= first_value <=1:
                gain = first_value * 128 + second_value
                
                gain /= 10 
                
                if gain > 15:
                    return 15
                return gain
                
            if 126 <= first_value <= 127:
                high = 127 - first_value
                low = 127 - second_value
                int_gain = (high * 128) + low
                gain = int_gain / -10
                gain -= 0.1
                return gain
   
        return None

    @staticmethod
    def convert_hex_to_str(str_hex):
        return bytes.fromhex(str_hex).decode('ascii')

    @staticmethod
    def init_and_listen(listenAddresses, call_type):
        listen = MidiListener(listenAddresses, call_type)

        start = time.time()
   
        midiController = MidiController()

        for address in listenAddresses:
            midiController.request_value(address)

        while time.time() - start < 10:
            time.sleep(0.5)
            if listen.has_received_all():
                break

        listen.stop()

        return listen.get_results()

class MidiUserSync():
    def __init__(self, sendback, address, addressMain, token_user):
        self.loop = asyncio.get_event_loop()
        self.send_back = sendback
        self.post_address = address
        self.addressMain = addressMain
        self.token = token_user

        get_midi_multiplexer().register(self.listening)

    def stop(self):
        get_midi_multiplexer().unregister(self.listening)


    def listening(self, msg, token = None):
        if msg.type == 'sysex' and (token == None or token != self.token):
            data = tuple(msg.data)
            if data[:5] == tuple(header) and data[5] == Command_ID_Set:
                canale = f"0x{data[6]:02X}, 0x{data[7]:02X}"
                valore = 0
                if data[8:10] == tuple(self.post_address):
                    valore = MidiListener.convert_hex_to_fader(data[10], data[11])

                    asyncio.run_coroutine_threadsafe(
                        self.send_back(canale, valore),
                        self.loop
                    )
                elif data[6:10] == tuple(self.addressMain + fader_post):
                    canale = "main"
                    valore = MidiListener.convert_hex_to_fader(data[10], data[11])

                    asyncio.run_coroutine_threadsafe(
                        self.send_back(canale, valore),
                        self.loop
                    )

class MidiVideoSync():
    def __init__(self, sendback, address, addressMain, token_user):
        
        self.loop = asyncio.get_event_loop()
        self.send_back = sendback
        self.post_address = address
        self.addressMain = addressMain
        self.token = token_user

        get_midi_multiplexer().register(self.listening)

    def stop(self):
        get_midi_multiplexer().unregister(self.listening)


    def listening(self, msg, token = None):
        if msg.type == 'sysex' and (token == None or token != self.token):
            data = tuple(msg.data)

            if data[:5] == tuple(header) and data[5] == Command_ID_Set:
                canale = f"0x{data[6]:02X}, 0x{data[7]:02X}"
                
                typeCmd =""
                valore = 0
                
                if data[6:8] == tuple(self.addressMain):
                    canale = "main"

                    if data[8:10] == tuple(switch_post):
                        typeCmd = "switch"
                        valore = MidiListener.convert_hex_to_switch(data[10])
                    elif data[8:10] == tuple(fader_post):
                        valore = MidiListener.convert_hex_to_fader(data[10], data[11])
                        typeCmd = "fader"

                elif data[8:10] == tuple(self.post_address):
                    valore = MidiListener.convert_hex_to_fader(data[10], data[11])
                    typeCmd ="fader"

                if typeCmd != "":
                    asyncio.run_coroutine_threadsafe(
                        self.send_back(typeCmd, canale, valore),
                        self.loop
                    )

class MidiMixerSync():
    def __init__(self, send_back, token_user):
        self.loop =  asyncio.get_event_loop()
        self.send_back = send_back
        self.token = token_user

        get_midi_multiplexer().register(self.listening)

    def stop(self):
        get_midi_multiplexer().unregister(self.listening)


    def listening(self, msg, token = None):
        if msg.type == 'sysex' and (token== None or token != self.token):
            data = tuple(msg.data)

            if data[:5] == tuple(header) and data[5] == Command_ID_Set:
                canale = ""
                if(3 == data[6] ):
                    canale = f"0x{data[6]:02X}, 0x{data[7]:02X}"
                
                if f"0x{data[6]:02X}, 0x{data[7]:02X}" == preMain:
                    canale = "main"
                typeCmd =""
                valore = 0
                if data[8:10] == tuple(switch_post):
                    typeCmd = "switch"
                    valore = MidiListener.convert_hex_to_switch(data[10])
                elif data[8:10] == tuple(fader_post):
                    valore = MidiListener.convert_hex_to_fader(data[10], data[11])
                    typeCmd = "fader"

                if data[6] == preDca[0]:
                    canale = f"0x{data[6]:02X}, 0x{data[7]:02X}"
                    if data[8:10] == tuple(dca_fader_post):
                        valore = MidiListener.convert_hex_to_fader(data[10], data[11])
                        typeCmd = "fader"
                    elif data[8:10] == tuple(dca_switch_post):
                        typeCmd = "switch"
                        valore = MidiListener.convert_hex_to_switch(data[10])

                
                if typeCmd != "" and canale != "" :
                    asyncio.run_coroutine_threadsafe(
                        self.send_back(typeCmd, canale, valore),
                        self.loop
                    )

class MidiMultiplexer:
    def __init__(self):
        self.callbacks = []
        self.lock = threading.Lock()

        port_name = None
        for port in mido.get_input_names():
            if midi_name in port:
                port_name = port
                break      
        if not port_name:
            raise Exception("Nessuna porta MIDI trovata. Assicurati che il dispositivo sia connesso e riprova.")

        self.port = mido.open_input(port_name, callback=self._dispatch)

        
    def _dispatch_send(self, msg, token):
        with self.lock:
            for cb in self.callbacks:
                cb(msg, token)

    def _dispatch(self, msg):
        with self.lock:
            for cb in self.callbacks:
                cb(msg)
            
    def register(self, callback):
        with self.lock:
            self.callbacks.append(callback)

    def unregister(self, callback):
        with self.lock:
            self.callbacks.remove(callback)

    def close(self):
        self.port.close()

_multiplexer_instance = None

def get_midi_multiplexer():
    global _multiplexer_instance
    if _multiplexer_instance is None:
        _multiplexer_instance = MidiMultiplexer()
    return _multiplexer_instance

def get_eq_address_value(typeFreq, typeEQ, value):
    match typeFreq:
        case 0:
            match typeEQ:
                case "gain":
                    return eq_low_gain, MidiController.convert_gain_to_hex(value)
                case "freq":
                    return eq_low_freq, MidiController.convert_freq_to_hex(int(value))
        case 1:
            match typeEQ:
                case "gain":
                    return eq_low_mid_gain, MidiController.convert_gain_to_hex(value)
                case "freq":
                    return eq_low_mid_freq, MidiController.convert_freq_to_hex(int(value))
                case "q":
                    return eq_low_mid_q, MidiController.convert_q_to_hex(value)
        case 2:
            match typeEQ:
                case "gain":
                    return eq_mid_hi_gain, MidiController.convert_gain_to_hex(value)
                case "freq":
                    return eq_mid_hi_freq, MidiController.convert_freq_to_hex(int(value))
                case "q":
                    return eq_mid_hi_q, MidiController.convert_q_to_hex(value)
        case 3:
            match typeEQ:
                case "gain":
                    return eq_high_gain, MidiController.convert_gain_to_hex(value)
                case "freq":
                    return eq_high_freq, MidiController.convert_freq_to_hex(int(value))

def get_eq_channel(channel_address, typeEQ):
    channels = dict()
    
    if typeEQ == call_type.Q: 
        channels["eq_low_mid_q"] = channel_address + eq_low_mid_q
        channels["eq_mid_hi_q"] = channel_address + eq_mid_hi_q

    if typeEQ == call_type.FREQ: 
        channels["eq_low_freq"] = channel_address + eq_low_freq 
        channels["eq_low_mid_freq"] = channel_address + eq_low_mid_freq
        channels["eq_mid_hi_freq"] = channel_address + eq_mid_hi_freq
        channels["eq_high_freq"] = channel_address + eq_high_freq

    if typeEQ == call_type.GAIN:
        channels["eq_low_gain"] = channel_address + eq_low_gain 
        channels["eq_low_mid_gain"] = channel_address + eq_low_mid_gain
        channels["eq_mid_hi_gain"] = channel_address + eq_mid_hi_gain
        channels["eq_high_gain"] = channel_address + eq_high_gain 

    return channels

