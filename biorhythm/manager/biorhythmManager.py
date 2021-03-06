# Dashboard Manager
import datetime
import math
import string
from flask import session
from biorhythm.dao import userDAO
from bson import ObjectId
from biorhythm.manager import eventManager

def getBioRhythm(userId: string) -> bool:
    user = userDAO.getUserById(userId=ObjectId(userId))
    # check if the biorhythm is updated
    if datetime.datetime.today() - user["biorhythm"]["startDate"] > datetime.timedelta(
        days=0
    ):
        # out of date, calculate and update, then return
        newBiorhythm = calculateBioRhythm(user["birthdate"])
        user = userDAO.updateUserBioRhythm(
            userId=ObjectId(userId), biorhythm=newBiorhythm
        )
        return user["biorhythm"]
    else:
        # updated, return object
        return user["biorhythm"]


def calculateBioRhythm(birthdate: datetime.datetime) -> dict:
    pArr = [None] * 10
    eArr = [None] * 10
    iArr = [None] * 10
    for i in range(1, 11):
        pArr[i - 1] = getPhysicalBioRhythm(getDaysFromBirthToday(birthdate, offset=i))
        eArr[i - 1] = getEmotionalBioRhythm(getDaysFromBirthToday(birthdate, offset=i))
        iArr[i - 1] = getIntellectualBioRhythm(getDaysFromBirthToday(birthdate, offset=i))
    biorhythm = {
        "physical": pArr,
        "emotional": eArr,
        "intellectual": iArr,
        "startDate": datetime.datetime.today(),
        "endDate": datetime.datetime.today() + datetime.timedelta(days=10),
    }
    return biorhythm

def getDaysFromBirthToday(birthdate: datetime.datetime, offset: int) -> int:
    baseDate = datetime.datetime.today() + datetime.timedelta(days=offset)
    return (baseDate - birthdate).days


def getPhysicalBioRhythm(delta: int) -> float:
    return round(math.sin((2 * math.pi * delta) / 23), 4)


def getEmotionalBioRhythm(delta: int) -> float:
    return round(math.sin((2 * math.pi * delta) / 28), 4)


def getIntellectualBioRhythm(delta: int) -> float:
    return round(math.sin((2 * math.pi * delta) / 33), 4)

def getBioRhythmTypeForEvent(userId: string, eventDate: datetime.datetime) -> str:
    user = userDAO.getUserById(userId=ObjectId(userId))

    eventDate = datetime.datetime.strptime(eventDate, '%Y-%m-%d')

    physical = getPhysicalBioRhythm((eventDate - user["birthdate"]).days)
    emotional = getEmotionalBioRhythm((eventDate - user["birthdate"]).days)
    intellectual = getIntellectualBioRhythm((eventDate - user["birthdate"]).days)
    
    types = [physical, emotional, intellectual]

    biorhythmType = 0.0
    for type in types:
        if type > biorhythmType:
            biorhythmType = type
    if (biorhythmType == physical):
        return 'physical'
    elif (biorhythmType == emotional):
        return 'emotional'
    else:
        return 'intellectual'

def getFriendsToInviteByBioRhythm(eventId: ObjectId):
    event = eventManager.getEvent(eventId)
    friends = eventManager.getUsers()
    friendsToInvite = []
    for friend in friends:
        brType = getBioRhythmTypeForEvent(str(friend['_id']['$oid']), event['eventDate'])
        if (brType == event['biorhythmType'] and ({'userId': str(friend['_id']['$oid']), 'username': friend['username']} not in event['invitedUsers'])):
            friendsToInvite.append({'userId': str(friend['_id']['$oid']), 'username': friend['username']})
    return friendsToInvite

