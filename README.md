# Total War Developer Contributions

## Overview

This repository contains a script used to parse the credits files of all Total War series games up until the release of Total War: Pharaoh in 2023, in order to use them in generating statistics and visualizations. This project was merely a curiosity and does not have an agenda, the data is the data but there are numerous caveats to its collection, sanitization, filtering, and processing. Any conclusions drawn from the data, statistics, or visualizations are up to interpretation.

## Data Source and Caveats

The source of all data are the credits from every Total War game. These were acquired in the following ways:

* Hand copied from screenshots for: Shogun
* Hand copied from `CREDITS.txt` loose file in the game files for: Medieval
* Parsed from `credits.txt` loose/unpacked file in the game files for: Rome, Medieval 2
* Parsed from `credits.xml` loose/unpacked file in the game files for: All other games

The actual credits files are not included in the source of this repository since they're technically still proprietary game files, but the data can be regenerated if a user has access to the game files of all games.

The parsing sections of this script could be adapted to create a different cross-cut of the raw credits data if desired. The specific cross-section that was interesting to me was developers of Creative Assembly proper (ie. not SEGA or external entities) who were in core technical game development roles. This is a bit of a nebulous distinction and is not indicative of value added, but the filters roughly align with:

* Included: Programming, Art, Design, Audio Engineering, Production, Writing, QA, (Some) Leadership
* Excluded: Data, Business Intelligence, IT, Infrastructure, PR, Marketing, Sales, Brand, Music, Voices, MoCap, Localization, Operations, Community, Content, Finance, Research, Special Thanks

In addition to the default statistics and visualizations being run on a curated data subset, the following caveats should be considered:

* Multiple people with the exact same name can't be handled well, so they would have been bundled together into one, doubly powerful, conjoined developer.
* People who go by nicknames or misspelling or etc may be counted twice. 116 determinable mappings were made from a scan of the data for common nicknames and misspellings with explicit remapping, but not all cases were likely covered. There's no good way to handle this since the credits aren't designed for deconflicting individuals, maybe in the future CA would be so kind as to include SSN/NIN/etc for all employees.
* People who had name changes due to marriage/divorce, same as above, will be counted twice or separately per game.
* Remasters like Rome Remastered from Feral Interactive are not included in the chronology.
* To the extent possible, SEGA employees are not counted as well as other external entities and outsourced roles, but it's not always perfectly clear cut so some may have slipped in, the rascals.
* Fall of the Samurai is treated as a full game, since it was explicitly pulled out as a Saga game. All other expansion/DLC/content teams are included in the total count of the respective base game since they're covered in the same credits file. These should include all the DLCs which had explicit credits subsections since I happened to own every DLC of every game at the time data was collected 10/2023 (except for Shadows of Change, even I haven't bought that, Kappa).
* The data implies nothing about the volume of contributions of an individual to a game. Someone who contributed thousands of hours of development time explicitly to that game is counted the same as someone who was mentioned (outside of Special Thanks) and only fixed a single bug or made some implicit contribution from a prior game. Maybe in the future CA would be so kind as to include Story Points accrued by each accredited individual.

## Statistics and Visualizations

All of the statistics and visualizations are against the curated subset described above, but could be re-run against any filters.

* Statistics
  * **Unique Contributing Developers:** 1,082
  * **Recent Contributors (3K and later):** 669
  * **Remaining Old Timers (Contributed to M2 or earlier and 3K or later):** 23
    * **% of Recent Contributors that are Old Timers:** 3.44%

### Total War Developer Flow

[HTML](visualizations/tw_developer_flow.html) | [PNG](visualizations/tw_developer_flow.png)

This sankey diagram attempts to show the flow of developers contributing to different games over time. A link between two games means that number of developers contributed to Game A and then their next contribution chronologically was to Game B. So if someone had contributed to every game, they'd be in pairwise connections between every game. The "None / TBD" category at the end is used to track that a developer has yet to contribute to another game after that one, which may mean they're working on an in-development project, left the company, or moved to a role that was excluded from the data set. It's a little messy but there are a lot of different transitions, I'd recommend viewing the HTML version which can be hovered over.

### Three Kingdoms / Warhammer 3 / Pharaoh Developer Overlap

[PNG](visualizations/3k_wh3_ph_overlap.png)

This venn diagram shows developers who contributed to only one of Three Kingdoms, Warhammer 3, or Pharaoh, as well as any combination thereof. At the time of creation these were the latest games developed by the Historical Main Team, Fantasy Main Team, and CA Sofia Team respectively, based on CA's characterization of how its development teams are segmented. The data does appear to corroborate this separation, with substantial numbers of developers only contributing to 1 of the 3 games, considerably more as a percentage of total than the ~20% attrition rate of each prior evaluated game.

### Total Contribution Counts

[PNG](visualizations/tw_contribution_counts.png)

This bar chart buckets developers based on the total number of games they've contributed to (in a role that wasn't excluded). With each game having multi-year development cycles, the much higher representation of short term contributors to long term contributors isn't particularly surprising. Similar data would be required from other studios to infer anything about worse or better retention rate than the industry norm. The individuals with the longest tenure by this metric were:

* 15 Games
  * Chris Gambold: Design/Writing
  * Mike Simpson: Creative Director
  * Nick Tresadern: Art / Art Direction
* 14 Games
  * Graham Axford: QA
  * Joss Adley: Art

### Developer Attrition

[PNG](visualizations/tw_developer_attrition.png)

This bar chart shows the percentage of developers who made their last contribution to each game relative to the total number of developers contributing to that game. This percentage has stayed remarkably consistent across all the games, hovering around 20% attrition. The data also shows the two anomalous scenarios, when CA moved from Medieval to Rome which entailed a large team expansion and subsequently the SEGA acquisition, and Medieval 2, developed by the CA Australia studio which was subsequently dissolved.

## Running the Script

### Data Acquisition and Sanitization

If you just want to use the pre-processed, pre-filtered data based on my personal criteria, that's stashed in `processed/developer_contributions.json`. If you comment out the following lines in the script before running it then it should use the cached file and be fine.

```
    # Process all of the credits files to generate JSON outputs
    #contributions.shogun_is_as_shogun_does()
    #contributions.medieval_is_as_medieval_does()
    #contributions.process_txt_credits()
    #contributions.process_xml_credits()

    # Populate the developer contributions map
    #contributions.populate_developer_contributions()
```

If you want to regenerate or filter the data differently, you'll need to grab the credits file from (almost) every Total War game, or else comment out sections of the script related to ones you can't collect. For the most part, these are loose files in the game installation folder in somewhere like `data/text`, but it varies. Exceptions:

* For Shogun/Medieval, the credits are hand coded and don't need to be reaquired.
* For Medieval 2, need to use the bundled unpacker tool to unpack `credits.txt`.
* For Empire/Napoleon/Shogun 2, need to use [RPFM](https://github.com/Frodo45127/rpfm) tool to open `main.pack` or `data.pack` and extract `credits.xml`.

These files need to be placed in the `games` sub-directory in an appropriately names sub-folder. The layout should look like:

* games/
  * 2004_rome/credits.txt
  * 2006_medieval_2/credits.txt
  * 2009_empire/credits.xml
  * 2010_napoleon/credits.xml
  * 2011_shogun_2/credits.xml
  * 2013_rome_2/credits.xml
  * 2015_attila/credits.xml
  * 2016_warhammer/credits.xml
  * 2017_warhammer_2/credits.xml
  * 2018_thrones_of_britannia/credits.xml
  * 2019_three_kingdoms/credits.xml
  * 2020_troy/credits.xml
  * 2022_warhammer_3/credits.xml
  * 2023_pharaoh/credits.xml

The following data sanitizations were applied before processing:

* Empire
  * Had a single `fontsize="24"` role entry, changed to `fontsize="22"`.
  * Removed a special character in the line for employee last name Fazenda.
* Thrones of Britannia
  * Had a – (U+2013) character a few places and lists encoding as "UTF-10" which isn't a supported encoding. Changed the character to just '-' (U+002d) and updated encoding to UTF-8.
  * Had a handful of `fontsize="14"` entries which are all job roles, changed to `fontsize="16"` to match the majority case.
  * Had some sections which were `fontsize="16"` instead of `fontsize="18"`. Didn't change all of these, but changed SEGA on line 515 to fontsize="18"` since it's used as the break point.
  * Some musicians used the same separator to their instrument as separator between employee names, deleted the instrument on lines 494-496.
  * Some employees had some sub-function note in parentheses after the name. Deleted anything in parentheses on lines 13, 38, 42, 65, 386, 388, and 636.
* All v2 XML (2016 onwards besides ToB)
  * These changes likely aren't necessary but VS Code was angry at these characters mirroring more commonly used varieties so just did a find-replace on both sets.
    * Find-replace '–' (U+2013) with '-' (U+002d).
    * Find-replace ' ' (U+00a0) with ' ' (U+0020).

### Setup

Install Python and setup/source a virtual environment, then:
```
pip install -r requirements.txt
```

### Run

```
python total_war_developer_contributions.py
```
