from xml.dom import UserDataHandler

from flask import redirect, session
from biorhythm.dao import userDAO
import bcrypt


def login(username: str, password: str) -> bool:
    # find the user by username
    user = userDAO.findSingleUserByUsername(username)
    if not user:
        return False
    hashedPass = user["password"]
    # check if passwords match
    if bcrypt.checkpw(password=bytes(password, "utf-8"), hashed_password=hashedPass):
        session["userId"] = str(user["_id"])
        session["username"] = user["username"]
        return True
    else:
        return False


def logout():
    if "userId" in session:
        session.pop("userId")
        return True
    return False
