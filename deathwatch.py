import argparse
import requests
import shutil
from os import path
from defusedxml import ElementTree as ET
import gzip

# https://www.nationstates.net/pages/regions.xml.gz 
# https://www.nationstates.net/pages/nations.xml.gz 

def download_file(mainNation,url):
    headers = {
        "User-Agent":f"DeathWatch/0.1, developed by Volstrostia, in use by {mainNation}"
    }

    print(f"Downloading {url}")
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True, headers=headers) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    
    return local_filename

def parseNations(mainNation, region, days):
    headers = {
        "User-Agent":f"DeathWatch/0.1, developed by Volstrostia, in use by {mainNation}"
    }

    r = requests.get(f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=nations", headers=headers)
    nations = ET.fromstring(r.text).findtext("NATIONS").split(":")
    print(f"Identified {len(nations)} nations in {region}")

    print("Loading nations.xml")
    with gzip.open("nations.xml.gz",mode="r") as f:
        rawnations = f.read()

    nationsxml = ET.fromstring(rawnations)
    print(f"Scanning for nations in {region}")

    numOld = 0
    for nation in nationsxml.findall("NATION"):
        if nation.find("REGION").text.lower().replace(" ","_") == region:
            #print(nation.find("NAME").text, nation.find("LASTLOGIN").text, nation.find("LASTACTIVITY").text)
            lastlogin = nation.find("LASTACTIVITY").text
            if "days" in lastlogin.lower():
                numDays = int(lastlogin.split(" days")[0])
                if numDays >= days:
                    print(f"{nation.find('NAME').text} last logged in {numDays} days ago")
                    numOld += 1

    print(f"Identified {numOld} nations who have logged in more than {days} days ago")


def main():
    # TODO: Argparse
    print("DeathWatch needs your main nation to comply with scripting requirements")

    mainNation = input("Main nation: ").lower().replace(" ","_")
    region = input("Region of interest: ").lower().replace(" ","_")
    days = input("Inactive for X days (default 25): ")
    if days:
        days = int(days)
    else:
        days = 25

    if path.isfile("nations.xml.gz"):
        print("Previous data dump detected.")
        downloadLatest = input("Download latest? (y/N) ")
        if downloadLatest and downloadLatest[0].lower() == "y": #Skip download
            download_file(mainNation, "https://www.nationstates.net/pages/nations.xml.gz") #Download nations datadump
            parseNations(mainNation, region, days)
        else:
            parseNations(mainNation, region, days) # Region?
    else:
        download_file(mainNation, "https://www.nationstates.net/pages/nations.xml.gz") #Download nations datadump
        parseNations(mainNation, region, days) # Region?

if __name__ == "__main__":
    main()
