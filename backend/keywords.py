# BITR Manipulation Keyword Lists

#Imported by detector.py

# 1. FEAR TRIGGERS (weight: 0.30)

FEAR_TRIGGERS = [
    "danger", "deadly", "fatal", "emergency", "crisis", "catastrophe", "alert", 
    "warning", "red alert", "maximum alert", "arrest warrant", "legal action",
    "court summons", "police case", "frozen", "blocked", "immediate arrest",
    "fbi", "interpol", "cbi", "raw", "terrorist", "hacking", "malware", 
    "virus detected", "account compromised",
    # --- Region Specific ---
    "kseb disconnection", "power will be disconnected at 9:30 pm", "electricity office notice",
    "previous month bill not updated", "contact electricity officer immediately",
    "mvd fine", "challan issued", "traffic penalty", "fastag blocked",
    "ktu exam cancelled", "ktu strict warning", "collector order", "district collector holiday",
    "5g radiation danger", "whatsapp gold", "red tick on whatsapp", "three blue ticks", 
    "calls are being recorded by government"
]


# 2. AUTHORITY IMPERSONATION (weight: 0.25)

AUTHORITY_IMPERSONATION = [
    "official notice", "government order", "ministry of health", "world health organization",
    "who", "unicef", "united nations", "fbi", "cia", "nasa", "official report",
    "verified source", "prime minister", "president office", "supreme court",
    # --- India/Kerala Specific ---
    "kerala police cyberdome", "cyber cell trivandrum", "rbi cyber cell", "rbi notice", "kseb official", 
    "district medical officer", "dmo warning", "collectorate", "ktu registrar",
    "asianet news exclusive", "mathrubhumi reported", "manorama news alert",
    "cm pinarayi vijayan announced", "kerala high court order", "kerala health ministry",
    "rbi governor", "department of telecommunications", "dot notice"
]


# 3. SCARCITY / URGENCY PRESSURE (weight: 0.20)

SCARCITY_URGENCY = [
    "act now", "last chance", "limited time", "offer ends", "hurry", "urgent",
    "immediately", "within 24 hours", "before it's too late", "expires today",
    "don't wait", "final warning", "now or never",
    # --- Region specific ---
    "link pan with aadhaar today", "free jio recharge ends today", "free bsnl data",
    "ambani free gift", "tata 100th anniversary reward", "kalyan silks free coupon",
    "onam bumper free ticket", "last date for scholarship", "kyc update pending"
]


# 4. SOCIAL PROOF MANIPULATION (weight: 0.15)

SOCIAL_PROOF = [
    "going viral", "everyone is talking", "millions of people", "trending now",
    "don't be the last to know", "shared by thousands", "breaking the internet",
    "world is watching", "thousands have already completed", "completed the process successfully",
    # --- Region Specific ---
    "forward to all malayalees", "share in all family groups", 
    "nammude naattil", "ellavarum ariyuka", "dayavayi share cheyyuka",
    "don't break the chain", "forwarded as received", "keralathile ellavarum kaanuka"
]


# 5. EMOTIONAL AMPLIFICATION (weight: 0.10)

EMOTIONAL_AMPLIFICATION = [
    "shocking", "unbelievable", "heartbreaking", "disgusting", "outrageous",
    "miracle", "amazing", "you won't believe", "must see", "shameful",
    # --- Region Specific ---
    "shradhikuka", "pradhana vaartha", "kashtam", "proud to be malayalee",
    "kerala is in danger", "save our children", "boycott", "manushyathvam undo"
]


# CREDIBILITY INDICATORS (Inverted Logic)

# 1. SOURCE_INDICATORS: Absence = PENALTY. 
#    If the text contains NONE of these, it is flagged as unverified.

# 2. SUSPICIOUS_URL_PATTERNS: Presence = PENALTY. 
#    Standard pattern (match adds to manipulation score).

SOURCE_INDICATORS = [
    "according to", "reported by", "source:", "cited by", "published by", 
    "as reported", "as per", "study by", "research by", "survey by", "data from",
    "times of india", "the hindu", "ndtv", "bbc", "reuters", "associated press", 
    "press trust of india", "pti", "ani news", "pib", "press information bureau"
]

SUSPICIOUS_URL_PATTERNS = [
    "bit.ly", "tinyurl", "t.co", "goo.gl", "ow.ly", "rb.gy", "shorturl.at", 
    "is.gd", "buff.ly", "wa.me", "t.me", "chat.whatsapp.com", "click-here",
    "claim-now", "win-prizes"
]
