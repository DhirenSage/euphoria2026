"""Authoritative EUPHORIA 2K26 registration catalogue for preview seeding."""

CATEGORIES = [
    {"id": "cultural", "name": "Cultural", "order": 1},
    {"id": "literary-management", "name": "Literary and Management", "order": 2},
    {"id": "sci-pha-agro", "name": "Sci-Pha-Agro (The Magic of Science)", "order": 3},
    {"id": "sports", "name": "Sports", "order": 4},
]

EVENTS = [
    ("cultural", "Move & Groove (Solo Dance Competition)", "move-groove-solo-dance", 299, "individual", None, None),
    ("cultural", "Move & Groove (Group Dance Competition)", "move-groove-group-dance", 899, "team", 2, 20),
    ("cultural", "Swar Fiesta (Solo Singing Competition)", "swar-fiesta-solo-singing", 299, "individual", None, None),
    ("cultural", "Battle of Bands", "battle-of-bands", 2499, "team", 3, 12),
    ("cultural", "Rap Battle", "rap-battle", 249, "individual", None, None),
    ("cultural", "Fashion-Fiesta (Fashion Show – Solo Model Round)", "fashion-fiesta-solo-model", 799, "individual", None, None),
    ("cultural", "Fashion-Fiesta (Designer Round – Min 4 Garments)", "fashion-fiesta-designer-round", 2499, "individual", None, None),
    ("cultural", "Model Hunt (Audition)", "model-hunt-audition", 199, "individual", None, None),
    ("cultural", "Game Mania", "game-mania", 99, "individual", None, None),
    ("cultural", "Reel Making Competition", "reel-making-competition", 199, "individual", None, None),
    ("literary-management", "Crack the Clue (Treasure Hunt)", "crack-the-clue-treasure-hunt", 999, "team", 2, 6),
    ("literary-management", "Bid To Win (IPL Auction)", "bid-to-win-ipl-auction", 499, "team", 2, 5),
    ("literary-management", "The Great Debate", "the-great-debate", 249, "individual", None, None),
    ("literary-management", "Vocal Ink (Slam Poetry)", "vocal-ink-slam-poetry", 249, "individual", None, None),
    ("sci-pha-agro", "Model/Product Making Presentation", "model-product-making-presentation", 249, "individual", None, None),
    ("sci-pha-agro", "Oral / Poster Presentation", "oral-poster-presentation", 249, "individual", None, None),
    ("sci-pha-agro", "On Spot / Attending", "on-spot-attending", 299, "individual", None, None),
    ("sports", "Cricket", "cricket", 1600, "team", 11, 15),
    ("sports", "Football", "football", 1000, "team", 7, 14),
    ("sports", "Basketball", "basketball", 1000, "team", 5, 12),
    ("sports", "Kabaddi", "kabaddi", 800, "team", 7, 12),
    ("sports", "Carrom", "carrom", 200, "individual", None, None),
    ("sports", "Chess", "chess", 200, "individual", None, None),
    ("sports", "Volleyball", "volleyball", 800, "team", 6, 12),
    ("sports", "Table Tennis", "table-tennis", 250, "individual", None, None),
    ("sports", "Badminton (Singles) Men", "badminton-singles-men", 300, "individual", None, None),
    ("sports", "Badminton (Doubles) Men", "badminton-doubles-men", 400, "team", 2, 2),
    ("sports", "Badminton (Singles) Women", "badminton-singles-women", 200, "individual", None, None),
    ("sports", "Badminton (Doubles) Women", "badminton-doubles-women", 400, "team", 2, 2),
    ("sports", "Power Lifting", "power-lifting", 300, "individual", None, None),
    ("sports", "Weight Lifting", "weight-lifting", 300, "individual", None, None),
    ("sports", "Arm Wrestling", "arm-wrestling", 150, "individual", None, None),
]

CATEGORY_NAMES = {item["id"]: item["name"] for item in CATEGORIES}

CATEGORY_DETAILS = {
    "cultural": {
        "venue": "Main Auditorium · SAGE University Indore",
        "banner_url": "https://images.unsplash.com/photo-1506157786151-b8491531f063?auto=format&fit=crop&w=1800&q=85",
        "eligibility": "Open to school and college students with a valid institutional ID.",
        "coordinator_name": "EUPHORIA Cultural Coordination Team",
    },
    "literary-management": {
        "venue": "Seminar Hall · SAGE University Indore",
        "banner_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1800&q=85",
        "eligibility": "Open to school and college students; participants must carry a valid ID.",
        "coordinator_name": "EUPHORIA Literary & Management Team",
    },
    "sci-pha-agro": {
        "venue": "Innovation Lab · SAGE University Indore",
        "banner_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1800&q=85",
        "eligibility": "Open to student innovators; original work and institutional ID are required.",
        "coordinator_name": "EUPHORIA Sci-Pha-Agro Team",
    },
    "sports": {
        "venue": "University Sports Complex · SAGE University Indore",
        "banner_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1800&q=85",
        "eligibility": "Open to school and college students who are medically fit to participate.",
        "coordinator_name": "EUPHORIA Sports Coordination Team",
    },
}


def build_event_document(event):
    category_id, name, slug, fee, registration_type, min_team_size, max_team_size = event
    details = CATEGORY_DETAILS[category_id]
    rules = [
        "Carry the registration confirmation and a valid institutional photo ID.",
        "Report at the venue at least 30 minutes before the scheduled start.",
        "Follow coordinator, safety and venue instructions throughout the event.",
        "The judges' and organising committee's decision will be final.",
    ]
    if registration_type == "team":
        rules.insert(1, f"Teams must have between {min_team_size} and {max_team_size} registered members.")
    return {
        "id": slug,
        "category_id": category_id,
        "category_name": CATEGORY_NAMES[category_id],
        "name": name,
        "slug": slug,
        "short_description": f"Step into {name} and make your EUPHORIA 2K26 moment count.",
        "description": f"{name} is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.",
        "event_type": "sports" if category_id == "sports" else "competition",
        "registration_type": registration_type,
        "fee": fee,
        "capacity": 250,
        "venue": details["venue"],
        "status": "registration_open",
        "min_team_size": min_team_size,
        "max_team_size": max_team_size,
        "banner_url": details["banner_url"],
        "event_date": "15 September 2026",
        "event_time": "10:00 AM – 6:00 PM",
        "registration_deadline": "14 September 2026 · 11:59 PM",
        "eligibility": details["eligibility"],
        "rules": rules,
        "prizes": ["Winner trophy and merit certificate", "Runner-up merit certificate", "Participation certificate for eligible participants"],
        "coordinator_name": details["coordinator_name"],
        "coordinator_contact": "EUPHORIA Event Desk · SAGE University Indore",
        "schedule": [
            {"time": "09:30 AM", "title": "Reporting & verification"},
            {"time": "10:00 AM", "title": "Event briefing"},
            {"time": "10:15 AM", "title": "Competition begins"},
            {"time": "05:30 PM", "title": "Results & recognition"},
        ],
    }


EVENT_DOCUMENTS = [build_event_document(event) for event in EVENTS]


async def ensure_catalogue(db) -> None:
    for category in CATEGORIES:
        await db.euphoria_categories.update_one({"id": category["id"]}, {"$set": category}, upsert=True)
    for event in EVENT_DOCUMENTS:
        await db.euphoria_events.update_one({"id": event["id"]}, {"$set": event}, upsert=True)
    await db.euphoria_events.create_index("id", unique=True)
    await db.euphoria_registrations.create_index("registration_id", unique=True)