import math

from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .models import Phone, User
from . import services


def index(request):
    username = request.session.get("username")
    featured_phones = Phone.objects.all()[:3]
    return render(
        request,
        "user/index.html",
        {
            "username": username,
            "featured_phones": featured_phones,
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

    user = User.objects.filter(username=username).first()
    if not user or not check_password(password, user.password):
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
    brands = list(Phone.objects.values_list('brand', flat=True).distinct().order_by('brand'))
    return render(
        request,
        "user/requirement.html",
        {
            "username": request.session.get("username"),
            "brands": brands,
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
    phones = Phone.objects.all()

    # Filter by preferred brand if not "any"
    preferred_brand = preferences.get("preferred_brand")
    if preferred_brand and preferred_brand != "any":
        phones = phones.filter(brand=preferred_brand)

    if not phones.exists():
        return render(
            request,
            "user/recommend.html",
            {
                "username": request.session.get("username"),
                "preferences": preferences,
                "best_match": None,
                "alternatives": [],
                "error": "No phone data available. Please import the database first.",
            },
        )

    recommendations = services.get_recommendations(phones, preferences)

    best_match = recommendations[0]
    alternatives = recommendations[1:4]

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
    phones = Phone.objects.all()
    phone_list = []

    for phone in phones:
        # Value score: weighted sum of key specs divided by price, ×1000 for readability.
        # ROM counts 1/4 (storage is cheaper per GB), rear camera counts 1/2 (subjective quality),
        # front camera counts full weight. Battery counts 1/200 (large absolute numbers).
        perf_score = (phone.ram + phone.rom // 4 + phone.battery // 200 +
                      phone.front_camera + phone.rear_camera // 2) / max(phone.price, 1) * 1000
        phone_list.append({
            "brand": phone.brand,
            "model": phone.model,
            "price": phone.price,
            "ram": phone.ram,
            "rom": phone.rom,
            "battery": phone.battery,
            "rear_camera": phone.rear_camera,
            "value_score": round(perf_score, 2),
        })

    # TOP 20 highest value-score phones
    ranked_by_value = sorted(phone_list, key=lambda x: x["value_score"], reverse=True)[:20]

    return render(
        request,
        "user/result.html",
        {
            "username": request.session.get("username"),
            "phones": ranked_by_value,
            "methodology": [
                "The project converts user preferences into a feature vector.",
                "Cosine similarity measures the angle between the preference vector and each phone's feature vector.",
                "Higher similarity means the phone better matches the user's desired profile.",
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
        password=make_password(password),
        email=email,
    )

    request.session["username"] = username
    return redirect("requirement")


def _read_preferences(request):
    """Parse preference form fields from the POST request."""
    return {
        "budget": int(request.POST.get("budget", 8000)),
        "performance": int(request.POST.get("performance", 4)),
        "charging": int(request.POST.get("charging", 4)),
        "screen_size": float(request.POST.get("screen_size", 6.1)),
        "storage": int(request.POST.get("storage", 6)),
        "battery": int(request.POST.get("battery", 4)),
        "camera": int(request.POST.get("camera", 4)),
        "preferred_brand": request.POST.get("preferred_brand", "any"),
    }
