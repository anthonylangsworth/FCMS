import sys
import requests
import os
try:
    # Python 2
    import Tkinter as tk
except ModuleNotFoundError:
    # Python 3
    import tkinter as tk

import myNotebook as nb
from config import config, appname
from ttkHyperlinkLabel import HyperlinkLabel
import logging

this = sys.modules[__name__]
this.plugin_name = "FCMS"
this.plugin_url = "https://fleetcarrier.space/"
this.apikey_url = "https://fleetcarrier.space/my_carrier"
this.version_info = (0, 2, 0)
this.version = ".".join(map(str, this.version_info))
this.api_url = "https://fleetcarrier.space/api"

# A Logger is used per 'found' plugin to make it easy to include the plugin's
# folder name in the logging output format.
# NB: plugin_name here *must* be the plugin's folder name as per the preceding
#     code, else the logger won't be properly set up.
logger = logging.getLogger(f'{appname}.{os.path.basename(os.path.dirname(__file__))}')

# If the Logger has handlers then it was already set up by the core code, else
# it needs setting up here.
if not logger.hasHandlers():
    level = logging.INFO  # So logger.info(...) is equivalent to print()

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)

def plugin_start(plugin_dir: str):
    # Migrate from single setting
    if not config.get("fcms_cmdrs"):
        if config.get("FCMSEmail"):
            # first commander will get the old settings
            config.set("fcms_emails", [config.get("FCMSEmail") or ""])
            config.set("fcms_apikeys", [config.get("FCMSKey") or ""])
        config.delete("FCMSEmail")
        config.delete("FCMSKey")
    return this.plugin_name


def plugin_start3(plugin_dir: str):
    return plugin_start(plugin_dir)


def plugin_app(parent: nb.Notebook):
    pass


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool):

    PADX = 10
    PADY = 2

    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    HyperlinkLabel(
        frame, text="Fleet Carrier Management System", background=nb.Label().cget("background"),
        url=this.plugin_url, underline=True
    ).grid(row=8, padx=PADX, sticky=tk.W)
    nb.Label(frame, text="Version: %s" % this.version).grid(row=8, column=1, padx=PADX, sticky=tk.E)

    nb.Label(frame).grid(sticky=tk.W)   # spacer

    this.cred_frame = nb.Frame(frame)   # credentials frame
    this.cred_frame.grid(columnspan=3, sticky=tk.EW)
    this.cred_frame.columnconfigure(1, weight=1)

    HyperlinkLabel(
        this.cred_frame, text="FCMS credentials", background=nb.Label().cget("background"),
        url=this.apikey_url, underline=True
    ).grid(row=1, columnspan=3, padx=PADX, sticky=tk.W)

    nb.Label(this.cred_frame, text=_("Cmdr")).grid(row=10, padx=PADX, sticky=tk.W)
    this.cmdr_text = nb.Label(this.cred_frame)
    this.cmdr_text.grid(row=10, column=1, columnspan=2, padx=PADX, pady=PADY, sticky=tk.W)

    this.add_cmdr_prefix = nb.Checkbutton(this.cred_frame, text="Add CMDR Prefix", command=add_cmdr_prefix_changed)
    this.add_cmdr_prefix.grid(row=10, column=2, padx=PADX, pady=PADY, sticky=tk.W)
    
    nb.Label(this.cred_frame, text="Email").grid(row=11, padx=PADX, sticky=tk.W)
    this.email = nb.Entry(this.cred_frame)
    this.email.grid(row=11, column=1, columnspan=2, padx=PADX, pady=PADY, sticky=tk.EW)

    nb.Label(this.cred_frame, text="API Key").grid(row=12, padx=PADX, sticky=tk.W)
    this.apikey = nb.Entry(this.cred_frame)
    this.apikey.grid(row=12, column=1, columnspan=2, padx=PADX, pady=PADY, sticky=tk.EW)

    prefs_cmdr_changed(cmdr, is_beta)

    return frame

def add_cmdr_prefix_changed():
    logger.info("add_cmdr_prefix_changed called")
    # this.cmdr_text["text"] = get_cmdr_text(cmdr, this.add_cmdr_prefix.value)

def set_state_frame_childs(frame, state):
    for child in frame.winfo_children():
        if child.winfo_class() in ("TFrame", "Frame", "Labelframe"):
            set_state_frame_childs(child, state)
        else:
            child["state"] = state


def credentials(cmdr):
    # Credentials for cmdr
    if cmdr:
        cmdrs = config.get("fcms_cmdrs")
        if not cmdrs:
            # Migrate from single setting, first commander gets the old settings
            cmdrs = [cmdr]
            config.set("fcms_cmdrs", cmdrs)
        emails = config.get("fcms_emails")
        apikeys = config.get("fcms_apikeys")
        addCmdrPrefixValue = config.get("fcms_addCMDRPrefix") or False
        if cmdr in cmdrs and emails and apikeys:
            idx = cmdrs.index(cmdr)
            logger.info(f"Loaded CMDR '{cmdr}' at index {idx} with email '{emails[idx]}', add prefix '{addCmdrPrefixValue}'")
            return (emails[idx], apikeys[idx], addCmdrPrefixValue)
    return None


def prefs_cmdr_changed(cmdr, is_beta):
    set_state_frame_childs(this.cred_frame, tk.NORMAL)
    this.email.delete(0, tk.END)
    this.apikey.delete(0, tk.END)
    if cmdr:
        cred = credentials(cmdr)
        this.cmdr_text["text"] = get_cmdr_text(cmdr, cred[2]) + (is_beta and " [Beta]" or "")
        if cred:
            this.email.insert(0, cred[0])
            this.apikey.insert(0, cred[1])
            this.add_cmdr_prefix.value = cred[2]
    else:
        this.cmdr_text["text"] = _("None")

    if not cmdr or is_beta:
        set_state_frame_childs(this.cred_frame, tk.DISABLED)


def prefs_changed(cmdr, is_beta):
    if cmdr and not is_beta:
        cmdrs = config.get("fcms_cmdrs")
        emails = config.get("fcms_emails") or []
        apikeys = config.get("fcms_apikeys") or []
        if cmdr in cmdrs:
            idx = cmdrs.index(cmdr)
            emails.extend([""] * (1 + idx - len(emails)))
            emails[idx] = this.email.get().strip()
            apikeys.extend([""] * (1 + idx - len(apikeys)))
            apikeys[idx] = this.apikey.get().strip()
        else:
            config.set("fcms_cmdrs", cmdrs + [cmdr])
            emails.append(this.email.get().strip())
            apikeys.append(this.apikey.get().strip())
        config.set("fcms_emails", emails)
        config.set("fcms_apikeys", apikeys)
        config.set("fcms_addCMDRPrefix", this.add_cmdr_prefix_value)


# See https://github.com/FuelRats/FCMS/blob/master/FCMS/views/api.py for server side of call.
# See https://www.w3schools.com/python/ref_requests_response.asp for response help

def journal_entry(cmdr, is_beta, system, station, entry, state):
    if entry["event"] in ["CarrierJumpRequest", "CarrierJumpCancelled"] and not is_beta:
        cred = credentials(cmdr)
        if cred:
            this.status["text"] = "Sending %s..." % entry["event"][11:]
            post = {
                "cmdr": get_cmdr_text(cmdr, cred[2]),
                "system": system,
                "station": station,
                "data": entry,
                "is_beta": is_beta,
                "user": cred[0],
                "key": cred[1],
            }
            response = requests.post(this.api_url, json=post)
            if response.status_code == 200:
                this.status["text"] = "Success"
            else:
                this.status["text"] = "Failed: " + str(response.status_code) + " (" + response.text + ")"
        else:
            this.status["text"] = "No credentials"
    elif entry["event"] in ("LoadGame", "NewCommander") and not credentials(cmdr):
        this.status["text"] = "No credentials"
    elif entry["event"] == "Shutdown" or (
         entry["event"] == "Music" and entry["MusicTrack"] in ("MainMenu", "CQC", "CQCMenu")
    ):
        this.status["text"] = "v%s - Ready" % this.version

def get_cmdr_text(cmdr: str, addCMDRPrefix: bool):
  return cmdr if not addCMDRPrefix else "CMDR " + cmdr
  