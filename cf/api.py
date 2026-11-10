import random
import requests
from django.core.cache import cache
from ninja import FilterSchema, NinjaAPI, Schema

api = NinjaAPI()


class ResOut(Schema):
    rank: str
    maxRank: str
    handle: str
    maxRating: int
    rating: int

class ErrorOut(Schema):
    message: str

class ProblemFilterSchema(FilterSchema):
    rating: int

class VerifyIn(Schema):
    contestId: int
    index: str

class VerifyOut(Schema):
    verified: bool
    message: str

class Correctsub(Schema):
    message: str  # Fixed typo from 'messge'

@api.get("/perinfo", response={200: ResOut, 404: ErrorOut})
def profile(request, userinfo: str):
    url = "https://codeforces.com/api/user.info"
    res = requests.get(url, params={"handles": userinfo}, timeout=10)
    resdata = res.json()
    if resdata.get("status") == "OK":
        return resdata["result"][0]
    elif resdata.get("status") == "FAILED":
        comment = resdata.get("comment", "").lower()
        if "not found" in comment:
            return 404, {"message": "Incorrect user id"}
        return 404, {"message": comment}

CF_CACHE_KEY = "cf_filtered_problems"
CACHE_TIMEOUT = 60 * 60 * 24

def get_questions():
    cached_res = cache.get(CF_CACHE_KEY)
    if cached_res is not None:
        return cached_res
    url = "https://codeforces.com/api/problemset.problems"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    problems = res.json()["result"]["problems"]
    result = {"900": [], "1000": [], "1400": [], "1700": []}
    target_ratings = {900, 1000, 1400, 1700}
    for q in problems:
        rating = q.get("rating")
        if rating in target_ratings:
            result[str(rating)].append(q)

    cache.set(CF_CACHE_KEY, result, CACHE_TIMEOUT)
    return result

@api.get("/allq")
def qfetching(request):
    return get_questions()

@api.get("/submissionhistory")
def subfetching(request, userinfo: str):
    url = "https://codeforces.com/api/user.status"
    res = requests.get(url, params={"handle": userinfo}, timeout=10)
    resdata = res.json()
    if resdata.get("status") != "OK":
        return 404, {"message": "Could not fetch user submission history"}
    solved_set = {
        f"{q['problem'].get('contestId')}{q['problem'].get('index')}"
        for q in resdata.get("result", [])
        if q.get("verdict") == "OK" and "problem" in q
    }
    all_problems = get_questions()
    finres = {"1000": [], "1400": [], "1700": []}
    for rating in ["1000", "1400", "1700"]:
        pool = all_problems.get(rating, [])
        unsolved = [
            q for q in pool
            if f"{q.get('contestId')}{q.get('index')}" not in solved_set
        ]
        finres[rating] = unsolved

    finalres = {
        r: random.choice(finres[r]) if finres[r] else None
        for r in ["1000", "1400", "1700"]
    }
    return finalres

@api.get("/genverq")
def verq(request):
    problems = get_questions().get("900", [])
    return {"900": random.choice(problems) if problems else None}


@api.post("/verifyce", response={200: VerifyOut, 400: ErrorOut, 404: ErrorOut})
def verifyuser(request, userinfo: str, payload: VerifyIn):
    url = "https://codeforces.com/api/user.status"
    res = requests.get(url, params={"handle": userinfo, "from": 1, "count": 1}, timeout=10)
    resdata = res.json()
    if resdata.get("status") != "OK":
        return 404, {"message": "Could not fetch user submission history"}
    listq = resdata.get("result", [])
    if not listq:
        return 400, {"message": "No submissions found for this user"}

    latest = listq[0]
    problem = latest.get("problem", {})
    verdict = latest.get("verdict")
    same_problem = (
        problem.get("contestId") == payload.contestId
        and problem.get("index") == payload.index
    )
    if not same_problem:
        return 400, {"message": "Do compilation error at correct q"}

    if verdict != "COMPILATION_ERROR":
        return 400, {"message": "Expected verdict COMPILATION_ERROR"}

    return 200, {"verified": True, "message": "Handle successfully verified via compilation error"}


@api.post("/verifysub", response={200: Correctsub, 400: ErrorOut, 404: ErrorOut})
def verifysub(request, userinfo: str, payload: VerifyIn):
    url = "https://codeforces.com/api/user.status"
    res = requests.get(url, params={"handle": userinfo, "from": 1, "count": 1}, timeout=10)
    resdata = res.json()
    if resdata.get("status") != "OK":
        return 404, {"message": "Could not fetch user submission history"}
    listq = resdata.get("result", [])
    if not listq:
        return 400, {"message": "No submissions found for this user"}

    latest = listq[0]
    problem = latest.get("problem", {})
    verdict = latest.get("verdict")
    same_problem = (
        problem.get("contestId") == payload.contestId
        and problem.get("index") == payload.index
    )
    if not same_problem:
        return 400, {"message": "Q is not same"}

    if verdict != "OK":
        return 400, {"message": "Q is not solved"}
    return 200, {"message": "Problem successfully solved and verified"}