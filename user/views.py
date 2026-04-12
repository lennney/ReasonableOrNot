import hashlib

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import User


PHONES = [
    {
        "id": "p1",
        "name": "iPhone 14 Pro 128GB",
        "series": "iPhone 14 Pro",
        "price": 7099,
        "performance": 4,
        "storage_score": 5,
        "storage_gb": 128,
        "charging": 4,
        "battery": 3,
        "screen": 4,
        "camera": 3,
        "screen_size": 6.1,
        "summary": "Balanced entry point for the 14 Pro line with solid everyday performance.",
    },
    {
        "id": "p2",
        "name": "iPhone 14 Pro 256GB",
        "series": "iPhone 14 Pro",
        "price": 7899,
        "performance": 4,
        "storage_score": 6,
        "storage_gb": 256,
        "charging": 4,
        "battery": 3,
        "screen": 4,
        "camera": 3,
        "screen_size": 6.1,
        "summary": "A practical upgrade for users who want more local storage without changing the form factor.",
    },
    {
        "id": "p3",
        "name": "iPhone 14 Pro 512GB",
        "series": "iPhone 14 Pro",
        "price": 9299,
        "performance": 4,
        "storage_score": 7,
        "storage_gb": 512,
        "charging": 4,
        "battery": 3,
        "screen": 4,
        "camera": 3,
        "screen_size": 6.1,
        "summary": "For users who shoot often and keep a larger media library on-device.",
    },
    {
        "id": "p4",
        "name": "iPhone 14 Pro 1TB",
        "series": "iPhone 14 Pro",
        "price": 10199,
        "performance": 4,
        "storage_score": 8,
        "storage_gb": 1024,
        "charging": 4,
        "battery": 3,
        "screen": 4,
        "camera": 3,
        "screen_size": 6.1,
        "summary": "Built for creators who care more about capacity than price efficiency.",
    },
    {
        "id": "p5",
        "name": "iPhone 15 Pro 1TB",
        "series": "iPhone 15 Pro",
        "price": 12999,
        "performance": 4,
        "storage_score": 8,
        "storage_gb": 1024,
        "charging": 4,
        "battery": 4,
        "screen": 4,
        "camera": 4,
        "screen_size": 6.1,
        "summary": "Top-tier option for premium buyers focused on battery and camera improvements.",
    },
    {
        "id": "p6",
        "name": "iPhone 15 Pro 128GB",
        "series": "iPhone 15 Pro",
        "price": 7999,
        "performance": 4,
        "storage_score": 5,
        "storage_gb": 128,
        "charging": 4,
        "battery": 4,
        "screen": 4,
        "camera": 4,
        "screen_size": 6.1,
        "summary": "Good fit for users who want the newer generation but do not need large storage.",
    },
    {
        "id": "p7",
        "name": "iPhone 15 Pro 256GB",
        "series": "iPhone 15 Pro",
        "price": 8999,
        "performance": 4,
        "storage_score": 6,
        "storage_gb": 256,
        "charging": 4,
        "battery": 4,
        "screen": 4,
        "camera": 4,
        "screen_size": 6.1,
        "summary": "The most versatile choice when budget, capacity, and camera quality all matter.",
    },
    {
        "id": "p8",
        "name": "iPhone 15 Pro 512GB",
        "series": "iPhone 15 Pro",
        "price": 10999,
        "performance": 4,
        "storage_score": 7,
        "storage_gb": 512,
        "charging": 4,
        "battery": 4,
        "screen": 4,
        "camera": 4,
        "screen_size": 6.1,
        "summary": "A premium middle ground with strong capacity for creators and heavy users.",
    },
]

SCORING_FIELDS = [
    ("budget", "price", 0.28),
    ("performance", "performance", 0.12),
    ("charging", "charging", 0.10),
    ("screen_size", "screen_size", 0.10),
    ("storage", "storage_score", 0.18),
    ("battery", "battery", 0.12),
    ("camera", "camera", 0.10),
]


def index(request):
    username = request.session.get("username")
    return render(
        request,
        "user/index.html",
        {
            "username": username,
            "featured_phones": PHONES[4:7],
        },
    )


def login(request):
    if request.method == "GET":
        return render(request, "user/login.html", {"username": request.session.get("username")})

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    if not username or not password:
        return render(
            request,
            "user/login.html",
            {
                "error": "Please enter both username and password.",
                "username": request.session.get("username"),
            },
        )

    hashed_password = _hash_password(password)
    user = User.objects.filter(username=username, password=hashed_password).first()
    if not user:
        return render(
            request,
            "user/login.html",
            {
                "error": "Account not found or password is incorrect.",
                "username": request.session.get("username"),
            },
        )

    request.session["username"] = user.username
    return redirect("requirement")


def logout(request):
    request.session.flush()
    return redirect("index")


def requirement(request):
    return render(
        request,
        "user/requirement.html",
        {
            "username": request.session.get("username"),
            "preset_ranges": [
                {"label": "Level 1", "price": "0-4,000", "charging": "0-30W", "screen": "6.0", "storage": "128GB", "camera": "Basic"},
                {"label": "Level 2", "price": "4,000-8,000", "charging": "31-60W", "screen": "6.5", "storage": "256GB", "camera": "Balanced"},
                {"label": "Level 3", "price": "8,000-12,000", "charging": "61-90W", "screen": "6.8", "storage": "512GB", "camera": "Advanced"},
                {"label": "Level 4", "price": "12,000-16,000", "charging": "91-120W", "screen": "7.0+", "storage": "1TB", "camera": "Flagship"},
            ],
        },
    )


def recommend(request):
    if request.method != "POST":
        return redirect("requirement")

    preferences = _read_preferences(request)
    ranked_phones = [_build_recommendation(phone, preferences) for phone in PHONES]
    ranked_phones.sort(key=lambda item: item["match_score"], reverse=True)

    best_match = ranked_phones[0]
    alternatives = ranked_phones[1:4]

    return render(
        request,
        "user/recommend.html",
        {
            "username": request.session.get("username"),
            "preferences": preferences,
            "best_match": best_match,
            "alternatives": alternatives,
        },
    )


def result(request):
    ranked_by_value = sorted(
        [
            {
                **phone,
                "value_score": round(
                    (
                        phone["performance"]
                        + phone["battery"]
                        + phone["camera"]
                        + phone["screen"]
                        + phone["storage_score"] / 2
                    )
                    / phone["price"]
                    * 10000,
                    2,
                ),
            }
            for phone in PHONES
        ],
        key=lambda item: item["value_score"],
        reverse=True,
    )

    return render(
        request,
        "user/result.html",
        {
            "username": request.session.get("username"),
            "phones": ranked_by_value,
            "methodology": [
                "The project converts user preferences into a weighted profile.",
                "Each phone is scored by closeness to the expected price, storage, battery, and camera level.",
                "The final output highlights both the strongest match and nearby alternatives for comparison.",
            ],
        },
    )


def register(request):
    if request.method == "GET":
        return render(request, "user/register.html", {"username": request.session.get("username")})

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    email = request.POST.get("email", "").strip()

    if not username or not password or not email:
        return render(
            request,
            "user/register.html",
            {
                "error": "Username, password, and email are all required.",
                "username": request.session.get("username"),
            },
        )

    if User.objects.filter(username=username).exists():
        return render(
            request,
            "user/register.html",
            {
                "error": "This username already exists. Try another one.",
                "username": request.session.get("username"),
            },
        )

    User.objects.create(
        username=username,
        password=_hash_password(password),
        email=email,
    )

    return render(
        request,
        "user/register.html",
        {
            "success": "Registration completed. You can now sign in and start testing the recommender.",
            "username": request.session.get("username"),
        },
    )


def _hash_password(password):
    salted = password + settings.SECRET_KEY
    return hashlib.md5(salted.encode("utf-8")).hexdigest()


def _read_preferences(request):
    return {
        "budget": int(request.POST.get("budget", 8000)),
        "performance": int(request.POST.get("performance", 4)),
        "charging": int(request.POST.get("charging", 4)),
        "screen_size": float(request.POST.get("screen_size", 6.1)),
        "storage": int(request.POST.get("storage", 6)),
        "battery": int(request.POST.get("battery", 4)),
        "camera": int(request.POST.get("camera", 4)),
        "preferred_series": request.POST.get("preferred_series", "any"),
    }


def _build_recommendation(phone, preferences):
    score = 0
    breakdown = []

    for preference_key, phone_key, weight in SCORING_FIELDS:
        target = preferences[preference_key]
        actual = phone[phone_key]

        if preference_key == "budget":
            closeness = max(0, 1 - abs(target - actual) / max(target, actual, 1))
        else:
            closeness = max(0, 1 - abs(target - actual) / max(target, actual, 1))

        weighted = closeness * weight * 100
        score += weighted
        breakdown.append(
            {
                "label": preference_key.replace("_", " ").title(),
                "score": round(weighted, 1),
            }
        )

    series_bonus = 0
    if preferences["preferred_series"] != "any" and preferences["preferred_series"] in phone["series"].lower():
        series_bonus = 6
        score += series_bonus

    return {
        **phone,
        "match_score": round(score, 1),
        "series_bonus": series_bonus,
        "breakdown": sorted(breakdown, key=lambda item: item["score"], reverse=True),
    }
