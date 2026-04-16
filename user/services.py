"""Recommendation engine — cosine similarity on normalized feature vectors."""

import math


def get_recommendations(phones, preferences):
    """Return ranked phone recommendations with match scores and breakdowns.

    Args:
        phones: queryset or list of Phone objects
        preferences: dict with keys budget, performance, charging,
                     screen_size, storage, battery, camera, preferred_brand

    Returns:
        List of dicts sorted by match_score descending.
    """
    pref_vector = build_preference_vector(preferences)
    recommendations = []

    for phone in phones:
        phone_vector = build_phone_vector(phone)
        similarity = cosine_similarity(pref_vector, phone_vector)
        breakdown = compute_breakdown(preferences, pref_vector, phone_vector)

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
    return recommendations


def build_preference_vector(preferences):
    """Build normalized preference vector for cosine similarity.

    All dimensions are scaled to [0, 1] to match the phone vector scale.
    Levels (1-4) for performance/charging/battery/camera are divided by 4
    so they align with the same normalized range as actual phone specs.
    """
    return [
        preferences["budget"] / 20000,
        preferences["performance"] / 4,           # level 1-4 → 0-1
        preferences["charging"] / 4,             # level 1-4 → 0-1 (same scale as performance)
        preferences["screen_size"] / 10,
        preferences["storage"] / 1024,
        preferences["battery"] / 4,              # level 1-4 → 0-1
        preferences["camera"] / 4,               # level 1-4 → 0-1
    ]


def build_phone_vector(phone):
    """Build normalized phone feature vector for cosine similarity.

    Note: battery and camera use level-scale normalization (/4 and /4 respectively)
    to match the level-based preference form inputs. This keeps all dimensions
    on a comparable 0-1 scale for cosine similarity.
    """
    return [
        phone.price / 20000,
        phone.ram / 24,                         # max ~24GB RAM in dataset
        phone.charging / 240,                    # max ~240W charging
        phone.screen_size / 10,
        phone.rom / 1024,
        phone.battery / 4,                       # level 1-4 to match form scale
        phone.rear_camera / 4,                   # level 1-4 to match form scale
    ]


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def compute_breakdown(preferences, pref_vec, phone_vec):
    """Compute per-dimension contribution to the cosine similarity score.

    Each dimension's contribution is its share of the dot product,
    expressed as a percentage. Sum of all breakdown scores = 100%.
    """
    labels = ["Budget", "Performance", "Charging", "Screen Size", "Storage", "Battery", "Camera"]
    breakdown = []

    dot_product = sum(p * ph for p, ph in zip(pref_vec, phone_vec))
    for label, p_val, ph_val in zip(labels, pref_vec, phone_vec):
        if p_val > 0 and dot_product > 0:
            contribution = (p_val * ph_val) / dot_product
            breakdown.append({
                "label": label,
                "score": round(contribution * 100, 1),
            })

    return sorted(breakdown, key=lambda x: x["score"], reverse=True)
