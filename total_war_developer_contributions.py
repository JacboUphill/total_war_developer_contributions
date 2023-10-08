"""
Statistics and visualizations about Total War developer contributions.
"""
import glob
import json
import os
import re
from typing import List

from bs4 import BeautifulSoup
from matplotlib_venn import venn3
from matplotlib import pyplot as plt
import plotly.graph_objects as go


class TotalWarDeveloperContributions:
    """
    Processes credits files from Total War games and generates statistics and visualizations.
    """
    def __init__(self):
        self.include_sections = [
            # These are sections which aren't relevant to how we're using the data
            # but we want to include the various roles within them
            "Ajax & Diomedes",
            "Brand, PR and Community",
            "CA QA",
            "CA SOFIA",
            "Creative Assembly",
            "Creative Assembly Sofia",
            "Dialogue Department",
            "GAME MANAGEMENT",
            "MUSICIANS",
            "MUSIC PRODUCTION:",
            "Mythos",
            "NEW CONTENT TEAM",
            "Rhesus and Memnon",
            "THE CREATIVE ASSEMBLY",
            "THE CREATIVE ASSEMBLY, BRISBANE AUSTRALIA",
            "THE CREATIVE ASSEMBLY, SOUTHWATER UK",
        ]

        self.exclude_sections = [
            # These are sections which aren't relevant to how we're using the data
            # and we want to exclude them from this treatment since they deal primarily
            # with something like localization, support from parent company rather than
            # CA studio resources, or outsourced roles
            "Audio Contractors",
            "Audio (External)",
            "AUDIO (External)",
            "Audio (External) - Cast",
            "Audio (External) - Musicians",
            "Audio (External) - Sound, Dialogue and Music",
            "Audio (Internal) - Group Voices",
            "Berlin Studio",
            "Bucharest Studio",
            "Cairo Studio",
            "English &amp; Japanese Voice Production",
            "French Voice Production",
            "German Voice Production",
            "Istanbul Studio",
            "Italian Voice Production",
            "Keywords Studios FQA Testers",
            "Keywords Studios Localisation QA",
            "Localisation",
            "One Voice Productions",
            "OUTSOURCED ROLES",
            "PORTING TEAM",
            "Prague Studio",
            "Sega America",
            "Sega America Creative Services Team",
            "Sega America Mastering Lab",
            "Sega America Media Lab",
            "Sega America Web Team",
            "SEGA EUROPE",
            "SEGA Europe Limited Staff Credits",
            "SEGA Games Co. Ltd.",
            "Sega Localisation",
            "SEGA of America, Inc.",
            "Sega of China",
            "SEGA OF JAPAN (Japanese Version)",
            "SEGA Publishing Group",
            "SEGA QA",
            "SEGA Sofia QA",
            "SEGA Technical Group",
            "Sofia Studio",
            "Sound Department (External)",
            "Spanish Voice Production",
            "Vilnius Studio",
            "Voice Studio",
            "Warsaw Studio",
            "WITH THE SUPPORT OF",
            "Zagreb Studio",
        ]

        self.exclude_roles = [
            # These are unclear roles or contain loose text rather than just names
            "Additional material by",
            "Additional Thanks",
            "CA Production Babies",
            "CA Special Thanks To",
            "Development Babies",
            "DEVELOPMENT TEAM",
            "Production Babies",
            "Special Thanks To",
            "Special Thanks",
            "Thanks",
            # These are outsourced roles that reference some other studio or deal
            # with localisation or voice acting, which are disproportionately large
            # and would skew results, or other similarly large categories like orchestras
            "Actors UK Language",
            "Actors",
            "Additional Norsca DLC Voices",
            "Additional Voices",
            "Concept Art Contractor",
            "Contractors",
            "Crowds (cont.)",
            "Crowds",
            "English Actors",
            "Environment Art Contractors",
            "External Audio Engineer (Mediamill)",
            "French Dialogue Consultant",
            "Keywords QA",
            "Localisation Voice Actors",
            "Lucnica Chorus",
            "Marin \"Bai Marin\" Krunzov",
            "ORCHESTRA:",
            "Pinewood Studios",
            "Recording studio - The Slovak Radio Concert Hall, Bratislava",
            "Recording Studios",
            "Sega QA",
            "Steamworks Revision",
            "Translated by",
            "Voice Acting - English",
            "Voice Acting - French",
            "Voice Acting - Other Languages",
            "Voice Actors",
            # These are roles which are relevant but which to keep the data set relatively consistent and focused
            # on technical development resources have been omitted. It'd be totally reasonable to regenerate all
            # of the reports with these included.
            "Accounts Assistant",
            "Accounts Payable",
            "Additional Arrangements of Music",
            "Additional Composers",
            "Additional Marketing",
            "Additional MoCap Performance",
            "Additional Music",
            "Additional Musicians:",
            "Additional Musicians",
            "Additional Oud arrangements",
            "Additional Score Preparation",
            "Additional Support",
            "Analytics and User Research",
            "Arabic Flutes",
            "Arabic Percussion",
            "Associate Brand Designer",
            "Associate Brand Manager",
            "Associate Brand Managers",
            "Associate Community Manager",
            "Associate Content Producers",
            "Associate Development Communications Manager",
            "Associate Editorial & Localisation Co-ordinator",
            "Associate Localisation & Editorial Coordinator",
            "Associate Localisation Manager",
            "Associate Music Designer",
            "Associate Player Experience Manager",
            "Associate PR Manager",
            "Associate Web Developer",
            "Audio Administrator",
            "Bansuri",
            "Bass Flute",
            "BI Analyst & Developer",
            "BI Developer",
            "BI Developers",
            "Bone Flute, Bowed Lyre, Cow Horn",
            "Brand Designer",
            "Brand Manager",
            "Brand Team Development Manager",
            "Business Analyst",
            "Business Intelligence Developers",
            "Casting & Voice Production",
            "Casting and Voice Production",
            "Celtic Harp",
            "Character Art Contractors",
            "Chief Operating Officer",
            "Choir Master",
            "Cloud Infrastructure Engineer",
            "Communications Manager",
            "Community Co-ordinator",
            "Community Content Editor",
            "Community Development Manager",
            "Community Manager",
            "Community Team",
            "Composer",
            "Composers",
            "Conductor & Orchestrator:",
            "Conductor",
            "Consultant on Muslim Culture",
            "Content Producers",
            "CSR Coordinator",
            "Cura Saz, Baglama, Cumbus, Oud, Lyre",
            "Data Analyst",
            "Development Communications Manager",
            "Development Management",
            "Dialog & Additional Content",
            "Director of Corporate Communications",
            "Duduk",
            "Dulcimer, Santoor, Cimbalom",
            "Electric Cello",
            "Ethnic Winds",
            "Ethnic Woodwinds",
            "Event Manager",
            "Facilities Manager",
            "Fiddle & Cello",
            "Fight Choreography and Mocap Fight Performers",
            "Fight performance",
            "Fight production, direction and performance",
            "Fight production, direction",
            "Finance Assistant",
            "Finance Director",
            "Finance Manager",
            "Financial Business Analyst",
            "Financial Controller",
            "Foley artist",
            "Foley asset editor",
            "Foley Mixer / Sound editor",
            "Foley Mixer",
            "Forum Manager",
            "French Community Co-ordinator",
            "Front of House Administrator",
            "Front of House Administrators",
            "German Community Co-ordinator",
            "Head of Brand",
            "Head of Business Intelligence",
            "Head of Communications",
            "Head of Community Marketing",
            "Head of Corporate Communications",
            "Head of Data",
            "Head of Finance and Accounting",
            "Head of HR",
            "Head of IT",
            "Helpdesk Technician",
            "Historical Consultant",
            "Historical Research",
            "HR Administrator",
            "HR Administrators",
            "HR Advisor",
            "HR Advisors",
            "HR Business Partner (Maternity Cover)",
            "HR Business Partner",
            "HR Business Partners",
            "HR Director",
            "HR Manager",
            "HR Managers",
            "HR/Finance",
            "HR/Finance/IT",
            "Influencer Marketing Manager",
            "Influencer Relations Manager",
            "Infrastructure Engineer",
            "Infrastructure Engineers",
            "IT & Network Administrators",
            "IT Director",
            "IT Lead",
            "IT Manager",
            "IT Support Lead",
            "IT Support Manager",
            "IT Support",
            "IT System Administrator",
            "Junior Accountant",
            "Junior Brand Manager",
            "Junior Infrastructure Engineer",
            "Kemenche & Sarangi",
            "Kithara, Lute",
            "Lead BI Developer",
            "Lead Brand Designer",
            "Lead Brand Manager",
            "Lead Community & Social Media Manager",
            "Lead Community Manager",
            "Lead Content Producer",
            "Lead Infrastructure Engineer",
            "Lead Player Experience Manager",
            "Lead Web Developer",
            "Librarian and Score Co-ordinator",
            "Linux Administrator",
            "Linux Infrastructure Engineer",
            "Live Feedback Team",
            "Live Services",
            "Localisation and Editorial Coordinator",
            "Localisation Coordinator",
            "Management Accountant",
            "Mandocello, Pandura,Bouzouki, C\u00fcmb\u00fcs",
            "Mandolin & Guitar",
            "Manual",
            "Marketing & PR",
            "Marketing and PR Director",
            "Marketing",
            "Midi Transcription",
            "Mocap perfromance",
            "Morin Khuur",
            "Motion Capture Actors",
            "Motion Capture Choreographer and Director",
            "Motion Capture Performance",
            "Motion Capture Technician",
            "Music Assistant to Tilman Sillescu",
            "Music co-ordinator",
            "Music Contractor and Recording Manager",
            "Music orchestrated and conducted by",
            "Music preparation & Assistant engineer",
            "Music",
            "Musicians",
            "Online And PR Manager",
            "Operations Assistant",
            "Operations Manager",
            "Operations",
            "Orchestra & Choir manager",
            "Orchestra & Choir recorded and mixed",
            "Orchestra Manager",
            "Orchestration & Conducting",
            "Oud, Lyre, C\u00fcmb\u00fcs",
            "Oud, Saz, Setar, Tambura",
            "Percussion",
            "Player Experience Manager - China Region",
            "PR & Marketing",
            "PR & Online Manager",
            "PR and Online Manager",
            "PR Manager",
            "Principal Development Communications Manager",
            "Procurement Coordinator",
            "Producer - Platige",
            "Product Evangelist",
            "Public Relations",
            "Purchasing Assistant",
            "Purchasing Coordinator",
            "Recording and Mix Engineer",
            "Recording Engineers",
            "Recording manager",
            "Recruitment Administrator",
            "Recruitment Coordinator",
            "Recruitment Resourcer",
            "Recruitment Specialist",
            "Recruitment Specialists",
            "Relocation Coordinator",
            "Rubab, Tar, Kopuz & Santur",
            "Santur, Cimbalom",
            "Senior Accountant",
            "Senior BI Developer",
            "Senior Brand Manager",
            "Senior Community Manager",
            "Senior DevOps and Automation Manager",
            "Senior Finance Coordinator",
            "Senior Infrastructure Engineer",
            "Senior Infrastructure Engineers",
            "Senior Linux Infrastructure Engineer",
            "Senior Network Infrastructure Engineer",
            "Senior Network Technician",
            "Senior PR Manager",
            "Senior System Administrator",
            "Senior Web Developer",
            "Senior Web Developers",
            "Service Desk Lead",
            "Service Desk Technician",
            "Shakuhachi, Shinobue & Nohkan",
            "Singers",
            "Social Media Manager",
            "SQL BI Developer",
            "Studio Communications Manager",
            "Studio HR Manager",
            "Studio Support Assistant",
            "Studio Support Coordinator",
            "Studio Support Coordinators",
            "Studio Support Manager",
            "Support Desk Lead",
            "Support Desk Technician",
            "Support Desk Technicians",
            "Supporting Roles",
            "System Administrator",
            "Taiki Drums (Taikoz)",
            "Talent Manager",
            "Throat Singers",
            "Total War Universe Project Lead",
            "Total War Universe Senior Brand Manager",
            "Total War, Vice President",
            "Trainee Brand Manager",
            "Transcription and Copying",
            "Trumpet Fanfares",
            "TW Brand Team",
            "Universe Project Lead",
            "Vielle, Kemenche",
            "Viol & Kamaan",
            "Viola",
            "Vocals",
            "Vocals/Lyrics",
            "Voice Actors",
            "Voiceover Artists",
            "Voices",
            "Web Developer",
            "Web Development Manager",
            "Webmaster",
        ]

        self.exclude_entities = [
            # These are entities rather than individuals (I think...)
            "Animation",
            "Boffin Language Group",
            "Budapest Scoring Symphonic Orchestra",
            "Character Art",
            "Dynamedion",
            "Effective Media",
            "Environment",
            "ExeQuo",
            "FILMharmonic Orchestra and Choir, Prague",
            "Four For Music",
            "Great Britain Kendo Squad",
            "Kubler Auckland Management",
            "LUCNICA",
            "LUCNICA - SLOVAK NATIONAL CHAMBER CHOIR",
            "MotionCraft.de",
            "Musa",
            "Noiseworks",
            "Pinewood Studios",
            "Platige Image",
            "SLOVAK NATIONAL CHAMBER CHOIR",
            "Slovak National Symphony Orchestra",
            "Softclub",
            "Space Crate Ltd",
            "Studio 301",
            "THE SLOVAK NATIONAL SYMPHONY ORCHESTRA",
            "UI Art",
            "Virtuos",
            "Wabi Sabi",
        ]

        self.mapped_developers = {
            # For cases where it was obvious on skimming that two discrete names referred to the same
            # person, combine the entries here. Generally these are nicknames, shortened names, or accented vs not
            # accented characters applied to people working in the same role.
            "Agusti Curia": "Agustí Curià Morandeira",
            "Alba Rodriguez": "Alba Rodriguez del Rio",
            "Alex De Rosee": "Alex de Rosée",
            "Alex DeRosee": "Alex de Rosée",
            "Angel Diaz Romero": "Angel Gabriel Diaz Romero",
            "Callum Glover": "Cal Glover",
            "Chloe Bonnet": "Chloé Bonnet",
            "Chris Gray": "Christopher Gray",
            "Chris Johnston": "Christopher Johnston",
            "Chris Kemp": "Christopher Kemp",
            "Chris Reed": "Christopher Reed",
            "Csaba Toth": "Csaba Tóth",
            "Dan Glastonbury": "Daniel Glastonbury",
            "Dan McCarthy": "Daniel McCarthy",
            "Diego Gisbert Llorens": "Diego Gisbert-Llorens",
            "Dr Derek Fagan": "Derek Fagan",
            "Dr Tim Gosling": "Tim Gosling",
            "Duygu Cakmak": "Duygu Çakmak",
            "Eduardo Sanchez": "Eduardo Escudero Sanchez",
            "Ellie Koorlander-Lester": "Ellie Koorlander Lester",
            "Elliot Lock": "Elliott Lock",
            "Elliot Walder": "Elliott Walder",
            "Emma-Jayne Smith": "Emma Smith",
            "Georgi Georgiev": "Georgi Y. Georgiev",
            "Guy Davidson": "J. Guy Davidson",
            "Hannah Peratopoulous": "Hannah Peratopoullos",
            "Howard Raynor": "Howard Rayner",
            "Hriso Enev": "Hristo Enev",
            "Ivan Dionissiev": "Ivan Dionisiev",
            "James Woolridge": "James Wooldridge",
            "Jan Hendrickse": "Jan Hendrikse",
            "Jas Dhatt": "Jasmeet Dhatt",
            "Jerome. Rodgers-Blake": "Jerome Rodgers-Blake",
            "Johan Tann": "Johann Tan",
            "Jonathon Hemmens": "Jonathan Hemmens",
            "Joe Nicholson": "Joseph Nicholson",
            "Joey Dalton": "Josephine Dalton",
            "Josh Croft": "Joshua Croft",
            "Josh Williams": "Joshua Williams",
            "Kevin Mcdowell": "Kevin McDowell",
            "Kishore Kumar JV": "Kishore Kumar",
            "Konstantinos Vlachav": "Konstantinos Vlachavas",
            "Krystiana Gutbub": "Krystiana Maria Gutbub",
            "Lothar Zhou": "Lothar W Zhou",
            "Marcos Sueiro": "Marcos Sueiro Eglicerio",
            "Mariusz Kozik": "Marius Kozik",
            "Mark Tarrisse": "Mark Tarisse",
            "Matt Fidler": "Matthew Fidler",
            "Matt Hall": "Matthew Hall",
            "Matt Lewis": "Matthew Lewis",
            "Matt McCamley": "Matthew McCamley",
            "Matt Starbuck": "Matthew Starbuck",
            "Matt Wright": "Matthew Wright",
            "Michael Pettit": "Michael Pettitt",
            "Michael De Plater": "Michael de Plater",
            "Mikaela Lidstrom": "Mikaela Lidström",
            "Mike James": "Michael James",
            "Mitch Heastie": "Mitchell Heastie",
            "Mohammed Thanish": "Mohamed Thanish",
            "Morten Zimmermann": "Morten Zimmerman",
            "Nat Martin": "Natalie Martin",
            "Nick Tresedern": "Nick Tresadern",
            "Olly Brabiner": "Oliver Brabiner",
            "Pablo Estevez": "Pablo Perez Estevez",
            "Pete Brophy": "Peter Brophy",
            "Pete Clapperton": "Peter Clapperton",
            "Pete Stewart": "Peter Stewart",
            "Peter Juhasz": "Péter Juhász",
            "Peter Lameroux": "Peter Lamoureux",
            "Phil Abram": "Phillip Abram",
            "Phil Gradidge": "Phillip Gradidge",
            "R. T. Smith": "R.T. Smith",
            "Rene Vravko": "René Vravko",
            "Rich Broadhurst": "Richard Broadhurst",
            "Rich Aldridge": "Richard Aldridge",
            "Richard Gardener": "Richard Gardner",
            "Rob Farrell": "Robert Farrell",
            "Roland McDonald": "Roland MacDonald",
            "Sam Price": "Samuel Price",
            "Sam Simpson": "Samuel Simpson",
            "Samar Vijay": "Samar Vijay Singh",
            "Sonya Verchenko": "Sonya Virchenko",
            "Stefan Bakarov": "Stephan Bakarov",
            "Stephane Gros-Lemesre": "Stéphane Gros-Lemesre",
            "Stephanie Yath": "Stéphanie Yath",
            "Sylvia Hallett": "Sylvia Hallet",
            "Tamas Rebel": "Tamás Rábel",
            "Ting Li": "Ting Pong Li",
            "Tom Cleaves": "Thomas Cleaves",
            "Tom Parker": "Thomas Parker",
            "Tom Philips": "Tom Phillips",
            "Valentin Goellner": "Valentin Göellner",
            "Valentin Göllner": "Valentin Göellner",
            "Veronika Chorbadjieva": "Veronika Chorbadzhieva",
            "Vic Prentice": "Victoria Prentice",
            "Vicky Danko": "Victoria Danko",
            "Viktorija Ardamatska": "Viktorija Ardamatskaja",
            "Vlad Costin": "Vladimir Costin",
            "Will Meaton": "William Meaton",
            "Will Tidman": "William Tidman",
            "Will Wright": "William Wright",
            "William Hakestad": "William Håkestad",
            "Zoltan A. Molnar": "Zoltan Molnar",
        }

        # Used for generating the flow visualization
        self.game_metadata = {
            "2000_shogun": {
                "color_code": "rgba(205, 127, 50, 0.8)",  # Bronze
                "index": 0,
                "label": "Shogun (2000)",
                "x": 0.05,
                "y": 0.1,
            },
            "2002_medieval": {
                "color_code": "rgba(0, 0, 139, 0.8)",  # Deep Blue
                "index": 1,
                "label": "Medieval (2002)",
                "x": 0.10,
                "y": 0.5,
            },
            "2004_rome": {
                "color_code": "rgba(255, 0, 0, 0.8)",  # Red
                "index": 2,
                "label": "Rome (2004)",
                "x": 0.15,
                "y": 0.9,
            },
            "2006_medieval_2": {
                "color_code": "rgba(111, 115, 123, 0.8)",  # Steel Gray
                "index": 3,
                "label": "Medieval 2 (2006)",
                "x": 0.20,
                "y": 0.5,
            },
            "2009_empire": {
                "color_code": "rgba(242, 133, 0, 0.8)",  # Tangerine
                "index": 4,
                "label": "Empire (2009)",
                "x": 0.25,
                "y": 0.1,
            },
            "2010_napoleon": {
                "color_code": "rgba(65, 105, 225, 0.8)",  # Royal Blue
                "index": 5,
                "label": "Napoleon (2010)",
                "x": 0.30,
                "y": 0.5,
            },
            "2011_shogun_2": {
                "color_code": "rgba(255, 215, 0, 0.8)",  # Gold
                "index": 6,
                "label": "Shogun 2 (2011)",
                "x": 0.35,
                "y": 0.9,
            },
            "2012_fall_of_the_samurai": {
                "color_code": "rgba(255, 183, 197, 0.8)",  # Cherry Blossom Pink
                "index": 7,
                "label": "Fall of the Samurai (2012)",
                "x": 0.40,
                "y": 0.5,
            },
            "2013_rome_2": {
                "color_code": "rgba(139, 0, 0, 0.8)",  # Dark Red
                "index": 8,
                "label": "Rome 2 (2013)",
                "x": 0.45,
                "y": 0.1,
            },
            "2015_attila": {
                "color_code": "rgba(53, 94, 59, 0.8)",  # Hunter Green
                "index": 9,
                "label": "Attila (2015)",
                "x": 0.50,
                "y": 0.5,
            },
            "2016_warhammer": {
                "color_code": "rgba(143, 0, 255, 0.8)",  # Violet
                "index": 10,
                "label": "Warhammer 1 (2016)",
                "x": 0.55,
                "y": 0.9,
            },
            "2017_warhammer_2": {
                "color_code": "rgba(147, 112, 219, 0.8)",  # Medium Purple
                "index": 11,
                "label": "Warhammer 2 (2017)",
                "x": 0.60,
                "y": 0.5,
            },
            "2018_thrones_of_britannia": {
                "color_code": "rgba(175, 111, 9, 0.8)",  # Caramel
                "index": 12,
                "label": "Thrones of Britannia (2018)",
                "x": 0.65,
                "y": 0.1,
            },
            "2019_three_kingdoms": {
                "color_code": "rgba(0, 168, 107, 0.8)",  # Jade Green
                "index": 13,
                "label": "Three Kingdoms (2019)",
                "x": 0.70,
                "y": 0.5,
            },
            "2020_troy": {
                "color_code": "rgba(70, 130, 180, 0.8)",  # Aegean Blue
                "index": 14,
                "label": "Troy (2020)",
                "x": 0.75,
                "y": 0.9,
            },
            "2022_warhammer_3": {
                "color_code": "rgba(106, 13, 173, 0.8)",  # True Purple
                "index": 15,
                "label": "Warhammer 3 (2022)",
                "x": 0.80,
                "y": 0.5,
            },
            "2023_pharaoh": {
                "color_code": "rgba(210, 170, 109, 0.8)",  # Sand Yellow
                "index": 16,
                "label": "Pharaoh (2023)",
                "x": 0.85,
                "y": 0.1,
            },
            # Special "none" game for transition to show last worked on
            "none": {
                "color_code": "rgba(0, 0, 0, 0.8)",  # Black
                "index": 17,
                "label": "None / TBD",
                "x": 0.95,
                "y": 0.5,
                "annotation_x": 0.825,
                "annotation_y": 0.55,
            },
        }

        self.developer_contributions = {}
        self.contribution_counts = {}
        self.developer_attrition = {}
        self.num_games_evaluated = 0

    def sanitize_name(self, name: str) -> str:
        """
        Sanitizes a name so that it doesn't include clearly defined nicknames or parenthetical notes.
        Also attempts to map together discrete developer entries which are obviously related.

        Args:
            name (str): The name to sanitize

        Returns:
            str: The sanitized name
        """
        sanitized_name = ' '.join(re.sub(r"\([^)]*\)", '', re.sub(r"'\w+'", '', name)).split())
        return self.mapped_developers.get(sanitized_name, sanitized_name)

    def shogun_is_as_shogun_does(self) -> None:
        """
        The Shogun: Total War game files didn't appear to have an explicit credits file in text
        or XML format (but maybe I just missed it). As such, these credits are hand coded from
        referencing screenshots taken of the credits screen in-game since the team was relatively
        small back then, so pulling in pytesseract felt like overkill.

        Creates a JSON file with keys corresponding to role and values lists of developer names.
        """
        game_credits = {
            "Project Director": ["Mike Simpson"],
            "Programming": ["A.P. Taglione", "Matteo Sartori", "Shane O'Brien", "Dan Parkes",
                            "John McFarlane", "Dan Laviers", "Dan Triggs", "Charlie Dell",
                            "Joss Adley", "Howard Rayner", "Greg Alston", "Ester Reeve",
                            "Nick Smith", "Al Hope", "Nick Tresadern", "Jude Bond"],
            "Project Management": ["Mike Simpson", "Luci Black", "Ross Manton", "Tim Ansell"],
            "Q.A. Manager": ["Graham Axford"],
            "Testers": ["Chris Morphew", "Jeff Woods", "Jason Ong", "James Buckle"],
            "Historical Research": ["Stephen Turnbull"],
            "Dialog & Additional Content": ["Mike Brunton"],
            "Scenario Editing": ["Tony Sinclair"],
            "Lead Technician": ["Alan Ansell"],
            "Editing & Processing": ["Greg Alston", "Leonor Juarez"],
            "Motion Capture Actors": ["Angela Kase", "Emmanuel Levi", "Daley Chaston"],
            "Music": ["Jeff van Dyck"],
            "Sound Effects": ["Sam Spanswick", "Karl Learmont", "Jeff van Dyck"],
            "Movie Post-Production": ["Jeff van Dyck", "Angela Somerville"],
            "Audio Director": ["Jeff van Dyck"],
            "Casting & Voice Production": ["Phillip Morris"],
            "Voice Actors": ["Togo Igawa", "Eiji Kusuhara", "Daniel York", "Simon Greenall", "Kentaro Suyami"],
            "Public Relations": ["Jason Fitzgerald", "Cathy Campos"]
        }

        # Exclude roles
        game_credits = {k: v for k, v in game_credits.items() if k not in self.exclude_roles}

        # Sort the names in the lists alphabetically
        for role in game_credits:
            game_credits[role] = sorted(game_credits[role])

        # Output processed roles and developers
        with open(os.path.join("processed", "2000_shogun_credits.json"), "w", encoding="utf-16") as game_credits_json:
            json.dump(game_credits, game_credits_json, indent=4)

    def medieval_is_as_medieval_does(self) -> None:
        """
        The Medieval: Total War files do have an explicit credits text file, but it doesn't match the more
        sanely parseable format of the later Rome/M2 text files. It's definitely still parseable, but since
        there were so few names it was simpler to just hand code them here than write a one-off parser logic.

        Creates a JSON file with keys corresponding to role and values lists of developer names.
        """
        game_credits = {
            "Project Director": ["Mike Simpson"],
            "Lead Programmer": ["A.P. Taglione"],
            "Battle Logic & AI": ["R.T. Smith"],
            "FE Core, Strategy Map UI & Infrastructure": ["Shane O'Brien"],
            "Multiplayer, FE, Castle AI": ["Gil Jaysmith"],
            "Historical Campaigns, FE, Agents, Mercs": ["Dan Parkes"],
            "Strategy Map AI": ["Ting Li"],
            "Fleets, Glory Goals and Tutorial": ["Matteo Sartori"],
            "VnV's & Heroes": ["Mike Simpson"],
            "Battle Tutorials & Pathfinding": ["Dan Triggs"],
            "Battle UI": ["John McFarlane"],
            "Events and Installation": ["Melvyn Quek"],
            "UI Graphics & Maps": ["Joss Adley"],
            "Battle Graphics, Textures & Maps": ["Howard Rayner"],
            "Event & PR Drawings, Textures & Maps": ["Nick Smith"],
            "Portraits, PR Art & Strategy Map": ["Ester Reeve"],
            "Glory Art and Buildings": ["Irina Rohvarger"],
            "Portraits, Textures & Maps": ["Greg Alston"],
            "Writing": ["Mike Brunton", "Graeme Davis"],
            "Producer": ["Luci Black"],
            "Product Evangelist": ["Michael de Plater"],
            "Executive Producer": ["Tim Ansell"],
            "QA Manager": ["Graham Axford"],
            "Testers": ["Jeff Woods", "James Buckle", "Chris Morphew", "Ken Rafferty"],
            "Intro and PR Art": ["Alistair Hope", "Jude Bond"],
            "Programming": ["Richard Broadhurst", "Dan Laviers"],
            "Manual": ["Mike Brunton"],
            "Webmaster": ["Richie Skinner"],
            "PR & Marketing": ["Ian Roxburgh", "Cathy Campos"],
            "Tools": ["Richard Broadhurst", "Mark Milton", "Nick Tresadern"],
            "Additional Content": ["Tim Ansell", "Ross Manton"],
            "Assistant Producer & Catering": ["Chris Gambold"],
            "Consultant on Muslim Culture": ["Kaushar Tai"],
            "Music & Sound Effects": ["Jeff van Dyck"],
            "Additional Music": ["Richard Vaughan", "Saki Kaskas"],
            "Additional Sound Effects": ["Richard Vaughan", "Nathan McGuiness", "Karl Learmont", "Sam Spanswick"],
            "Trumpet Fanfares": ["Dale Richardson"],
            "Casting and Voice Production": ["Phillip Morris"],
            "Voices": ["Sean Pertwee", "Sulayman Al-Bassam", "Boris Sosna", "Nadim Sawalha"],
            "Audio Scripts": ["Mike Brunton"],
        }

        # Exclude roles
        game_credits = {k: v for k, v in game_credits.items() if k not in self.exclude_roles}

        # Sort the names in the lists alphabetically
        for role in game_credits:
            game_credits[role] = sorted(game_credits[role])

        # Output processed roles and developers
        with open(os.path.join("processed", "2002_medieval_credits.json"), "w", encoding="utf-16") as game_credits_json:
            json.dump(game_credits, game_credits_json, indent=4)

    def parse_txt_format(self, game: str, parsed: List[str]) -> None:
        """
        Parse through the txt credits format used for Rome and Medieval 2, excluding some sections,
        roles, and entities which don't constitute developers of Creative Assembly with clearly defined
        job functions.

        Creates a JSON file with keys corresponding to role and values lists of developer names.

        Args:
            game (str): The name of the game + year (e.g. 2004_rome), for naming the output file
            parsed (List[str]): List of lines in the text file
        """
        current_role = None
        section_enabled = False
        game_credits = {}
        for line in parsed:
            # sections and roles start with _
            if line.startswith("_"):
                role_or_section = line[1:].strip()
                # If this is an included section, mark section enabled but wait for a role
                if role_or_section in self.include_sections:
                    section_enabled = True
                    current_role = None
                # If this is an excluded section, mark section disabled and wait for next section
                elif role_or_section in self.exclude_sections:
                    section_enabled = False
                    current_role = None
                # If this is a role we want to skip, keep looking
                elif role_or_section in self.exclude_roles:
                    current_role = None
                # Otherwise, it's a role we want so if the section is enabled set current role
                elif section_enabled:
                    current_role = role_or_section
            # Names, text, and empty lines within enabled sections/roles
            elif current_role and section_enabled:
                # Break out multiple names if more than one column
                if "|" in line:
                    names = {self.sanitize_name(name) for name in line.strip().split("|")}
                else:
                    names = set([self.sanitize_name(line.strip())])

                for name in names:
                    if name and name not in self.exclude_entities:
                        if current_role not in game_credits:
                            game_credits[current_role] = set()

                        # Add found names if not empty and not an explicitly excluded entity
                        game_credits[current_role].add(name)

        # Replace sets with sorted lists which are JSON serializable
        for role in game_credits:
            game_credits[role] = sorted(list(game_credits[role]))

        # Output processed roles and developers
        with open(os.path.join("processed", f"{game}_credits.json"), "w", encoding="utf-16") as game_credits_json:
            json.dump(game_credits, game_credits_json, indent=4)

    def parse_xml_v1_format(self, game: str, parsed: BeautifulSoup) -> None:
        """
        Parse through the XML v1 credits format used until Attila (+ ToB), excluding some sections,
        roles, and entities which don't constitute developers of Creative Assembly with clearly defined
        job functions.

        Creates a JSON file with keys corresponding to role and values lists of developer names.

        Args:
            game (str): The name of the game + year (e.g. 2004_rome), for naming the output file
            parsed (BeautifulSoup): A bs4 object representation of the XML contents
        """
        # All of the v1 XML format share the fact that... they aren't the v2 XML format. Apart from
        # that, they use the <line> element for both job roles and names. The only shared
        # distinguishing element appears to be font size, the job roles and sections are typically
        # larger than the names. However, the font sizes change between the different games, so we have
        # to explicitly call out which font sizes to look for to distinguish roles from names.
        #
        # Additionally, some small edits were made to the stock files so that we could handle only
        # single sizes per type here, which are noted in the README. The edits will need to be applied
        # for this logic to work.
        game_categorization = {
            "2009_empire": {"developer": "18", "role": "22", "section": "22", "stop_at": "SEGA Technical Group"},
            "2010_napoleon": {"developer": "18", "role": "22", "section": "22", "stop_at": "English Language Voice Cast:"},
            "2011_shogun_2": {"developer": "18", "role": "22", "section": "22", "stop_at": "English & Japanese Voice Production"},
            "2012_fall_of_the_samurai": {"developer": "18", "role": "22", "section": "22", "stop_at": "English & Japanese Voice Production"},
            "2013_rome_2": {"developer": "18", "role": "22", "section": "22", "stop_at": "SEGA Europe"},
            "2015_attila": {"developer": "12", "role": "18", "section": "18", "stop_at": "English Actors"},
            "2018_thrones_of_britannia": {"developer": "12", "role": "16", "section": "18", "stop_at": "SEGA"},
        }

        # We create sections to store the parsed credits. Most games are 1:1 but for
        # Shogun 2 the credits also include Fall of the Samurai. Since unlike other expansions/DLC
        # this was considered a standalone Saga game equivocal to Troy/ToB we do want to consider
        # this an independent game for tracking purposes.
        game_credits = {game: {}}
        if game == "2011_shogun_2":
            game_credits["2012_fall_of_the_samurai"] = {}

        developer_font = game_categorization[game]["developer"]
        role_font = game_categorization[game]["role"]
        section_font = game_categorization[game]["section"]
        stop_section = game_categorization[game]["stop_at"]
        # Start by including since no upfront section in some files
        section_enabled = True
        current_role = None
        current_game = game
        continue_processing = True
        wait_for_next_game = False
        for line in parsed.select("credits > page > line"):
            # We either process the line as a whole or left/right sections
            elements = [line]
            left = line.find("left", recursive=False)
            right = line.find("right", recursive=False)
            if left or right:
                elements = [elem for elem in [left, right] if elem]

            for element in elements:
                font_size = element.get("fontsize", "")
                text = re.sub(r"\s+", " ", element.text.strip())

                # The special "38" font size for Shogun 2 is used to split FotS from Shogun 2
                if game == "2011_shogun_2" and font_size == "38":
                    if text == "- Fall of the Samurai -":
                        current_game = "2012_fall_of_the_samurai"
                        wait_for_next_game = False
                    else:
                        current_game = "2011_shogun_2"
                        wait_for_next_game = False
                    break

                # Only Shogun 2 FotS should set this, as an alternative to fully exiting
                if wait_for_next_game:
                    continue

                # First we check if it's a section. In most of the v1 files roles and
                # sections aren't distinguishable by metadata, so we rely on matching
                # it to one of the explicit sections in include/exclude lists. If it
                # wasn't added to one of those then we fall through and consider it a role.
                if font_size == section_font:
                    # We found the stop section, the rest of the file can be skipped
                    if text == stop_section:
                        # FotS needs a special case, it comes first including all the sections
                        # after its stop_at point, but we still want to process Shogun 2
                        if current_game == "2012_fall_of_the_samurai":
                            wait_for_next_game = True
                        else:
                            continue_processing = False
                        break

                    # We want to include this section, enable parsing roles/developers
                    if text in self.include_sections:
                        section_enabled = True
                        current_role = None
                        break

                    # We don't want to include this section, disable parsing roles/developers
                    if text in self.exclude_sections:
                        section_enabled = False
                        current_role = None
                        break

                # Only process roles/developers if we're in an enabled section
                if section_enabled:
                    # If we're looking at a role then we want to set current role
                    if font_size == role_font:
                        if text in self.exclude_roles:
                            current_role = None
                        else:
                            current_role = text
                    # Otherwise it should be an developer, so handle adding name to appropriate role
                    elif current_role and font_size == developer_font:
                        # Break out multiple names if more than one column
                        if " - " in text:
                            names = {self.sanitize_name(name) for name in text.split(" - ")}
                        else:
                            names = set([self.sanitize_name(text)])

                        for name in names:
                            if name and name not in self.exclude_entities:
                                if current_role not in game_credits[current_game]:
                                    game_credits[current_game][current_role] = set()

                                game_credits[current_game][current_role].add(name)

            # We saw the role we want to stop at, the rest of the file are roles we don't
            # want to include in the data set
            if not continue_processing:
                break

        for game_name, game_data in game_credits.items():
            # Replace sets with sorted lists which are JSON serializable
            for role in game_data:
                game_data[role] = sorted(list(game_data[role]))

            # Output processed roles and developers
            with open(os.path.join("processed", f"{game_name}_credits.json"), "w", encoding="utf-16") as game_credits_json:
                json.dump(game_data, game_credits_json, indent=4)

    def parse_xml_v2_format(self, game: str, parsed: BeautifulSoup) -> None:
        """
        Parse through the XML v1 credits format used since Warhammer, excluding some sections,
        roles, and entities which don't constitute developers of Creative Assembly with clearly defined
        job functions.

        Creates a JSON file with keys corresponding to role and values lists of developer names.

        Args:
            game (str): The name of the game + year (e.g. 2004_rome), for naming the output file
            parsed (BeautifulSoup): A bs4 object representation of the XML contents
        """
        game_categorization = {
            "2016_warhammer": {"stop_at": "Audio (External)"},
            "2017_warhammer_2": {"stop_at": "Audio (External)"},
            "2019_three_kingdoms": {"stop_at": "Audio (External) - Sound, Dialogue and Music"},
            "2020_troy": {"stop_at": "Sound Department (External)"},
            "2022_warhammer_3": {"stop_at": "AUDIO (External)"},
            "2023_pharaoh": {"stop_at": "Voice Over Artists (External)"},
        }

        game_credits = {}
        stop_section = game_categorization[game]["stop_at"]
        # Start by including since no upfront section in some files
        section_enabled = True
        current_role = None
        continue_processing = True
        for line in parsed.select("credits > page > line"):
            # We either process the line as a whole or left/right sections
            elements = [line]
            left = line.find("left", recursive=False)
            right = line.find("right", recursive=False)
            if left or right:
                elements = [elem for elem in [left, right] if elem]

            for element in elements:
                style = element.get("style", "")
                text = re.sub(r"\s+", " ", element.text.strip())

                # Header and section are intechangeably used to define sections and roles
                # so we can't assume they map 1:1 and have to check for both cases for either
                if style in ["header", "subheader"]:
                    # We found the stop section, the rest of the file can be skipped
                    if text == stop_section:
                        continue_processing = False
                        break

                    # We want to include this section, enable parsing roles/developers
                    if text in self.include_sections:
                        section_enabled = True
                        current_role = None
                        break

                    # We don't want to include this section, disable parsing roles/developers
                    if text in self.exclude_sections:
                        section_enabled = False
                        current_role = None
                        break

                    # If it's not a defined section then we assume it's a role, so check
                    # the exclude list and if it's not there then set the current role so that we
                    # start including developers for this role
                    if not section_enabled or text in self.exclude_roles:
                        current_role = None
                    else:
                        current_role = text
                elif style in ["text", "text_pair"]:
                    # These should both represent developers, so add to role if the current role is
                    # filled (it's one we're including)
                    if current_role and text and text not in self.exclude_entities:
                        if current_role not in game_credits:
                            game_credits[current_role] = set()

                        game_credits[current_role].add(self.sanitize_name(text))
                # No need to work with the formatting lines so skip to next
                elif style in ["break", "image"]:
                    pass
                # Shouldn't hit this case on any files that existed pre-Pharaoh, if new formatting
                # is added that still largely conforms to XML v2 the above cases should be amended
                else:
                    print(f"Error: No case for style {style} in v2 XML parser, needs support added.")

            # We saw the role we want to stop at, the rest of the file are roles we don't
            # want to include in the data set
            if not continue_processing:
                break

        # Replace sets with sorted lists which are JSON serializable
        for role in game_credits:
            game_credits[role] = sorted(list(game_credits[role]))

        # Output processed roles and developers
        with open(os.path.join("processed", f"{game}_credits.json"), "w", encoding="utf-16") as game_credits_json:
            json.dump(game_credits, game_credits_json, indent=4)

    def process_txt_credits(self) -> None:
        """
        Go through the games sub-folders and find any that use the standard txt credits
        format used by Rome and Medieval 2 and pass the file contents and name to parser.
        """
        # TXT credits files
        txt_credits = sorted(glob.glob(os.path.join("games", "**", "credits.txt")))

        for txt_file in txt_credits:
            game = txt_file.split(os.sep)[-2]

            # The file appears to be UTF-16 rather than UTF-8
            with open(txt_file, "r", encoding="utf-16") as file:
                parsed = file.readlines()

            # Technically the medieval file shouldn't match since its file is uppercase,
            # but on the off-chance it was renamed explicitly skip it. I don't think there
            # is a shogun file, but if someone finds one skip that too. Both are handled
            # explicitly.
            if game not in ["2000_shogun", "2002_medieval"]:
                self.parse_txt_format(game, parsed)

    def process_xml_credits(self) -> None:
        """
        Go through the games sub-folders and find any that use the v1 or v2 xml credits
        format used from Empire onwards and pass the file contents and name to parser.
        """
        # XML credits files
        xml_credits = sorted(glob.glob(os.path.join("games", "**", "credits.xml")))

        for credits_file in xml_credits:
            game = credits_file.split(os.sep)[-2]

            # Turn XML into a beautiful pot of soup
            with open(credits_file, "r", encoding="utf-8") as file:
                parsed = BeautifulSoup(file, features="lxml-xml")

            # There are 2 different XML formats, one used from Empire through Attila (+ ToB)
            # and another used from Warhammer through Warhammer 3 (chronologically). We could
            # hardcode this or use multiple heuristics to detect, one which seems to work is
            # all v2 XML have a style property on the first line, and none of the v1 files do.
            xml_format = "v2"
            for line in parsed.select("credits > page > line", limit=1):
                if not line.get("style", ""):
                    xml_format = "v1"

            # Call parser depending on detected format
            if xml_format == "v2":
                self.parse_xml_v2_format(game, parsed)
            else:
                self.parse_xml_v1_format(game, parsed)

    def populate_developer_contributions(self) -> None:
        """
        Goes through all of the processed credits files with entries grouped by role and pulls them
        into developer contributions map where it's grouped by developer name with a chronological
        list of roles.
        """
        # JSON processed credits files
        processed_credits = sorted(glob.glob(os.path.join("processed", "*_credits.json")))
        self.num_games_evaluated = len(processed_credits)

        for i, credits_file in enumerate(processed_credits):
            game = os.path.splitext(credits_file.split(os.sep)[-1].replace("_credits", ""))[0]

            with open(credits_file, "r", encoding="utf-16") as credits_json:
                credits_parsed = json.load(credits_json)

            for role, developers in credits_parsed.items():
                for developer in developers:
                    if developer not in self.developer_contributions:
                        self.developer_contributions[developer] = {}

                    if game not in self.developer_contributions[developer]:
                        self.developer_contributions[developer][game] = []

                    self.developer_contributions[developer][game].append(role)

        self.developer_contributions = dict(sorted(self.developer_contributions.items()))
        print(f"Unique Developer Contributions: {len(self.developer_contributions.keys())}")

        with open(os.path.join("processed", "developer_contributions.json"), "w", encoding="utf-16") as contributions_json:
            json.dump(self.developer_contributions, contributions_json, indent=4)

    def generate_interesting_statistics(self) -> None:
        """
        Generate various interesting statistics.

        Contribution Counts:
            Goes through developer contributions and buckets into counts based on number of games contributed to.
        Recent Contributors:
            Counts the number of developers who've contributed to something Three Kingdoms or later.
        Remaining Old Timers:
            Counts the number of developers who contributed to Medieval 2 or earlier, and to Three Kingdoms or later.
        """
        self.contribution_counts = {k: {"count": 0, "developers": []} for k in range(self.num_games_evaluated, 0, -1)}
        self.developer_attrition = {k: {"total": 0, "final": 0} for k in self.game_metadata}
        old_timers_remaining = 0
        recent_contributors = 0
        for developer, contributions in self.developer_contributions.items():
            # Tabulate the number of contributions and add to contribution count bucket
            num_contributions = len(contributions.keys())
            self.contribution_counts[num_contributions]["count"] += 1
            self.contribution_counts[num_contributions]["developers"].append(developer)

            # Check for old timers, people who contributed to a game before Empire and also after ToB
            contributed_up_to_medieval_2 = False
            contributed_after_three_kingdoms = False
            for game in contributions.keys():
                self.developer_attrition[game]["total"] += 1
                final_game = game
                if game in ["2000_shogun", "2002_medieval", "2004_rome", "2006_medieval_2"]:
                    contributed_up_to_medieval_2 = True
                elif game in ["2019_three_kingdoms", "2020_troy", "2022_warhammer_3", "2023_pharaoh"]:
                    contributed_after_three_kingdoms = True

            self.developer_attrition[final_game]["final"] += 1

            if contributed_up_to_medieval_2 and contributed_after_three_kingdoms:
                old_timers_remaining += 1
                recent_contributors += 1
            elif contributed_after_three_kingdoms:
                recent_contributors += 1

        print(f"Recent Contributors: {recent_contributors}")
        print(f"Remaining Old Timers: {old_timers_remaining} (% of Recent Contributors: {round((old_timers_remaining / recent_contributors) * 100, 2)}%)")

        with open(os.path.join("processed", "contribution_counts.json"), "w", encoding="utf-16") as contributions_counts_json:
            json.dump(self.contribution_counts, contributions_counts_json, indent=4)

    def generate_developer_flow_diagram(self) -> None:
        """
        Generate a Sankey diagram showing developer flow between games chronologically.
        """
        # Generate the buckets and volumes to feed to sankey diagram
        transition_buckets = {}
        for contributions in self.developer_contributions.values():
            previous_contribution_index = None
            for contribution in contributions.keys():
                current_contribution_index = self.game_metadata[contribution]["index"]
                if previous_contribution_index is not None:
                    transition = f"{previous_contribution_index}, {current_contribution_index}"
                    if transition not in transition_buckets:
                        transition_buckets[transition] = 0
                    transition_buckets[transition] += 1
                previous_contribution_index = current_contribution_index

            transition = f"{previous_contribution_index}, -1"
            if transition not in transition_buckets:
                transition_buckets[transition] = 0
            transition_buckets[transition] += 1

        # Now process the buckets to put them in the format used by the Sankey diagram, which requires that the
        # source, target, and volume of transitions from source->target be specified at a shared index in discrete lists
        source_colors = [game["color_code"] for game in self.game_metadata.values()]
        labels = [f'<b>{game["label"]}</b>' for game in self.game_metadata.values()]
        sources = []
        targets = []
        values = []
        colors = []
        for transition, volume in transition_buckets.items():
            source, target = transition.split(", ")
            source = int(source)
            target = int(target)
            values.append(volume)
            sources.append(source)
            colors.append(source_colors[source])
            if target >= 0:
                targets.append(target)
            else:
                targets.append(self.game_metadata["none"]["index"])

        with open(os.path.join("processed", "transition_buckets.json"), "w", encoding="utf-8") as transition_buckets_json:
            json.dump(dict(sorted(transition_buckets.items())), transition_buckets_json, indent=4)

        fig = go.Figure(
            data=[
                go.Sankey(
                    valueformat=".",
                    valuesuffix=" developers",
                    node={
                        "pad": 15,
                        "thickness": 15,
                        "line": {"color": "black", "width": 0.5},
                        "label": labels,
                        "color": source_colors,
                        "x": [game["x"] for game in self.game_metadata.values()],
                        "y": [game["y"] for game in self.game_metadata.values()],
                    },
                    link={
                        "source": sources,
                        "target": targets,
                        "value": values,
                        # The shown name of the link
                        "label": ["" for _ in range(len(sources))],
                        "color": colors,
                    },
                )
            ]
        )

        fig.write_html(os.path.join("visualizations", "tw_developer_flow.html"))
        fig.write_html("index.html")

    def generate_recent_game_overlap_venn_diagram(self) -> None:
        """
        Generate a Venn diagram showing overlap of developers contributing to the 3 most recent titles.
        """
        # Generate the buckets and volumes to feed to venn diagram
        circles = {
            "3k_wh3_ph": 0,
            "3k_wh3": 0,
            "3k_ph": 0,
            "3k": 0,
            "wh3_ph": 0,
            "wh3": 0,
            "ph": 0,
        }
        for contributions in self.developer_contributions.values():
            if "2019_three_kingdoms" in contributions:
                if "2022_warhammer_3" in contributions:
                    if "2023_pharaoh" in contributions:
                        circles["3k_wh3_ph"] += 1
                    else:
                        circles["3k_wh3"] += 1
                elif "2023_pharaoh" in contributions:
                    circles["3k_ph"] += 1
                else:
                    circles["3k"] += 1
            elif "2022_warhammer_3" in contributions:
                if "2023_pharaoh" in contributions:
                    circles["wh3_ph"] += 1
                else:
                    circles["wh3"] += 1
            elif "2023_pharaoh" in contributions:
                circles["ph"] += 1

        # Extracting values in the order expected by venn3 function
        # The order is: (Abc, aBc, ABc, abC, AbC, aBC, ABC)
        values = (
            circles['3k'],
            circles['wh3'],
            circles['3k_wh3'],
            circles['ph'],
            circles['3k_ph'],
            circles['wh3_ph'],
            circles['3k_wh3_ph']
        )

        # Colors
        color_3k = (0/255, 168/255, 107/255)
        color_wh3 = (106/255, 13/255, 173/255)
        color_ph = (210/255, 170/255, 109/255)

        # Creating the Venn diagram
        venn_diagram = venn3(subsets=values, set_labels=("Three Kingdoms", "Warhammer 3", "Pharaoh"))
        plt.title(label="Developer Contribution Overlap", fontsize=20)

        # Set the colors for individual circles
        venn_diagram.get_patch_by_id('100').set_color(color_3k)
        venn_diagram.get_patch_by_id('010').set_color(color_wh3)
        venn_diagram.get_patch_by_id('001').set_color(color_ph)

        # Blend the colors for the overlapping regions
        venn_diagram.get_patch_by_id('110').set_color([(c1+c2)/2 for c1, c2 in zip(color_3k, color_wh3)])
        venn_diagram.get_patch_by_id('101').set_color([(c1+c2)/2 for c1, c2 in zip(color_3k, color_ph)])
        venn_diagram.get_patch_by_id('011').set_color([(c1+c2)/2 for c1, c2 in zip(color_wh3, color_ph)])
        venn_diagram.get_patch_by_id('111').set_color([(c1+c2+c3)/3 for c1, c2, c3 in zip(color_3k, color_wh3, color_ph)])

        # Save to PNG
        plt.savefig(os.path.join("visualizations", "3k_wh3_ph_overlap.png"))

    def generate_contribution_counts_bar_chart(self) -> None:
        """
        Generate a bar chart showing developers by number of games contributed to.
        """
        counts = {k: v["count"] for k, v in self.contribution_counts.items()}

        # Sorting data based on keys
        sorted_keys = sorted(counts.keys())
        sorted_values = [counts[key] for key in sorted_keys]

        # Create bar chart
        fig = go.Figure(data=[go.Bar(x=sorted_keys, y=sorted_values)])
        fig.update_layout(
            title={
                "text": "Distribution of Developers by Number of Games Contributed To",
                "font_size": 20,
            },
            xaxis_title="Number of Games Contributed To",
            yaxis_title="Number of Developers",
            xaxis={
                "tickmode": 'linear',
                "tick0": 1,
                "dtick": 1
            }
        )
        fig.write_image(os.path.join("visualizations", "tw_contribution_counts.png"))

    def generate_developer_attrition_bar_chart(self) -> None:
        """
        Generate a bar chart showing developer attrition relative to total contributors for each game.
        """
        # We exclude recent games since it hasn't been long enough to assume developers
        # aren't working on another project in development, as well as the 'none' category
        exclude_games = ["2019_three_kingdoms", "2020_troy", "2022_warhammer_3", "2023_pharaoh", "none"]
        counts = {k: ((v["final"] / v["total"]) * 100) for k, v in self.developer_attrition.items() if k not in exclude_games}

        # Sorting data based on keys
        sorted_keys = sorted(counts.keys())
        sorted_values = [counts[key] for key in sorted_keys]

        # Create bar chart
        fig = go.Figure(data=[go.Bar(x=sorted_keys, y=sorted_values)])
        fig.update_layout(
            title={
                "text": "Developer Attrition Throughout The Series",
                "font_size": 20,
            },
            xaxis_title="Final Game Contributed To",
            yaxis_title="Percentage of Total Contributors",
        )
        fig.write_image(os.path.join("visualizations", "tw_developer_attrition.png"))

if __name__ == "__main__":
    # Create the JSON output and visualizations sub-directories if not present
    os.makedirs("processed", exist_ok=True)
    os.makedirs("visualizations", exist_ok=True)

    # Create the contributions object
    contributions = TotalWarDeveloperContributions()

    # Process all of the credits files to generate JSON outputs
    contributions.shogun_is_as_shogun_does()
    contributions.medieval_is_as_medieval_does()
    contributions.process_txt_credits()
    contributions.process_xml_credits()

    # Populate the developer contributions map
    contributions.populate_developer_contributions()

    # Generate statistics
    contributions.generate_interesting_statistics()

    # Generate visualizations
    contributions.generate_developer_flow_diagram()
    contributions.generate_recent_game_overlap_venn_diagram()
    contributions.generate_contribution_counts_bar_chart()
    contributions.generate_developer_attrition_bar_chart()
