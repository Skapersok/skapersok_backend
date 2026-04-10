import shutil
import json

import database as db
import dbmigrator
import paths
import auth

SAMPLE_ITEMS = [
    {
        "placement_code": "F-1-01",
        "name": "Smoke Alarm",
        "description": "Smoke alarm for detecting smoke",
        "keywords": "safety,alarm",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.10, 0.10], [0.18, 0.10], [0.18, 0.18], [0.10, 0.18]],
        },
    },
    {
        "placement_code": "F-1-02",
        "name": "Fire Alarm Pull Station",
        "description": "Manual activation of fire alarm",
        "keywords": "safety,alarm",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.20, 0.10], [0.28, 0.10], [0.28, 0.18], [0.20, 0.18]],
        },
    },
    {
        "placement_code": "F-2-01",
        "name": "Fire Extinguisher",
        "description": "ABC dry powder",
        "keywords": "safety,fire",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.10, 0.25], [0.18, 0.25], [0.18, 0.33], [0.10, 0.33]],
        },
    },
    {
        "placement_code": "F-2-02",
        "name": "Portable Fire Extinguisher",
        "description": "Small, mobile fire extinguisher",
        "keywords": "safety,fire",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.20, 0.25], [0.28, 0.25], [0.28, 0.33], [0.20, 0.33]],
        },
    },
    {
        "placement_code": "F-2-03",
        "name": "Handheld Fire Extinguisher",
        "description": "Compact extinguisher for small fires",
        "keywords": "safety,fire",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.30, 0.25], [0.38, 0.25], [0.38, 0.33], [0.30, 0.33]],
        },
    },
    {
        "placement_code": "F-2-04",
        "name": "Fire Hose Reel",
        "description": "Mounted fire hose for firefighting",
        "keywords": "safety,fire",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.40, 0.25], [0.48, 0.25], [0.48, 0.33], [0.40, 0.33]],
        },
    },
    {
        "placement_code": "F-2-05",
        "name": "Portable Fire Pump",
        "description": "Used to pump water during firefighting",
        "keywords": "safety,fire",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.50, 0.25], [0.58, 0.25], [0.58, 0.33], [0.50, 0.33]],
        },
    },
    {
        "placement_code": "F-2-06",
        "name": "Fire Blanket",
        "description": "Used to smother small fires",
        "keywords": "safety,fire",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.60, 0.25], [0.68, 0.25], [0.68, 0.33], [0.60, 0.33]],
        },
    },
    {
        "placement_code": "F-2-07",
        "name": "Emergency Fuel Shutoff",
        "description": "Device to stop fuel flow in emergencies",
        "keywords": "safety,fire",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.70, 0.25], [0.78, 0.25], [0.78, 0.33], [0.70, 0.33]],
        },
    },
    {
        "placement_code": "F-3-01",
        "name": "Fireproof Cabinet",
        "description": "Storage for documents and valuables",
        "keywords": "safety,fire",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.80, 0.25], [0.90, 0.25], [0.90, 0.35], [0.80, 0.35]],
        },
    },
    {
        "placement_code": "H-1-01",
        "name": "First Aid Kit",
        "description": "Basic first aid supplies",
        "keywords": "safety,health",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.10, 0.45], [0.18, 0.45], [0.18, 0.53], [0.10, 0.53]],
        },
    },
    {
        "placement_code": "H-1-02",
        "name": "Emergency Blanket",
        "description": "Thermal blanket for first aid",
        "keywords": "safety,health",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.20, 0.45], [0.28, 0.45], [0.28, 0.53], [0.20, 0.53]],
        },
    },
    {
        "placement_code": "H-1-03",
        "name": "Emergency Water Supply",
        "description": "Drinking water for emergencies",
        "keywords": "safety,health",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.30, 0.45], [0.38, 0.45], [0.38, 0.53], [0.30, 0.53]],
        },
    },
    {
        "placement_code": "H-2-01",
        "name": "Defibrillator (AED)",
        "description": "Automated external defibrillator for cardiac emergencies",
        "keywords": "safety,health,emergency",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.40, 0.45], [0.48, 0.45], [0.48, 0.53], [0.40, 0.53]],
        },
    },
    {
        "placement_code": "H-2-02",
        "name": "Portable Defibrillator Case",
        "description": "Carrying case for AED",
        "keywords": "safety,health,emergency",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.50, 0.45], [0.58, 0.45], [0.58, 0.53], [0.50, 0.53]],
        },
    },
    {
        "placement_code": "H-3-01",
        "name": "Emergency Shower",
        "description": "Safety shower for chemical exposure",
        "keywords": "safety,health",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.60, 0.45], [0.70, 0.45], [0.70, 0.60], [0.60, 0.60]],
        },
    },
    {
        "placement_code": "H-3-02",
        "name": "Eye Wash Station",
        "description": "Emergency station for eye rinsing",
        "keywords": "safety,health",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.72, 0.45], [0.82, 0.45], [0.82, 0.60], [0.72, 0.60]],
        },
    },
    {
        "placement_code": "H-3-03",
        "name": "Hand Sanitizer Station",
        "description": "Dispenses hand sanitizer",
        "keywords": "health,sanitation",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.84, 0.45], [0.92, 0.45], [0.92, 0.60], [0.84, 0.60]],
        },
    },
    {
        "placement_code": "H-4-01",
        "name": "Face Mask",
        "description": "Protective mask for airborne hazards",
        "keywords": "safety,health",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.10, 0.65], [0.18, 0.65], [0.18, 0.73], [0.10, 0.73]],
        },
    },
    {
        "placement_code": "H-4-02",
        "name": "Breathing Apparatus",
        "description": "Oxygen mask for hazardous air environments",
        "keywords": "safety,health",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.20, 0.65], [0.30, 0.65], [0.30, 0.78], [0.20, 0.78]],
        },
    },
    {
        "placement_code": "P-1-01",
        "name": "Safety Goggles",
        "description": "Protective eyewear for hazardous environments",
        "keywords": "safety,protective",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.35, 0.65], [0.43, 0.65], [0.43, 0.73], [0.35, 0.73]],
        },
    },
    {
        "placement_code": "P-1-02",
        "name": "Hard Hat",
        "description": "Head protection for construction zones",
        "keywords": "safety,helmet",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.45, 0.65], [0.55, 0.65], [0.55, 0.78], [0.45, 0.78]],
        },
    },
    {
        "placement_code": "P-1-03",
        "name": "Face Shield",
        "description": "Protective shield for face",
        "keywords": "safety,protective",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.58, 0.65], [0.66, 0.65], [0.66, 0.73], [0.58, 0.73]],
        },
    },
    {
        "placement_code": "P-2-01",
        "name": "Safety Gloves",
        "description": "Protective gloves for handling hazardous materials",
        "keywords": "safety,protective",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.68, 0.65], [0.76, 0.65], [0.76, 0.73], [0.68, 0.73]],
        },
    },
    {
        "placement_code": "P-2-02",
        "name": "Chemical Resistant Apron",
        "description": "Protective apron against chemicals",
        "keywords": "safety,chemical",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.78, 0.65], [0.88, 0.65], [0.88, 0.80], [0.78, 0.80]],
        },
    },
    {
        "placement_code": "P-3-01",
        "name": "Safety Boots",
        "description": "Steel-toe boots for workplace protection",
        "keywords": "safety,footwear",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.10, 0.82], [0.20, 0.82], [0.20, 0.92], [0.10, 0.92]],
        },
    },
    {
        "placement_code": "P-3-02",
        "name": "Ear Protection",
        "description": "Ear muffs or plugs for loud environments",
        "keywords": "safety,hearing",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.22, 0.82], [0.30, 0.82], [0.30, 0.92], [0.22, 0.92]],
        },
    },
    {
        "placement_code": "P-4-01",
        "name": "Safety Harness",
        "description": "Fall protection harness for working at heights",
        "keywords": "safety,fall",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.32, 0.82], [0.42, 0.82], [0.42, 0.95], [0.32, 0.95]],
        },
    },
    {
        "placement_code": "P-4-02",
        "name": "Safety Net",
        "description": "Netting to prevent falls from height",
        "keywords": "safety,fall",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.45, 0.82], [0.60, 0.82], [0.60, 0.95], [0.45, 0.95]],
        },
    },
    {
        "placement_code": "E-1-01",
        "name": "Emergency Light",
        "description": "Battery-powered lighting during power outage",
        "keywords": "safety,light",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.65, 0.82], [0.73, 0.82], [0.73, 0.90], [0.65, 0.90]],
        },
    },
    {
        "placement_code": "E-1-02",
        "name": "Emergency Whistle",
        "description": "Portable whistle for alerting others",
        "keywords": "safety,alert",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.75, 0.82], [0.80, 0.82], [0.80, 0.87], [0.75, 0.87]],
        },
    },
    {
        "placement_code": "E-1-03",
        "name": "Flood Light",
        "description": "High-power light for emergency areas",
        "keywords": "safety,light",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.82, 0.82], [0.92, 0.82], [0.92, 0.92], [0.82, 0.92]],
        },
    },
    {
        "placement_code": "E-2-01",
        "name": "Emergency Exit Sign",
        "description": "Illuminated sign indicating exit route",
        "keywords": "safety,exit",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.10, 0.95], [0.25, 0.95], [0.25, 1.00], [0.10, 1.00]],
        },
    },
    {
        "placement_code": "E-2-02",
        "name": "Rope Ladder",
        "description": "Portable ladder for emergency escape",
        "keywords": "safety,escape",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.28, 0.95], [0.36, 0.95], [0.36, 1.00], [0.28, 1.00]],
        },
    },
    {
        "placement_code": "E-2-03",
        "name": "Rescue Ladder",
        "description": "Ladder for rescue operations",
        "keywords": "safety,escape",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.38, 0.95], [0.48, 0.95], [0.48, 1.00], [0.38, 1.00]],
        },
    },
    {
        "placement_code": "E-2-04",
        "name": "Evacuation Chair",
        "description": "Chair for moving disabled persons down stairs",
        "keywords": "safety,evacuation",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.50, 0.95], [0.65, 0.95], [0.65, 1.00], [0.50, 1.00]],
        },
    },
    {
        "placement_code": "E-3-01",
        "name": "Emergency Phone",
        "description": "Phone for contacting emergency services",
        "keywords": "safety,communication",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.68, 0.95], [0.75, 0.95], [0.75, 1.00], [0.68, 1.00]],
        },
    },
    {
        "placement_code": "E-3-02",
        "name": "Safety Signage",
        "description": "Signs indicating hazards or instructions",
        "keywords": "safety,sign",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.77, 0.95], [0.87, 0.95], [0.87, 1.00], [0.77, 1.00]],
        },
    },
    {
        "placement_code": "E-3-03",
        "name": "Portable Barrier Tape",
        "description": "Warning tape for hazardous areas",
        "keywords": "safety,alert",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.89, 0.95], [0.98, 0.95], [0.98, 1.00], [0.89, 1.00]],
        },
    },
    {
        "placement_code": "M-1-01",
        "name": "Lockout/Tagout Kit",
        "description": "Prevents accidental machine startup",
        "keywords": "safety,machine",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.05, 0.05], [0.12, 0.05], [0.12, 0.12], [0.05, 0.12]],
        },
    },
    {
        "placement_code": "M-1-02",
        "name": "Emergency Stop Button",
        "description": "Stops machinery instantly in emergencies",
        "keywords": "safety,machine",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.14, 0.05], [0.20, 0.05], [0.20, 0.12], [0.14, 0.12]],
        },
    },
    {
        "placement_code": "M-2-01",
        "name": "Portable Generator",
        "description": "Backup power supply during outage",
        "keywords": "safety,power",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.22, 0.05], [0.35, 0.05], [0.35, 0.15], [0.22, 0.15]],
        },
    },
    {
        "placement_code": "C-1-01",
        "name": "Spill Kit",
        "description": "Absorbent materials for chemical spills",
        "keywords": "safety,chemical",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.38, 0.05], [0.46, 0.05], [0.46, 0.12], [0.38, 0.12]],
        },
    },
    {
        "placement_code": "C-2-01",
        "name": "Gas Detector",
        "description": "Detects harmful gas leaks",
        "keywords": "safety,gas",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.48, 0.05], [0.55, 0.05], [0.55, 0.12], [0.48, 0.12]],
        },
    },
    {
        "placement_code": "T-1-01",
        "name": "High-Visibility Vest",
        "description": "Reflective vest for visibility in low-light conditions",
        "keywords": "safety,visibility",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.58, 0.05], [0.66, 0.05], [0.66, 0.15], [0.58, 0.15]],
        },
    },
    {
        "placement_code": "T-2-01",
        "name": "Warning Cone",
        "description": "Cone for hazard or traffic warning",
        "keywords": "safety,alert",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.68, 0.05], [0.75, 0.05], [0.75, 0.15], [0.68, 0.15]],
        },
    },
    {
        "placement_code": "T-2-02",
        "name": "Traffic Barrier",
        "description": "Portable barrier for safety zones",
        "keywords": "safety,traffic",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.77, 0.05], [0.90, 0.05], [0.90, 0.18], [0.77, 0.18]],
        },
    },
    {
        "placement_code": "T-2-03",
        "name": "Crowd Control Barrier",
        "description": "Barrier for managing large gatherings",
        "keywords": "safety,control",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.05, 0.18], [0.20, 0.18], [0.20, 0.30], [0.05, 0.30]],
        },
    },
    {
        "placement_code": "T-3-01",
        "name": "Ladder",
        "description": "Portable ladder for safe height access",
        "keywords": "safety,access",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.22, 0.18], [0.30, 0.18], [0.30, 0.35], [0.22, 0.35]],
        },
    },
    {
        "placement_code": "F",
        "name": "Fire Safety",
        "description": "Equipment and systems designed to prevent, detect, and respond to fire-related hazards.",
        "keywords": "fire,safety,emergency,protection",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "F-1",
        "name": "Detection & Alarm",
        "description": "Devices used to detect fire, smoke, or heat and alert occupants of danger.",
        "keywords": "fire,alarm,detector,warning",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "F-2",
        "name": "Firefighting Equipment",
        "description": "Tools and equipment used to actively suppress or control fires.",
        "keywords": "firefighting,extinguisher,hose,emergency",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.5, 0.2], [0.7, 0.2], [0.7, 0.4], [0.5, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "F-3",
        "name": "Fire Protection & Storage",
        "description": "Fire-resistant storage and protective solutions for equipment and materials.",
        "keywords": "fire,storage,protection,cabinet",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.75, 0.2], [0.9, 0.2], [0.9, 0.4], [0.75, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "H",
        "name": "Health & First Aid",
        "description": "Health-related safety equipment and supplies for injury treatment and emergencies.",
        "keywords": "health,first aid,medical,safety",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.1, 0.1], [0.3, 0.1], [0.3, 0.3], [0.1, 0.3]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "H-1",
        "name": "Basic First Aid",
        "description": "Essential first aid supplies for treating minor injuries and medical issues.",
        "keywords": "first aid,medical,emergency,health",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "H-2",
        "name": "Cardiac & Emergency Equipment",
        "description": "Life-saving equipment for cardiac events and critical medical emergencies.",
        "keywords": "cardiac,aed,emergency,medical",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.5, 0.2], [0.7, 0.2], [0.7, 0.4], [0.5, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "H-3",
        "name": "Emergency Stations",
        "description": "Fixed stations providing immediate access to emergency health and safety equipment.",
        "keywords": "emergency,station,health,safety",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.75, 0.2], [0.9, 0.2], [0.9, 0.4], [0.75, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "H-4",
        "name": "Respiratory Protection",
        "description": "Protective equipment designed to safeguard breathing in hazardous environments.",
        "keywords": "respiratory,mask,breathing,protection",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.5], [0.4, 0.5], [0.4, 0.7], [0.2, 0.7]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "P",
        "name": "Personal Protection",
        "description": "Personal protective equipment used to reduce risk of injury or exposure.",
        "keywords": "ppe,personal protection,safety,equipment",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.1, 0.1], [0.3, 0.1], [0.3, 0.3], [0.1, 0.3]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "P-1",
        "name": "Head & Eye Protection",
        "description": "Protective equipment for safeguarding the head, face, and eyes.",
        "keywords": "helmet,goggles,eye protection,head protection",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "P-2",
        "name": "Hand & Body Protection",
        "description": "Protective gear for hands and body against mechanical or chemical hazards.",
        "keywords": "gloves,apron,body protection,chemical",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.5, 0.2], [0.7, 0.2], [0.7, 0.4], [0.5, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "P-3",
        "name": "Foot & Hearing Protection",
        "description": "Equipment protecting feet and hearing in hazardous work environments.",
        "keywords": "boots,hearing protection,earmuffs,footwear",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.75, 0.2], [0.9, 0.2], [0.9, 0.4], [0.75, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "P-4",
        "name": "Fall Protection",
        "description": "Systems and equipment designed to prevent falls from height.",
        "keywords": "fall protection,harness,safety net,height",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.5], [0.4, 0.5], [0.4, 0.7], [0.2, 0.7]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "E",
        "name": "Emergency & Evacuation",
        "description": "Equipment and systems supporting safe evacuation during emergencies.",
        "keywords": "emergency,evacuation,safety,escape",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.1, 0.1], [0.3, 0.1], [0.3, 0.3], [0.1, 0.3]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "E-1",
        "name": "Lighting & Alerts",
        "description": "Emergency lighting and alert systems used during power loss or danger.",
        "keywords": "emergency light,alert,warning,signal",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "E-2",
        "name": "Evacuation Equipment",
        "description": "Equipment designed to assist safe and rapid evacuation.",
        "keywords": "evacuation,escape,ladder,chair",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.5, 0.2], [0.7, 0.2], [0.7, 0.4], [0.5, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "E-3",
        "name": "Communication & Signage",
        "description": "Devices and signs used to communicate safety information and instructions.",
        "keywords": "communication,signage,emergency,information",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.75, 0.2], [0.9, 0.2], [0.9, 0.4], [0.75, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "M",
        "name": "Machinery & Power Safety",
        "description": "Safety systems related to machinery operation and power supply.",
        "keywords": "machinery,power,safety,lockout",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.1, 0.1], [0.3, 0.1], [0.3, 0.3], [0.1, 0.3]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "M-1",
        "name": "Machine Safety",
        "description": "Devices and procedures that reduce risk during machine operation.",
        "keywords": "machine safety,lockout,emergency stop",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "M-2",
        "name": "Power & Backup",
        "description": "Backup power and energy systems used during outages or emergencies.",
        "keywords": "power,backup,generator,energy",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.5, 0.2], [0.7, 0.2], [0.7, 0.4], [0.5, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "C",
        "name": "Chemical & Gas Safety",
        "description": "Safety equipment for handling chemical substances and gases.",
        "keywords": "chemical,gas,safety,hazard",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.1, 0.1], [0.3, 0.1], [0.3, 0.3], [0.1, 0.3]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "C-1",
        "name": "Chemical Spills",
        "description": "Equipment for containing and cleaning up chemical spills.",
        "keywords": "chemical spill,absorbent,cleanup",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "C-2",
        "name": "Gas Detection",
        "description": "Sensors and systems for detecting hazardous gas leaks.",
        "keywords": "gas detection,sensor,leak,monitoring",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.5, 0.2], [0.7, 0.2], [0.7, 0.4], [0.5, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "T",
        "name": "Traffic & Access Safety",
        "description": "Safety equipment related to traffic flow and controlled access.",
        "keywords": "traffic,access,safety,control",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.1, 0.1], [0.3, 0.1], [0.3, 0.3], [0.1, 0.3]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "T-1",
        "name": "Visibility",
        "description": "Equipment designed to improve visibility in low-light or hazardous conditions.",
        "keywords": "visibility,reflective,high visibility",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "T-2",
        "name": "Traffic Control",
        "description": "Devices used to guide, restrict, or control traffic flow.",
        "keywords": "traffic control,barrier,cone,warning",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.5, 0.2], [0.7, 0.2], [0.7, 0.4], [0.5, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
    {
        "placement_code": "T-3",
        "name": "Access Equipment",
        "description": "Equipment that enables safe access to elevated or restricted areas.",
        "keywords": "access,ladder,height,safety",
        "self_alignment": {
            "type": "cloud_child",
            "draw_points": [[0.75, 0.2], [0.9, 0.2], [0.9, 0.4], [0.75, 0.4]],
        },
        "children_arrangement": "{'type': 'cloud'}",
    },
]


# Path to default image
DEFAULT_MAP_IMAGE = paths.DATA_FOLDER_PATH.parent / "testinit" / "location.webp"
DEFAULT_DESC_IMAGE = paths.DATA_FOLDER_PATH.parent / "testinit" / "item.webp"
IMAGE_FOLDER = paths.DATA_FOLDER_PATH.parent / "data" / "img"


def create_sample_items(items):
    added = 0

    for item in items:
        if not db.get(item["placement_code"]):
            print(f"Adding sample item: {item['placement_code']}")
            db.add(
                item["placement_code"],
                item["name"],
                item.get("description", ""),
                item.get("keywords", ""),
                item.get("children_arrangement", ""),
                item.get("self_alignment", ""),
                item.get("color", ""),
            )
            added += 1
    print(f"Sample items added: {added}")


def duplicate_default_images(sample_items, overwrite=False):
    """
    Copies a default image to all image_path entries in SAMPLE_ITEMS.
    Skips existing files unless overwrite=True.
    """
    if not DEFAULT_MAP_IMAGE.exists():
        raise FileNotFoundError(
            f"Default location image '{DEFAULT_MAP_IMAGE}' not found!"
        )
    if not DEFAULT_DESC_IMAGE.exists():
        raise FileNotFoundError(f"Default item image '{DEFAULT_DESC_IMAGE}' not found!")

    IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)

    def copy_image(src, target_path):
        if target_path.exists() and not overwrite:
            print(f"Skipping existing file: {target_path}")
            return
        shutil.copy(src, target_path)
        print(f"Created: {target_path}")

    # Process items
    print("\nDuplicating images for SAMPLE_ITEMS...")
    for item in sample_items:
        # If item has a placement code, store in img folder
        if "placement_code" in item:
            target = IMAGE_FOLDER / "descimgs" / f"{item['placement_code']}.webp"
            copy_image(DEFAULT_DESC_IMAGE, target)
            target = IMAGE_FOLDER / "mapimgs" / f"{item['placement_code']}.webp"
            copy_image(DEFAULT_MAP_IMAGE, target)


if __name__ == "__main__":
    items = SAMPLE_ITEMS
    for item in items:
        if "self_alignment" in item and isinstance(item["self_alignment"], dict):
            item["self_alignment"] = json.dumps(item["self_alignment"])

    print("Removing database...")
    try:
        shutil.rmtree(paths.DATA_FOLDER_PATH)
    except FileNotFoundError:
        print("Database not found, skipping removal.")

    print("Creating new database...")
    dbmigrator.migrate()

    print("Filling the database with data...")
    create_sample_items(items)

    print("\nCreating placeholder images...")
    duplicate_default_images(items, overwrite=False)

    auth.create_user("admin", "password", "admin")

    print("\nSetup complete ✅")
