# This file downloads Factorio item image files from the official Factorio wiki
# (https://wiki.factorio.com/Category:Game_images). No Factorio images are distributed
# as part of this repository, and images should be used only for personal use as
# described in the Factorio terms of service (https://www.factorio.com/terms-of-service).
# Image files are downloaded once and placed in a folder called cache/ relative to the
# current working directory of the script.

import PIL
import os
import requests

# Official factorio wiki images URL
image_base_url = "https://wiki.factorio.com/images/"

def make_cache_folder_if_missing():
    if not os.path.exists("cache"):
        print("Creating non-existent cache/ folder")
        os.mkdir("cache")

def make_icon_path(item):
    return "cache/" + item + ".png"
        
def make_icon_download_url(item):
    """
    Most of the icon file names are derived from the item name
    (which is snake_case) by capitalising the first letter. The
    exceptions are stored in a dictionary
    """
    exceptions = {
        "power_armor_mk2": "Power_armor_MK2",
        "rail": "Straight_rail",
    }

    if item in exceptions:
        return image_base_url + exceptions[item] + ".png"
    else:
        return image_base_url + item.capitalize() + ".png"

def download_icon_if_missing(item):
    make_cache_folder_if_missing()
    icon_path = make_icon_path(item)
    if not os.path.exists(icon_path):
        url = make_icon_download_url(item)
        print(f"Downloading {icon_path} from {url}")
        r = requests.get(url)
        if r.status_code != 200:
            raise RuntimeError(f"GET request for {url} failed with error {r.status_code}")
        open(icon_path, "wb").write(r.content)
        
def open_image(item):
    """
    Open the image at cache/{item}.png
    """
    return PIL.Image.open(make_icon_path(item))
    

def get_icon(item):
    """
    Get the image (png) file as a 
    """
    try:
        download_icon_if_missing(item)
        return open_image(item)
    except:
        raise RuntimeError(f"Failed to get icon for {item}")
        
        
