import os
from dotenv import load_dotenv

load_dotenv()

def parse_list_var(value):
    return [int(val,16) for val in value.split(",")]

POST_MAIN_FADER = parse_list_var(os.getenv("Main_Post_Fix_Fader"))
POST_SWITCH = parse_list_var(os.getenv("Main_Post_Fix_Switch"))
PRE_MAIN = parse_list_var(os.getenv("Main_Pre_Fix"))
POST_EQ_SWITCH = parse_list_var(os.getenv("EQ_Post_Switch"))
POST_NAME = parse_list_var(os.getenv("Fader_Post_Name"))
POST_LINK = parse_list_var(os.getenv("Fader_Post_link"))
PRE_PREAMP = parse_list_var(os.getenv("Preamp_Pre"))
POST_PREAMP = parse_list_var(os.getenv("Preamp_Post"))
DCA_FADER_POST = parse_list_var(os.getenv("Dca_Fader_Post"))
DCA_SWITCH_POST = parse_list_var(os.getenv("Dca_Switch_Post"))