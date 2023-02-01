#!bin/python

from scraper import scraper
from sites.asura import asura as _asura
from sites.toonily import toonily as _toonily
from sites.mangareader import mangareader as _mangareader

import string
async def name():
    return __name__

async def test_notification():
    web = scraper()
    toonily = _toonily(web)
    asura = _asura(web)
    mangareader = _mangareader(web)

    result = await toonily.database.run("""SELECT DISTINCT title, name from manga where title is null;""")
    manga_name = []
    for name in result:
        for i in name:
            if i:
                manga_name.append(
                    i
                )

    title_name = [
        "heavenly-demon-instructor",
        "black-clover",
        "regressor-instruction-manual",
        "one-piece",
        "return-of-the-8th-class-magician",
        "the-constellation-that-returned-from-hell",
        "solo-max-level-newbie",
        "return-of-the-unrivaled-spear-knight",
        "the-max-level-hero-has-returned",
        "the-legend-of-the-northern-blade",
        "onepunch-man",
        "second-ranker",
        "a-returners-magic-should-be-special",
        "solo-spell-caster",
        "moonlight-sculptor",
        "a-different-class",
        "is-there-no-goddess-in-my-college",
        "king-of-the-night",
        "madam",
        "secret-class",
        "she-is-working-out",
        "that-time-i-got-reincarnated-as-a-slime",
        "the-rising-of-the-shield-hero",
        "darwins-game",
        "intern-haenyeo",
        "worlds-strongest-troll",
        "return-of-the-frozen-player",
        "my-school-life-pretending-to-be-a-worthless-person",
        "ill-be-taking-a-break-for-personal-reasons",
        "taming-master",
        "swordmasters-youngest-son",
        "the-archmage-returns-after-4000-years",
        "circles",
        "solo-leveling-hot"
    ]

    for i, title in enumerate(manga_name):
        result = await toonily.database.run(F"""UPDATE manga
        SET
        title = '{title_name[i]}'
        WHERE
        name = '{title}';
        """) 
    return manga_name