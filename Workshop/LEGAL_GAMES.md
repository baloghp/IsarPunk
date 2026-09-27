# Legal Games for the Batocera Finale

**Purpose:** legally safe candidates for an IsarPunk Batocera demo. Use these instead of commercial ROM packs.

**Validation date:** 2026-09-19  
**Rule for the workshop:** keep only games where the developer/project page gives a legal download, source license, or official release link. Do not use random ROM archives.

## Shortlist

| Game | Platform | Why it is usable | Validated source / download URL | Batocera note |
|------|----------|------------------|----------------------------------|---------------|
| **Petris** | Game Boy Color | Project page identifies it as homebrew, links official downloads/play-online, and GitHub reports MIT licenses. | Source: <https://github.com/bbbbbr/Petris> · Official download page: <https://bbbbbr.itch.io/petris> | Strong workshop fit: cute, legible, puzzle-based. Download from the official page, not a ROM archive. |
| **Tobu Tobu Girl Deluxe** | Game Boy / Game Boy Color | Source code is MIT; assets are CC BY 4.0; README says binaries are provided through the official itch.io page. | Source: <https://github.com/SimonLarsen/tobutobugirl-dx> · Official binary page: <https://tangramgames.itch.io/tobutobugirldx> | Best “wow” candidate. Validate the current itch download manually before adding the ROM to the demo image. |
| **Super Princess' 2092 Exodus** | Game Boy | gbdev lists it as homebrew; the GitHub project identifies it as a GBJAM platformer and links an official binary page. | Source: <https://github.com/Zal0/Super-Princess-2092-Exodus> · Official binary page: <https://sergeeo.itch.io/super-princess-2092-exodus> | Best Mario-like legal candidate found so far: side-scrolling platformer energy without Mario assets. Manually validate the itch download before imaging. |
| **Guns & Riders** | Game Boy | GitHub project is GPL-3.0 licensed and includes a `.gb` ROM in the repository. gbdev lists it as Game Boy homebrew. | Source/ROM repository: <https://github.com/kanfor/gunsridersgameboy> | Action-oriented option; test controls and content tone before using with younger students. |
| **Dino Boy** | Game Boy | MIT-licensed Game Boy port inspired by the open Chromium Dino game; source page documents manual build and project status. | Source: <https://github.com/rnegron/dino-gb> | Recognizable runner-game mechanic; likely build-from-source unless a prepared ROM from the repository works for your setup. |

## Backup / Build-From-Source Candidate

| Game | Platform | Why it is usable | Validated source URL | Batocera note |
|------|----------|------------------|----------------------|---------------|
| **Libbet and the Magic Floor** | Game Boy | README states it is free software under the zlib License. | <https://github.com/pinobatch/libbet> | Good legal backup, but expect to build it unless a release ROM is added later. |
| **2048-gb** | Game Boy | Source is zlib licensed and the README links an assembled ROM. | <https://github.com/Sanqui/2048-gb> | Legally clean but less exciting; keep as a controller/fallback test, not the finale. |

## Still Needed

- A legally clean kart/racing game with an official ROM or clear license. Do not use Mario, Mario Kart, or clone projects with Nintendo assets.
- Manual browser check for itch.io downloads, because automated validation may be blocked even when the official project page is legitimate.

## Demo-Pack Checklist

- [ ] Download only from the project/source links above.
- [ ] Keep a copy of this file with the Batocera image or USB prep notes.
- [ ] Record exact file names and versions after downloading.
- [ ] Do not add commercial console ROMs, “best of” ROM sets, BIOS dumps, or archive uploads with unclear rights.
- [ ] In the workshop, say: *“Batocera is free; the games still have to be legal.”*

## Suggested Finale Line

> This old laptop did not become waste. It became a tiny legal retro console, and the same machine could also become a Linux PC, a media box, a family computer, or a repair-shop project.