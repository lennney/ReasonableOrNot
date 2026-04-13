import math

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .models import Phone, User


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

    hashed_password = make_password(password)
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

    # Normalize features and compute cosine similarity
    pref_vector = _build_preference_vector(preferences)
    recommendations = []

    for phone in phones:
        phone_vector = _build_phone_vector(phone)
        similarity = _cosine_similarity(pref_vector, phone_vector)
        breakdown = _compute_breakdown(phone, preferences, pref_vector, phone_vector)

        recommendations.append({
            "id": phone.id,
            "brand": phone.brand,
            "model": phone.model,
            "price": phone.price,
            "cpu": phone.cpu,
            "ram": phone.ram,
            "rom": phone.rom,
            "charging": phone.charging,
            "battery": phone.battery,
            "screen_size": phone.screen_size,
            "front_camera": phone.front_camera,
            "rear_camera": phone.rear_camera,
            "match_score": round(similarity * 100, 1),
            "breakdown": breakdown,
        })

    recommendations.sort(key=lambda x: x["match_score"], reverse=True)

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
        # Value score: performance metrics per price unit
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


def _build_preference_vector(preferences):
    """Build normalized preference vector for cosine similarity."""
    # Map preferences to feature scale (1-4 normalized to 0-1)
    return [
        preferences["budget"] / 20000,           # budget: 0-20000
        preferences["performance"] / 4,           # performance: 1-4
        preferences["charging"] / 150,            # charging: 0-150W
        preferences["screen_size"] / 10,         # screen size: 0-10 inch
        preferences["storage"] / 1024,            # storage: 0-1024GB (using level as proxy)
        preferences["battery"] / 7000,            # battery: 0-7000mAh
        preferences["camera"] / 4,               # camera level: 1-4
    ]


def _build_phone_vector(phone):
    """Build normalized phone feature vector for cosine similarity."""
    return [
        phone.price / 20000,
        phone.ram / 24,                         # max ~24GB RAM in dataset
        phone.charging / 240,                    # max ~240W charging
        phone.screen_size / 10,
        phone.rom / 1024,                        # storage in GB
        phone.battery / 7000,
        phone.rear_camera / 20000,               # max ~200MP in dataset
    ]


def _cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def _compute_breakdown(phone, preferences, pref_vec, phone_vec):
    """Compute contribution of each feature to the similarity score."""
    labels = ["Budget", "Performance", "Charging", "Screen Size", "Storage", "Battery", "Camera"]
    breakdown = []

    for i, (label, p_val, ph_val) in enumerate(zip(labels, pref_vec, phone_vec)):
        if p_val > 0:
            contribution = (p_val * ph_val) / max(sum(pref_vec), 0.001)
            breakdown.append({
                "label": label,
                "score": round(contribution * 100, 1),
            })

    return sorted(breakdown, key=lambda x: x["score"], reverse=True)
