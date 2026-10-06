"""Source map data for ttrpg-convert-cli content sources.

Data extracted from the upstream source map at:
https://github.com/ebullient/ttrpg-convert-cli/blob/main/docs/sourceMap.md
"""

from __future__ import annotations

# Open-rule sources available without purchasing any books
OPEN_REFERENCE = [
    ("srd52", "SRD 5.2 (2024 open rules)"),
    ("basicRules2024", "2024 Free Rules"),
    ("srd", "SRD 5.1 (2014 open rules)"),
    ("basicrules", "Basic Rules (2014)"),
]

# 5eTools sources — books (full text content)
SOURCES_5E_BOOKS = [
    ("AAG", "Astral Adventurer's Guide"),
    ("AATM", "Adventure Atlas: The Mortuary"),
    ("ABH", "Astarion's Book of Hungers"),
    ("AI", "Acquisitions Incorporated"),
    ("AL", "Adventurers' League"),
    ("AU", "Arcana Unleashed"),
    ("AWM", "Adventure with Muk"),
    ("BAM", "Boo's Astral Menagerie"),
    ("BGG", "Bigby Presents: Glory of the Giants"),
    ("BMT", "The Book of Many Things"),
    ("CaBoMP", "Crochet: A Book of Many Patterns"),
    ("DMG", "Dungeon Master's Guide"),
    ("DMTCRG", "The Deck of Many Things: Card Reference Guide"),
    ("DoD", "Domains of Delight"),
    ("EFA", "Eberron: Forge of the Artificer"),
    ("EGW", "Explorer's Guide to Wildemount"),
    ("ERLW", "Eberron: Rising from the Last War"),
    ("FRAiF", "Forgotten Realms: Adventures in Faerun"),
    ("FRHoF", "Forgotten Realms: Heroes of Faerun"),
    ("FTD", "Fizban's Treasury of Dragons"),
    ("GGR", "Guildmasters' Guide to Ravnica"),
    ("HAT-TG", "Honor Among Thieves: Thieves' Gallery"),
    ("HF", "Heroes' Feast"),
    ("HFFotM", "Heroes' Feast Flavors of the Multiverse"),
    ("LFL", "Lorwyn: First Light"),
    ("MCV1SC", "Monstrous Compendium Volume 1: Spelljammer Creatures"),
    ("MCV4EC", "Monstrous Compendium Volume 4: Eldraine Creatures"),
    ("MGELFT", "Muk's Guide To Everything He Learned From Tasha"),
    ("MM", "Monster Manual"),
    ("MOT", "Mythic Odysseys of Theros"),
    ("MPMM", "Mordenkainen Presents: Monsters of the Multiverse"),
    ("MPP", "Morte's Planar Parade"),
    ("MTF", "Mordenkainen's Tome of Foes"),
    ("MaBJoV", "Minsc and Boo's Journal of Villainy"),
    ("NF", "Netheril's Fall"),
    ("OGA", "One Grung Above"),
    ("PaF", "Puncheons and Flagons"),
    ("PHB", "Player's Handbook"),
    ("RHW", "Ravenloft: The Horrors Within"),
    ("RMR", "D&D vs. Rick and Morty: Basic Rules"),
    ("SAC", "Sage Advice Compendium"),
    ("SatO", "Sigil and the Outlands"),
    ("SCAG", "Sword Coast Adventurer's Guide"),
    ("SCC", "Strixhaven: A Curriculum of Chaos"),
    ("TCE", "Tasha's Cauldron of Everything"),
    ("TD", "Tarot Deck"),
    ("VGM", "Volo's Guide to Monsters"),
    ("VRGR", "Van Richten's Guide to Ravenloft"),
    ("XDMG", "Dungeon Master's Guide (2024)"),
    ("XGE", "Xanathar's Guide to Everything"),
    ("XMM", "Monster Manual (2024)"),
    ("XPHB", "Player's Handbook (2024)"),
    ("XSAC", "Sage Advice Compendium (2025)"),
    ("XScreen", "Dungeon Master's Screen (2024)"),
    ("XScreenRHW", "DM's Screen; Ravenloft: The Horrors Within"),
]

# 5eTools sources — adventures (full text content)
SOURCES_5E_ADVENTURES = [
    ("AATM", "Adventure Atlas: The Mortuary"),
    ("AUD", "Arcana Unleashed: Deadfall"),
    ("AZfyT", "A Zib for your Thoughts"),
    ("AitFR-AVT", "Adventures in the Forgotten Realms: A Verdant Tomb"),
    ("AitFR-DN", "Adventures in the Forgotten Realms: Deepest Night"),
    ("AitFR-FCD", "Adventures in the Forgotten Realms: From Cyan Depths"),
    ("AitFR-ISF", "Adventures in the Forgotten Realms: In Scarlet Flames"),
    ("AitFR-THP", "Adventures in the Forgotten Realms: The Hidden Page"),
    ("BGDIA", "Baldur's Gate: Descent Into Avernum"),
    ("BQDD", "Borderlands Quest: Dagger Danger!"),
    ("BQGT", "Borderlands Quest: Goblin Trouble"),
    ("CM", "Candlekeep Mysteries"),
    ("CRCotN", "Critical Role: Call of the Netherdeep"),
    ("CoA", "Chains of Asmodeus"),
    ("CoS", "Curse of Strahd"),
    ("DC", "Divine Contention"),
    ("DD", "Dangerous Designs"),
    ("DIP", "Dragon of Icespire Peak"),
    ("DSotDQ", "Dragonlance: Shadow of the Dragon Queen"),
    ("DitLCoT", "Descent into the Lost Caverns of Tsojcanth"),
    ("DoDk", "Dungeons of Drakkenheim"),
    ("DoSI", "Dragons of Stormwreck Isle"),
    ("DrDe-ACfaS", "A Copper for a Song"),
    ("DrDe-BD", "A Copper for a Song"),
    ("DrDe-BtS", "Before the Storm"),
    ("DrDe-DaS", "Death at Sunset"),
    ("DrDe-DotSC", "Dragons of the Sandstone City"),
    ("DrDe-FWtVC", "For Whom the Void Calls"),
    ("DrDe-SD", "Shivering Death"),
    ("DrDe-TDoN", "The Dragon of Najkir"),
    ("DrDe-TFV", "The Forbidden Vale"),
    ("DrDe-TWoO", "The Will of Orcus"),
    ("EFR", "Eberron: Forgotten Relics"),
    ("FFotR", "Fated Flight of the Recluse"),
    ("FRAiF-TLLoL", "Forgotten Realms: The Lost Library of Lethchauntos"),
    ("FS", "Frozen Sick"),
    ("GoS", "Ghosts of Saltmarsh"),
    ("GotSF", "Giants of the Star Forge"),
    ("HBTD", "Hold Back The Dead"),
    ("HFStCM", "Heroes' Feast: Saving the Children's Menu"),
    ("HoL", "The House of Lament"),
    ("HotB", "Heroes of the Borderlands"),
    ("HotDQ", "Hoard of the Dragon Queen"),
    ("IDRotF", "Icewind Dale: Rime of the Frostmaiden"),
    ("IMR", "Infernal Machine Rebuild"),
    ("JttRC", "Journeys through the Radiant Citadel"),
    ("KKW", "Krenko's Way"),
    ("KftGV", "Keys from the Golden Vault"),
    ("LK", "Lightning Keep"),
    ("LLK", "Lost Laboratory of Kwalish"),
    ("LMoP", "Lost Mine of Phandelver"),
    ("LR", "Locathah Rising"),
    ("LRDT", "Red Dragon's Tale: A LEGO Adventure"),
    ("LoX", "Light of Xaryxis"),
    ("NRH-ASS", "NERDS Restoring Harmony: A Sticky Situation"),
    ("NRH-AT", "NERDS Restoring Harmony: Adventure Together"),
    ("NRH-AVitW", "NERDS Restoring Harmony: A Voice in the Wilderness"),
    ("NRH-AWoL", "NERDS Restoring Harmony: A Web of Lies"),
    ("NRH-CoI", "NERDS Restoring Harmony: Circus of Illusions"),
    ("NRH-TCMC", "NERDS Restoring Harmony: The Candy Mountain Caper"),
    ("NRH-TLT", "NERDS Restoring Harmony: The Lost Tomb"),
    ("OoW", "The Orrery of the Wanderer"),
    ("OotA", "Out of the Abyss"),
    ("PaBTSO", "Phandelver and Below: The Shattered Obelisk"),
    ("PiP", "Peril in Pinegrove"),
    ("PotA", "Princes of the Apocalypse"),
    ("QftIS", "Quests from the Infinite Staircase"),
    ("RMBRE", "The Lost Dungeon of Rickedness: Big Rick Energy"),
    ("RoT", "The Rise of Tiamat"),
    ("RtG", "Return to Glory"),
    ("SCC-ARiR", "A Reckoning in Ruins"),
    ("SCC-CK", "Campus Kerfuffle"),
    ("SCC-HfMT", "Hunt for Mage Tower"),
    ("SCC-TMM", "The Magister's Masquerade"),
    ("SDW", "Sleeping Dragon's Wake"),
    ("SKT", "Storm King's Thunder"),
    ("SLW", "Storm Lord's Wrath"),
    ("ScoEE", "Scions of Elemental Evil"),
    ("SjA", "Spelljammer Academy"),
    ("TLK", "The Lost Kenku"),
    ("TTP", "The Tortle Package"),
    ("TftYP-AtG", "Tales from the Yawning Portal: Against the Giants"),
    ("TftYP-DiT", "Tales from the Yawning Portal: Dead in Thay"),
    ("TftYP-TFoF", "Tales from the Yawning Portal: The Forge of Fury"),
    ("TftYP-THSoT", "Tales from the Yawning Portal: The Hidden Shrine of Tamoachan"),
    ("TftYP-TSC", "Tales from the Yawning Portal: The Sunless Citadel"),
    ("TftYP-ToH", "Tales from the Yawning Portal: Tomb of Horrors"),
    ("TftYP-WPM", "Tales from the Yawning Portal: White Plume Mountain"),
    ("ToA", "Tomb of Annihilation"),
    ("ToD", "Tyranny of Dragons"),
    ("ToFW", "Turn of Fortune's Wheel"),
    ("UtHftLH", "Uni and the Hunt for the Lost Horn"),
    ("VEoR", "Vecna: Eve of Ruin"),
    ("VNotEE", "Vecna: Nest of the Eldritch Eye"),
    ("WBtW", "The Wild Beyond the Witchlight"),
    ("WDH", "Waterdeep: Dragon Heist"),
    ("WDMM", "Waterdeep: Dungeon of the Mad Mage"),
    ("WttHC", "Stranger Things: Welcome to the Hellfire Club"),
    ("XMtS", "X Marks the Spot"),
]

# 5eTools sources — reference only (spells, classes, items, etc. without full text)
SOURCES_5E_REFERENCE = [
    ("ALCoS", "Adventurers League: Curse of Strahd"),
    ("ALEE", "Adventurers League: Elemental Evil"),
    ("ALRoD", "Adventurers League: Rage of Demons"),
    ("AitFR", "Adventures in the Forgotten Realms"),
    ("DrDe", "Dragon Delves"),
    ("EEPC", "Elemental Evil Player's Companion"),
    ("EET", "Elemental Evil: Trinkets"),
    ("EGW_DD", "Dangerous Designs (EGW)"),
    ("EGW_FS", "Frozen Sick (EGW)"),
    ("EGW_ToR", "Tide of Retribution (EGW)"),
    ("EGW_US", "Unwelcome Spirits (EGW)"),
    ("ESK", "Essentials Kit"),
    ("GHLoE", "Grim Hollow: Lairs of Etharis"),
    ("HAT-LMI", "Honor Among Thieves: Legendary Magic Items"),
    ("HFDoMM", "Heroes' Feast: The Deck of Many Morsels"),
    ("HWAitW", "Humblewood: Adventure in the Wood"),
    ("HWCS", "Humblewood Campaign Setting"),
    ("HftT", "Hunt for the Thessalhydra"),
    ("MCV2DC", "Monstrous Compendium Volume 2: Dragonlance Creatures"),
    ("MCV3MC", "Monstrous Compendium Volume 3: Minecraft Creatures"),
    ("MFF", "Mordenkainen's Fiendish Folio"),
    ("MisMV1", "Misplaced Monsters: Volume 1"),
    ("NRH", "NERDS Restoring Harmony"),
    ("PSA", "Plane Shift: Amonkhet"),
    ("PSD", "Plane Shift: Dominaria"),
    ("PSI", "Plane Shift: Innistrad"),
    ("PSK", "Plane Shift: Kaladesh"),
    ("PSX", "Plane Shift: Ixalan"),
    ("PSZ", "Plane Shift: Zendikar"),
    ("RoTOS", "The Rise of Tiamat Online Supplement"),
    ("SADS", "Sapphire Anniversary Dice Set"),
    ("SAiS", "Spelljammer: Adventures in Space"),
    ("SCREEN", "Dungeon Master's Screen"),
    ("SCREEN_DUNGEON_KIT", "DM's Screen: Dungeon Kit"),
    ("SCREEN_SPELLJAMMER", "DM's Screen: Spelljammer"),
    ("SCREEN_WILDERNESS_KIT", "DM's Screen: Wilderness Kit"),
    ("TftYP", "Tales from the Yawning Portal (common)"),
    ("ToB1-2023", "Tome of Beasts 1 (2023 Edition)"),
    ("UATMC", "Unearthed Arcana: The Mystic Class"),
    ("VD", "Vecna Dossier"),
]

# Pf2eTools sources — commonly used
SOURCES_PF2E_BOOKS = [
    ("CRB", "Core Rulebook"),
    ("APG", "Advanced Player's Guide"),
    ("B1", "Bestiary"),
    ("B2", "Bestiary 2"),
    ("B3", "Bestiary 3"),
    ("BB", "Beginner Box"),
    ("BotD", "Book of the Dead"),
    ("DA", "Dark Archive"),
    ("G&G", "Guns & Gears"),
    ("GMG", "Gamemastery Guide"),
    ("HotW", "Howl of the Wild"),
    ("LOACLO", "Lost Omens: Absalom, City of Lost Omens"),
    ("LOAG", "Lost Omens: Ancestry Guide"),
    ("LOCG", "Lost Omens: Character Guide"),
    ("LODM", "Lost Omens: Divine Mysteries"),
    ("LOGM", "Lost Omens: Gods & Magic"),
    ("LOIL", "Lost Omens: Impossible Lands"),
    ("LOKL", "Lost Omens: Knights of Lastwall"),
    ("LOL", "Lost Omens: Legends"),
    ("LOME", "Lost Omens: The Mwangi Expanse"),
    ("LOMM", "Lost Omens: Monsters of Myth"),
    ("LOPSG", "Lost Omens: Pathfinder Society Guide"),
    ("LORA", "Lost Omens: Rival Academies"),
    ("LOSK", "Lost Omens: Shining Kingdoms"),
    ("LOTG", "Lost Omens: Travel Guide"),
    ("LOTGB", "Lost Omens: The Grand Bazaar"),
    ("LOTXWG", "Lost Omens: Tian Xia World Guide"),
    ("LOWG", "Lost Omens: World Guide"),
    ("PC1", "Player Core"),
    ("PC2", "Player Core 2"),
    ("RoE", "Rage of Elements"),
    ("SoM", "Secrets of Magic"),
    ("TV", "Treasure Vault"),
    ("WoI", "War of Immortals"),
]

# All content type options for ttrpg-convert-cli configuration
REPRINT_BEHAVIORS = ["newest", "oldest", "all"]

DEFAULT_CONFIG = {
    "reprintBehavior": "newest",
    "racesAsSpecies": True,
    "splitRules": True,
    "images": {
        "copyInternal": False,
        "copyExternal": False,
    },
    "tagPrefix": "ttrpg-cli",
}


def all_5e_sources() -> list[tuple[str, str, str]]:
    """Return all 5e sources as (id, name, category) tuples."""
    result = []
    for sid, name in OPEN_REFERENCE:
        result.append((sid, name, "reference"))
    for sid, name in SOURCES_5E_BOOKS:
        result.append((sid, name, "book"))
    for sid, name in SOURCES_5E_ADVENTURES:
        result.append((sid, name, "adventure"))
    for sid, name in SOURCES_5E_REFERENCE:
        result.append((sid, name, "reference"))
    return result


def source_name_map() -> dict[str, str]:
    """Return a mapping from source ID to display name."""
    m = {}
    for sid, name in OPEN_REFERENCE:
        m[sid] = name
    for sid, name in SOURCES_5E_BOOKS:
        m[sid] = name
    for sid, name in SOURCES_5E_ADVENTURES:
        m[sid] = name
    for sid, name in SOURCES_5E_REFERENCE:
        m[sid] = name
    return m
