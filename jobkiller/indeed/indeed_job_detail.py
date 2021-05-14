from bs4 import BeautifulSoup as bs4
import requests
import json
from lxml import html
from pprint import pprint
from jobkiller.models.job import Job
import unicodedata
from jobkiller.indeed import indeed_job_list



def turnIndeedJobIntoJobOject(indeedJobUrl):
    # returns dummy model instead of a real Job object from jobmapJson
    jobmapJson = fetchIndeedJobDetailJson(indeedJobUrl)
    jobTitle = "title"
    companyName = "cmp"
    datePublished = "today"
    status = "not applied"
    jobUrl = indeedJobUrl
    recruiterEmail = "recruiter@gmail.com"
    job = Job(jobTitle, companyName, datePublished, status, jobUrl, recruiterEmail)
    return job



def fetchIndeedJobDetailJson(url):
    r = requests.get(url)
    html_bytes = r.text
    soup = bs4(html_bytes, 'lxml')
    jsonTemplate = '''
    {
        "jobDesc":"",
        "advantages":"",
        "workHours":"",
        "extraRewards":"",
        "cursusRequirements":"",
        "remoteWork":"",
        "safetyMeasures":"",
        "salary":"",
        "workplace":"",
        "contractType":""
    }
    '''
    jobJson = json.loads(jsonTemplate)

    if isJobFromIndeed(soup):
        jobJson = fillJsonWithCorrectTags(jobJson,soup)
    else:
        jobJson[jobDesc] = fillJobDescWithAllTags(soup)

    return jobJson


def isJobFromIndeed(soup):
    spanTag = "<span>Postuler</span>"
    if spanTag in str(soup): 
        return True
    return False

def fillJobDescWithAllTags(soup):
    allTags = getJobInfoList(soup)
    return "\n".join(allTags)

def getJobInfoList(soup):
    textList = []
    jobDescDiv = soup.find("div", {"id":"jobDescriptionText"})
    children = jobDescDiv.findChildren(recursive=True)
    for child in children:
        childText = unicodedata.normalize("NFKD",child.text)
        if childText not in textList:
            textList.append(childText)
    return textList

def fillJsonWithCorrectTags(jobDetailJson,soup):
    pTagsFrenchAndItsField = {
            "Avantages":"advantages",
            "Horaires":"workHours",
            "Rémunération":"extraRewards",
            "Formation":"cursusRequirements",
            "Télétravail":"remoteWork",
            "Précautions":"safetyMeasures",
            "Salaire":"salary",
            "Lieu de travail":"workplace",
            "Type d'emploi":"contractType"
    }
    jobInfoList = getJobInfoList(soup)
    currentField = "jobDesc"
    for info in jobInfoList:
        for pTag, field in pTagsFrenchAndItsField.items():
            info = unicodedata.normalize("NFKD",info)
            pTag = unicodedata.normalize("NFKD",pTag)
            if info.startswith(pTag):
                currentField = field
                break

        jobDetailJson[currentField] += info + "\n"

    return jobDetailJson

url = "https://fr.indeed.com/voir-emploi?q=R&D+Vision&t=D%C3%A9veloppeurs(ses)+informatique&jk=3fc9219d69b065f4"