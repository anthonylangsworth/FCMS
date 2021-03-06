import sys
import requests
import logging
import tkinter as tk
import os
from typing import Tuple, Optional, Dict, Any, Union

# Prevent linting errors with _() and, hopefully, enable better automaed unit testing in the future
try:
    import myNotebook as nb
    from config import config, appname
    from ttkHyperlinkLabel import HyperlinkLabel
except ImportError:
    from edmc_mocks import *

import fcms_web_services

this = sys.modules[__name__]
this.plugin_name = "FCMS"
this.plugin_url = "https://github.com/anthonylangsworth/FCMS"
this.apikey_url = "https://fleetcarrier.space/my_carrier"
this.version_info = (0, 10, 0)
this.version = ".".join(map(str, this.version_info))
this.api_url = "https://fleetcarrier.space/api"

CONFIG_CMDRS = "fcms_cmdrs"
CONFIG_EMAIL = "fcms_emails"
CONFIG_API_KEYS = "fcms_apikeys"
CONFIG_CMDR_NAMES = "fcms_cmdr_names"

# Setup logging
this.logger = logging.getLogger(f'{appname}.{os.path.basename(os.path.dirname(__file__))}')


def plugin_start3(plugin_dir: str) -> str:
    if not config.get_list(CONFIG_CMDRS):
        # Migrate from single setting
        if config.get_str("FCMSEmail"):
            # first commander will get the old settings
            # CONFIG_CMDR_NAMES set in get_credentials when CMDR name known
            config.set(CONFIG_EMAIL, [config.get_str("FCMSEmail") or ""])
            config.set(CONFIG_API_KEYS, [config.get_str("FCMSKey") or ""])
            config.delete("FCMSEmail")
            config.delete("FCMSKey")
    elif not config.get_list(CONFIG_CMDR_NAMES):
        # Default the FCMS CMDR names to in-game CMDR names
        config.set(CONFIG_CMDR_NAMES, config.get_list(CONFIG_CMDRS))

    return this.plugin_name


# Called by EDMC to show plug-in details on EDMC main window
def plugin_app(parent: tk.Frame) -> Union[tk.Widget, Tuple[tk.Widget, tk.Widget]]:
    REPO_OWNER = "anthonylangsworth"
    REPO = "FCMS"
    NEW_RELEASE_AVAILABLE = "New FCMS release available"
    BACKGROUND = tk.Label().cget("background")

    frame = None
    try:
        latest_release_url = fcms_web_services.get_newer_release(this.logger, REPO_OWNER, REPO, this.version_info)
        if latest_release_url:
            frame = tk.Frame(parent)
            HyperlinkLabel(
                frame, text=NEW_RELEASE_AVAILABLE, background=BACKGROUND, url=latest_release_url, underline=True
            ).grid(sticky=tk.EW)
    except Exception as e:
        this.logger.error(f"Error getting latest version from github: {e}")
    return frame


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:

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

    if not cmdr or is_beta:
        set_state_frame_childs(this.cred_frame, tk.DISABLED)

    return frame


def set_state_frame_childs(frame: tk.Frame, state):
    for child in frame.winfo_children():
        if child.winfo_class() in ("TFrame", "Frame", "Labelframe"):
            set_state_frame_childs(child, state)
        else:
            child["state"] = state


def get_credentials(cmdr: str) -> Optional[Tuple[str, str, str]]:
    """
    Load the settings for the given commander as a tuple containing the (1) FCMS name, (2) email address and (3) API key.
    Return None if there are no settings for that commander.
    """
    # Credentials for cmdr
    if cmdr:
        cmdrs = config.get_list(CONFIG_CMDRS)
        if not cmdrs:
            # Migrate from single setting, first commander gets the old settings
            cmdrs = [cmdr]
            config.set(CONFIG_CMDRS, cmdrs)
            config.set(CONFIG_CMDR_NAMES, cmdrs)
        emails = config.get_list(CONFIG_EMAIL)
        apikeys = config.get_list(CONFIG_API_KEYS)
        cmdr_names = config.get_list(CONFIG_CMDR_NAMES)
        if cmdr in cmdrs and emails and apikeys and cmdr_names:
            idx = cmdrs.index(cmdr)
            return (cmdr_names[idx], emails[idx], apikeys[idx])
    return None


# Preferences are saved in the registry at "HKEY_CURRENT_USER\SOFTWARE\Marginal\EDMarketConnector"

def prefs_changed(cmdr: str, is_beta: bool) -> None:
    if cmdr and not is_beta:
        cmdrs = config.get_list(CONFIG_CMDRS)
        cmdr_names = config.get_list(CONFIG_CMDR_NAMES) or [""] * len(cmdrs)
        emails = config.get_list(CONFIG_EMAIL) or [""] * len(cmdrs)
        apikeys = config.get_list(CONFIG_API_KEYS) or [""] * len(cmdrs)
        if cmdr in cmdrs:
            idx = cmdrs.index(cmdr)
            cmdr_names[idx] = this.cmdr_text.get().strip()
            emails[idx] = this.email.get().strip()
            apikeys[idx] = this.apikey.get().strip()
        else:
            config.set(CONFIG_CMDRS, cmdrs + [cmdr])
            cmdr_names.append(this.cmdr_text.get().strip())
            emails.append(this.email.get().strip())
            apikeys.append(this.apikey.get().strip())
        config.set(CONFIG_CMDR_NAMES, cmdr_names)
        config.set(CONFIG_EMAIL, emails)
        config.set(CONFIG_API_KEYS, apikeys)


# See https://github.com/FuelRats/FCMS/blob/master/FCMS/views/api.py for server side of call.
# See https://www.w3schools.com/python/ref_requests_response.asp for response help

def journal_entry(cmdr: str, is_beta: bool, system: Optional[str], station: Optional[str], entry: Dict[str, Any], stateentry: Dict[str, Any]) -> Optional[str]:
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
            with requests.post(this.api_url, json=post) as response:
                if response.status_code == 200:
                    this.logger.info(f"{ entry['event']} event posted to FCMS")
                else:
                    this.logger.info(f"{ entry['event']} event posting to FCMS failed: { str(response.status_code) }")
                    result = f"{this.plugin_name}: Error updating FCMS. Check CMDR name."
        else:
            this.logger.error("No credentials")
            result = f"{this.plugin_name}: Add credentials."
    return result
