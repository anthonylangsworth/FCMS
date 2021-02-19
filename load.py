import sys
import requests
import logging
import tkinter as tk
import os
from typing import Tuple, Optional, Dict, Any
import json

import myNotebook as nb
from config import config, appname
from ttkHyperlinkLabel import HyperlinkLabel

this = sys.modules[__name__]
this.plugin_name = "FCMS"
this.plugin_url = "https://fleetcarrier.space/"
this.apikey_url = "https://fleetcarrier.space/my_carrier"
this.version_info = (0, 2, 0)
this.version = ".".join(map(str, this.version_info))
this.api_url = "https://fleetcarrier.space/api"

CONFIG_EMAIL = "fcms_emails"

# Setup logging
logger = logging.getLogger(f'{appname}.{os.path.basename(os.path.dirname(__file__))}')


def plugin_start(plugin_dir:str) -> str:
    # Migrate from single setting
    if not config.get("fcms_cmdrs"):
        if config.get("FCMSEmail"):
            # first commander will get the old settings
            config.set("fcms_emails", [config.get("FCMSEmail") or ""])
            config.set("fcms_apikeys", [config.get("FCMSKey") or ""])
            config.set("fcms_cmdr_names", [config.get("FCMSKey") or ""])
        config.delete("FCMSEmail")
        config.delete("FCMSKey")
    return this.plugin_name


def plugin_start3(plugin_dir:str) -> str:
    return plugin_start(plugin_dir)


def plugin_prefs(parent:nb.Notebook, cmdr: str, is_beta:bool) -> Optional[tk.Frame]:

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
    this.cred_frame.grid(columnspan=2, sticky=tk.EW)
    this.cred_frame.columnconfigure(1, weight=1)

    HyperlinkLabel(
        this.cred_frame, text="FCMS credentials", background=nb.Label().cget("background"),
        url=this.apikey_url, underline=True
    ).grid(row=1, columnspan=2, padx=PADX, sticky=tk.W)

    nb.Label(this.cred_frame, text=_("Cmdr")).grid(row=10, padx=PADX, sticky=tk.W)
    this.cmdr_text = nb.Entry(this.cred_frame)
    this.cmdr_text.grid(row=10, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

    nb.Label(this.cred_frame, text=_("Email")).grid(row=11, padx=PADX, sticky=tk.W)
    this.email = nb.Entry(this.cred_frame)
    this.email.grid(row=11, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

    nb.Label(this.cred_frame, text=_("API Key")).grid(row=12, padx=PADX, sticky=tk.W)
    this.apikey = nb.Entry(this.cred_frame)
    this.apikey.grid(row=12, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

    prefs_cmdr_changed(cmdr, is_beta)

    return frame


def set_state_frame_childs(frame:tk.Frame, state):
    for child in frame.winfo_children():
        if child.winfo_class() in ("TFrame", "Frame", "Labelframe"):
            set_state_frame_childs(child, state)
        else:
            child["state"] = state


def get_credentials(cmdr:str) -> Tuple[str, str, str]:
    # Credentials for cmdr
    if cmdr:
        cmdrs = config.get("fcms_cmdrs")
        if not cmdrs:
            # Migrate from single setting, first commander gets the old settings
            cmdrs = [cmdr]
            config.set("fcms_cmdrs", cmdrs)
        if not cmdr in cmdrs:
            cmdrs.append(cmdr)
        emails = config.get("fcms_emails") or [""] * len(cmdrs)
        apikeys = config.get("fcms_apikeys") or [""] * len(cmdrs)
        cmdr_names = config.get("fcms_cmdr_names") or [""] * len(emails)
        if cmdr in cmdrs and emails and apikeys:
            idx = cmdrs.index(cmdr)
            if not cmdr_names[idx]:
                cmdr_names[idx] = cmdr
            return (cmdr_names[idx], emails[idx], apikeys[idx])
    return None


def prefs_cmdr_changed(cmdr:str, is_beta:bool) -> None:
    set_state_frame_childs(this.cred_frame, tk.NORMAL)
    this.cmdr_text.delete(0, tk.END)
    this.email.delete(0, tk.END)
    this.apikey.delete(0, tk.END)
    if cmdr:
        cred = get_credentials(cmdr)
        if cred:
            this.cmdr_text.insert(0, cred[0])
            this.email.insert(0, cred[1])
            this.apikey.insert(0, cred[2])
    else:
        this.cmdr_text.insert(0, _("None"))

    if not cmdr or is_beta:
        set_state_frame_childs(this.cred_frame, tk.DISABLED)

# Preferences are saved in the registry at "HKEY_CURRENT_USER\SOFTWARE\Marginal\EDMarketConnector"

def prefs_changed(cmdr:str, is_beta: bool) -> None:
    if cmdr and not is_beta:
        cmdrs = config.get("fcms_cmdrs")
        emails = config.get("fcms_emails") or [""] * len(cmdrs)
        apikeys = config.get("fcms_apikeys") or [""] * len(cmdrs)
        cmdr_names = config.get("fcms_cmdr_names") or [""] * len(cmdrs)
        if cmdr in cmdrs:
            idx = cmdrs.index(cmdr)
            emails[idx] = this.email.get().strip()
            apikeys[idx] = this.apikey.get().strip()
            cmdr_names[idx] = this.cmdr_text.get().strip()
        else:
            config.set("fcms_cmdrs", cmdrs + [cmdr])
            emails.append(this.email.get().strip())
            apikeys.append(this.apikey.get().strip())
            cmdr_names.append(this.cmdr_text.get().strip())
        config.set("fcms_emails", emails)
        config.set("fcms_apikeys", apikeys)
        config.set("fcms_cmdr_names", cmdr_names)


# See https://github.com/FuelRats/FCMS/blob/master/FCMS/views/api.py for server side of call.
# See https://www.w3schools.com/python/ref_requests_response.asp for response help

def journal_entry(cmdr:str, is_beta:bool, system:Optional[str], station:Optional[str], entry:Dict[str, Any], stateentry:Dict[str, Any]) -> Optional[str]:
    result = None
    if entry["event"] in ["CarrierJumpRequest", "CarrierJumpCancelled"] and not is_beta:
        cred = get_credentials(cmdr)
        if cred:
            post = {
                "cmdr": cred[0],
                "system": system,
                "station": station,
                "data": entry,
                "is_beta": is_beta,
                "user": cred[1],
                "key": cred[2],
            }
            response = requests.post(this.api_url, json=post)
            if response.status_code == 200:
                logger.info(f"{ entry['event']} event posted to FCMS")
            else:
                logger.info(f"{ entry['event']} event posting to FCMS failed: { str(response.status_code) }")
                result = f"{this.plugin_name}: Error updating FCMS. Check CMDR name."
        else:
            logger.error("No credentials")
            result = f"{this.plugin_name}: Add credentials."
    return result
