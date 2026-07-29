"""
liturgical_calendar.py

Holds:
  - Easter computation (so we can derive every moveable feast for any year)
  - A dictionary of FIXED feast days (same calendar date every year)
  - A dictionary of MOVEABLE feast days (calculated from Easter each year)
  - A lookup function get_feast(date) that returns feast info for a given
    date, checking moveable feasts first, then fixed feasts.

Each feast entry is a dict with:
  name        -> str, name of the feast/solemnity/day
  rank        -> str, e.g. "Solemnity", "Feast", "Memorial", "Season"
  dos         -> list[str], suggested things to do that day
  donts       -> list[str], suggested things to avoid that day
  verse_ref   -> str, Bible reference
  verse_text  -> str, Bible verse text (Douay-Rheims / KJV, public domain)
  blurb       -> str, one-line note on why the day matters

Feel free to expand these dictionaries with more saints' days that matter
to you personally (patron saints, parish feast day, etc.) -- that's the
whole point of running this yourself rather than using a generic app.
"""

from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Easter computation (Anonymous Gregorian / Meeus-Jones-Butcher algorithm)
# ---------------------------------------------------------------------------
def calculate_easter(year: int) -> date:
    """Return the date of Easter Sunday (Gregorian calendar) for the given year."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_moveable_feasts(year: int) -> dict:
    """
    Build a dict keyed by (month, day) tuples for every moveable feast
    that depends on Easter, for the given year.
    """
    easter = calculate_easter(year)

    ash_wednesday = easter - timedelta(days=46)
    palm_sunday = easter - timedelta(days=7)
    holy_thursday = easter - timedelta(days=3)
    good_friday = easter - timedelta(days=2)
    holy_saturday = easter - timedelta(days=1)
    divine_mercy_sunday = easter + timedelta(days=7)
    ascension = easter + timedelta(days=39)      # Thursday, 40th day of Easter
    pentecost = easter + timedelta(days=49)
    trinity_sunday = easter + timedelta(days=56)
    corpus_christi = easter + timedelta(days=60)  # Thursday; many places move to following Sunday
    corpus_christi_sunday = easter + timedelta(days=63)
    sacred_heart = easter + timedelta(days=68)    # Friday after Corpus Christi
    immaculate_heart = easter + timedelta(days=69)  # Saturday right after Sacred Heart
    christ_the_king = easter + timedelta(days=(34 * 7) - (easter.weekday()))  # computed below instead

    # Christ the King = last Sunday before Advent = Sunday nearest Nov 20-26,
    # 34 weeks after Pentecost is not exact, so compute directly instead:
    christ_the_king = _christ_the_king(year)

    feasts = {
        _k(ash_wednesday): {
            "name": "Ash Wednesday",
            "rank": "Beginning of Lent",
            "dos": [
                "Attend Mass and receive ashes",
                "Fast (one full meal + two smaller meals) if aged 18-59",
                "Abstain from meat",
                "Begin your Lenten resolutions: prayer, fasting, almsgiving",
            ],
            "donts": [
                "Don't eat meat",
                "Don't overeat outside the permitted meals",
                "Don't treat the ashes as just a formality -- let them remind you of your mortality and need for repentance",
            ],
            "verse_ref": "Joel 2:12-13",
            "verse_text": "Now therefore, saith the Lord, be converted to me with all your heart, in fasting, and in weeping, and in mourning. And rend your hearts, and not your garments, and turn to the Lord your God.",
            "blurb": "The solemn start of the Church's 40 days of penance before Easter.",
        },
        _k(palm_sunday): {
            "name": "Palm Sunday of the Passion of the Lord",
            "rank": "Sunday",
            "dos": [
                "Attend Mass and receive a blessed palm branch",
                "Keep the palm at home as a sacramental",
                "Reflect on the reading of the Passion",
            ],
            "donts": [
                "Don't discard the blessed palm as ordinary trash (burn it or return it to the parish next Ash Wednesday)",
            ],
            "verse_ref": "Matthew 21:9",
            "verse_text": "And the multitudes that went before, and that followed, cried, saying: Hosanna to the son of David: blessed is he that cometh in the name of the Lord: Hosanna in the highest.",
            "blurb": "Commemorates Christ's triumphant entry into Jerusalem before His Passion.",
        },
        _k(holy_thursday): {
            "name": "Holy Thursday (Mass of the Lord's Supper)",
            "rank": "Solemn day of Holy Week",
            "dos": [
                "Attend the evening Mass of the Lord's Supper",
                "Spend time in Eucharistic adoration afterward",
                "Reflect on the institution of the priesthood and the Eucharist",
            ],
            "donts": [
                "Don't skip adoration if you're able to attend -- watch and pray as the Apostles were asked to",
            ],
            "verse_ref": "1 Corinthians 11:23-24",
            "verse_text": "For I have received of the Lord that which also I delivered unto you, that the Lord Jesus, the same night in which he was betrayed, took bread. And giving thanks, broke, and said: Take ye, and eat: this is my body.",
            "blurb": "Commemorates the Last Supper and the institution of the Eucharist and priesthood.",
        },
        _k(good_friday): {
            "name": "Good Friday",
            "rank": "Solemn day of Holy Week (fast & abstinence)",
            "dos": [
                "Attend the Celebration of the Lord's Passion",
                "Venerate the Cross",
                "Fast and abstain from meat",
                "Pray the Stations of the Cross",
            ],
            "donts": [
                "Don't eat meat",
                "Don't celebrate Mass today (none is offered anywhere in the Church)",
                "Don't treat it as a normal workday -- keep it quiet and prayerful",
            ],
            "verse_ref": "Isaiah 53:5",
            "verse_text": "But he was wounded for our iniquities, he was bruised for our sins: the chastisement of our peace was upon him, and by his bruises we are healed.",
            "blurb": "The day Christ suffered and died on the Cross for the salvation of the world.",
        },
        _k(holy_saturday): {
            "name": "Holy Saturday",
            "rank": "Day of the Easter Vigil",
            "dos": [
                "Keep the day quiet -- Christ lies in the tomb",
                "Attend the Easter Vigil Mass after nightfall",
                "Prepare your heart to renew your baptismal promises",
            ],
            "donts": [
                "Don't hold the Vigil before nightfall",
                "Don't treat the day as the celebration itself -- the joy begins at the Vigil",
            ],
            "verse_ref": "Matthew 27:65-66",
            "verse_text": "Pilate saith to them: You have a guard; go, guard it as you know. And they departing, made the sepulchre sure, sealing the stone, and setting guards.",
            "blurb": "The day of watchful waiting between the Crucifixion and the Resurrection.",
        },
        _k(easter): {
            "name": "Easter Sunday -- The Resurrection of the Lord",
            "rank": "Solemnity (highest rank, Holy Day of Obligation)",
            "dos": [
                "Attend Mass",
                "Renew your baptismal promises",
                "Celebrate joyfully with family -- feasting is encouraged!",
                "Greet others with 'He is Risen!'",
            ],
            "donts": [
                "Don't fast today -- Lent is over, this is the greatest feast of the year",
                "Don't let the day pass without thanking God for the Resurrection",
            ],
            "verse_ref": "Matthew 28:6",
            "verse_text": "He is not here, for he is risen, as he said. Come, and see the place where the Lord was laid.",
            "blurb": "The center of the entire Christian faith: Christ's victory over sin and death.",
        },
        _k(divine_mercy_sunday): {
            "name": "Divine Mercy Sunday",
            "rank": "Feast (2nd Sunday of Easter)",
            "dos": [
                "Attend Mass and go to Confession within the octave if possible",
                "Pray the Divine Mercy Chaplet",
                "Seek and receive the plenary indulgence attached to this feast (per the usual conditions)",
            ],
            "donts": [
                "Don't let doubt keep you from trusting in God's mercy",
            ],
            "verse_ref": "John 20:29",
            "verse_text": "Jesus saith to him: Because thou hast seen me, Thomas, thou hast believed: blessed are they that have not seen, and have believed.",
            "blurb": "Celebrates the Divine Mercy revealed by Christ to St. Faustina.",
        },
        _k(ascension): {
            "name": "The Ascension of the Lord",
            "rank": "Solemnity (Holy Day of Obligation in many places)",
            "dos": [
                "Attend Mass",
                "Reflect on Christ's promise to send the Holy Spirit",
                "Begin the Novena to the Holy Spirit (through the vigil of Pentecost)",
            ],
            "donts": [
                "Don't skip Mass if it's a Holy Day of Obligation in your diocese (check local norms -- some have moved it to the following Sunday)",
            ],
            "verse_ref": "Acts 1:9-11",
            "verse_text": "And when he had said these things, while they looked on, he was raised up: and a cloud received him out of their sight. This same Jesus, who is taken up from you into heaven, shall so come, as you have seen him going into heaven.",
            "blurb": "Christ ascends bodily into Heaven 40 days after His Resurrection.",
        },
        _k(pentecost): {
            "name": "Pentecost Sunday",
            "rank": "Solemnity",
            "dos": [
                "Attend Mass",
                "Pray to the Holy Spirit for His seven gifts",
                "Consider wearing red, the liturgical color of the day",
            ],
            "donts": [
                "Don't neglect asking the Holy Spirit for guidance -- this is His feast",
            ],
            "verse_ref": "Acts 2:3-4",
            "verse_text": "And there appeared to them parted tongues as it were of fire, and it sat upon every one of them. And they were all filled with the Holy Ghost.",
            "blurb": "The descent of the Holy Spirit on the Apostles and the birth of the Church.",
        },
        _k(trinity_sunday): {
            "name": "The Most Holy Trinity",
            "rank": "Solemnity",
            "dos": [
                "Attend Mass",
                "Pray the Glory Be with deliberate attention to its meaning",
                "Reflect on how the Trinity is present in your daily life",
            ],
            "donts": [
                "Don't rush past this mystery -- take time to sit with it rather than merely reciting it",
            ],
            "verse_ref": "Matthew 28:19",
            "verse_text": "Going therefore, teach ye all nations; baptizing them in the name of the Father, and of the Son, and of the Holy Ghost.",
            "blurb": "Celebrates the central mystery of the Christian faith: One God in Three Persons.",
        },
        _k(corpus_christi): {
            "name": "The Most Holy Body and Blood of Christ (Corpus Christi)",
            "rank": "Solemnity",
            "dos": [
                "Attend Mass",
                "Join a Eucharistic procession if your parish holds one",
                "Spend extra time in adoration of the Blessed Sacrament",
            ],
            "donts": [
                "Don't receive Communion in a state of mortal sin -- go to Confession first if needed",
            ],
            "verse_ref": "John 6:51",
            "verse_text": "I am the living bread which came down from heaven. If any man eat of this bread, he shall live for ever.",
            "blurb": "Honors the Real Presence of Christ in the Holy Eucharist.",
        },
        _k(sacred_heart): {
            "name": "The Most Sacred Heart of Jesus",
            "rank": "Solemnity",
            "dos": [
                "Attend Mass",
                "Make an act of reparation and consecration to the Sacred Heart",
                "Pray for trust in God's merciful love",
            ],
            "donts": [
                "Don't let devotion to the Sacred Heart become mere sentiment -- let it call you to conversion",
            ],
            "verse_ref": "Matthew 11:29",
            "verse_text": "Take up my yoke upon you, and learn of me, because I am meek, and humble of heart: and you shall find rest to your souls.",
            "blurb": "Honors Christ's boundless love for humanity, symbolized by His Sacred Heart.",
        },
        _k(immaculate_heart): {
            "name": "The Immaculate Heart of Mary",
            "rank": "Memorial",
            "dos": [
                "Pray the Rosary",
                "Ask Mary's intercession for a heart more attentive to God, as hers was",
                "Reflect on Mary's own fiat and quiet trust through suffering",
            ],
            "donts": [
                "Don't separate devotion to Mary's heart from imitating her total openness to God's will",
            ],
            "verse_ref": "Luke 2:19",
            "verse_text": "But Mary kept all these words, pondering them in her heart.",
            "blurb": "Held the day after the Sacred Heart, honoring Mary's own heart -- her faith, hope, and love for God and neighbor.",
        },
        _k(christ_the_king): {
            "name": "Our Lord Jesus Christ, King of the Universe",
            "rank": "Solemnity (closes the liturgical year)",
            "dos": [
                "Attend Mass",
                "Renew your personal commitment to Christ's kingship over your life",
                "Pray for the conversion of the world to Christ",
            ],
            "donts": [
                "Don't let earthly concerns crowd out recognition of Christ as King of your life",
            ],
            "verse_ref": "John 18:37",
            "verse_text": "Pilate therefore said to him: Art thou a king then? Jesus answered: Thou sayest that I am a king. For this was I born, and for this came I into the world; that I should give testimony to the truth.",
            "blurb": "The final Sunday of the liturgical year, proclaiming Christ's kingship over all creation.",
        },
    }
    return feasts


def _christ_the_king(year: int) -> date:
    """Christ the King = the Sunday before the First Sunday of Advent.
    Advent's First Sunday is the Sunday nearest Nov 30 (St. Andrew's Day),
    specifically the 4th Sunday before Christmas."""
    christmas = date(year, 12, 25)
    # Find the Sunday on/before Dec 25 that starts Christmas week, then walk back.
    days_since_sunday = (christmas.weekday() + 1) % 7  # Monday=0 -> Sunday=6 offset fix
    # Simpler robust approach: find 4th Sunday before Christmas.
    d = christmas
    sundays_found = 0
    while True:
        d -= timedelta(days=1)
        if d.weekday() == 6:  # Sunday
            sundays_found += 1
            if sundays_found == 4:
                first_advent_sunday = d
                break
    return first_advent_sunday - timedelta(days=7)


def _k(d: date) -> tuple:
    return (d.month, d.day)


# ---------------------------------------------------------------------------
# Fixed feast days (same calendar date every year)
# Keyed by (month, day). Expand this freely with saints you have devotion to.
# ---------------------------------------------------------------------------
FIXED_FEASTS = {
    (1, 1): {
        "name": "Mary, Mother of God",
        "rank": "Solemnity (Holy Day of Obligation)",
        "dos": ["Attend Mass", "Begin the year entrusting it to Mary", "Pray the Rosary"],
        "donts": ["Don't start the new year without asking Our Lady's intercession"],
        "verse_ref": "Luke 2:19",
        "verse_text": "But Mary kept all these words, pondering them in her heart.",
        "blurb": "Honors Mary's divine motherhood, celebrated on the Octave Day of Christmas.",
    },
    (1, 6): {
        "name": "The Epiphany of the Lord",
        "rank": "Solemnity",
        "dos": ["Attend Mass", "Chalk your door (20+C+M+B+26)", "Reflect on the Magi's journey of faith"],
        "donts": ["Don't overlook the call to seek Christ as the Magi did, at real cost"],
        "verse_ref": "Matthew 2:11",
        "verse_text": "And entering into the house, they found the child with Mary his mother, and falling down they adored him.",
        "blurb": "Celebrates Christ's manifestation to the Gentiles, represented by the Magi.",
    },
    (2, 2): {
        "name": "The Presentation of the Lord (Candlemas)",
        "rank": "Feast",
        "dos": ["Attend Mass", "Have candles blessed", "Reflect on Simeon's canticle (Nunc Dimittis)"],
        "donts": ["Don't forget to thank God for the light of Christ in your life"],
        "verse_ref": "Luke 2:32",
        "verse_text": "A light to the revelation of the Gentiles, and the glory of thy people Israel.",
        "blurb": "Commemorates Mary and Joseph presenting the infant Jesus in the Temple.",
    },
    (3, 19): {
        "name": "St. Joseph, Spouse of the Blessed Virgin Mary",
        "rank": "Solemnity",
        "dos": ["Attend Mass", "Ask St. Joseph's intercession for your family and work", "Consider a St. Joseph consecration"],
        "donts": ["Don't overlook St. Joseph's quiet, faithful example of obedience"],
        "verse_ref": "Matthew 1:24",
        "verse_text": "And Joseph rising up from sleep, did as the angel of the Lord had commanded him, and took unto him his wife.",
        "blurb": "Honors St. Joseph, foster father of Jesus and patron of the universal Church.",
    },
    (3, 25): {
        "name": "The Annunciation of the Lord",
        "rank": "Solemnity",
        "dos": ["Attend Mass", "Pray the Angelus", "Reflect on Mary's fiat ('let it be done')"],
        "donts": ["Don't let fear keep you from saying 'yes' to God's will as Mary did"],
        "verse_ref": "Luke 1:38",
        "verse_text": "And Mary said: Behold the handmaid of the Lord; be it done to me according to thy word.",
        "blurb": "Commemorates the Angel Gabriel announcing Christ's Incarnation to Mary.",
    },
    (5, 1): {
        "name": "St. Joseph the Worker",
        "rank": "Optional Memorial",
        "dos": ["Offer your work of the day to God", "Ask St. Joseph's help for the dignity of labor"],
        "donts": ["Don't treat your work as disconnected from your faith today"],
        "verse_ref": "Colossians 3:23",
        "verse_text": "Whatsoever you do, do it from the heart, as to the Lord, and not to men.",
        "blurb": "Honors the dignity of human work through St. Joseph's example.",
    },
    (6, 24): {
        "name": "The Nativity of St. John the Baptist",
        "rank": "Solemnity",
        "dos": ["Attend Mass", "Reflect on John's role as the forerunner of Christ"],
        "donts": ["Don't miss the lesson of humility -- 'He must increase, but I must decrease'"],
        "verse_ref": "John 3:30",
        "verse_text": "He must increase, but I must decrease.",
        "blurb": "One of the few birth-feasts on the calendar, marking John's role preparing the way for Christ.",
    },
    (6, 29): {
        "name": "Sts. Peter and Paul, Apostles",
        "rank": "Solemnity",
        "dos": ["Attend Mass", "Pray for the Pope and the unity of the Church", "Reflect on the two pillars of the early Church"],
        "donts": ["Don't take the Church's foundation on the Apostles for granted"],
        "verse_ref": "Matthew 16:18",
        "verse_text": "And I say to thee: That thou art Peter; and upon this rock I will build my church.",
        "blurb": "Honors the two great Apostles who founded and shaped the early Church in Rome.",
    },
    (8, 6): {
        "name": "The Transfiguration of the Lord",
        "rank": "Feast",
        "dos": ["Attend Mass", "Reflect on the glimpse of Christ's divine glory given to Peter, James, and John"],
        "donts": ["Don't stay only on the 'mountaintop' -- like the Apostles, come back down to serve"],
        "verse_ref": "Matthew 17:5",
        "verse_text": "This is my beloved Son, in whom I am well pleased: hear ye him.",
        "blurb": "Commemorates Christ revealing His divine glory to three Apostles on the mountain.",
    },
    (8, 15): {
        "name": "The Assumption of the Blessed Virgin Mary",
        "rank": "Solemnity (Holy Day of Obligation)",
        "dos": ["Attend Mass", "Pray the Rosary", "Reflect on our own hope of bodily resurrection"],
        "donts": ["Don't miss Mass -- this is a Holy Day of Obligation in most places"],
        "verse_ref": "Luke 1:49",
        "verse_text": "Because he that is mighty, hath done great things to me: and holy is his name.",
        "blurb": "Celebrates Mary's body and soul being assumed into Heaven.",
    },
    (9, 14): {
        "name": "The Exaltation of the Holy Cross",
        "rank": "Feast",
        "dos": ["Attend Mass", "Venerate a crucifix", "Reflect on the Cross as the instrument of salvation"],
        "donts": ["Don't view the Cross only as suffering -- see it also as victory"],
        "verse_ref": "John 3:14-15",
        "verse_text": "And as Moses lifted up the serpent in the desert, so must the Son of man be lifted up: that whosoever believeth in him may not perish, but may have life everlasting.",
        "blurb": "Commemorates the finding and exaltation of the True Cross.",
    },
    (10, 4): {
        "name": "St. Francis of Assisi",
        "rank": "Memorial",
        "dos": ["Pray for a spirit of simplicity and poverty of spirit", "Consider having pets blessed"],
        "donts": ["Don't let material attachments crowd out your relationship with God today"],
        "verse_ref": "Matthew 6:19-20",
        "verse_text": "Lay not up to yourselves treasures on earth... But lay up to yourselves treasures in heaven.",
        "blurb": "Honors the patron of animals, ecology, and radical evangelical poverty.",
    },
    (11, 1): {
        "name": "All Saints",
        "rank": "Solemnity (Holy Day of Obligation)",
        "dos": ["Attend Mass", "Pray to your patron saint(s)", "Read about a saint you don't know well"],
        "donts": ["Don't forget the universal call to holiness -- sainthood is for you too"],
        "verse_ref": "Revelation 7:9",
        "verse_text": "After this I saw a great multitude, which no man could number, of all nations, and tribes, and peoples, and tongues, standing before the throne.",
        "blurb": "Honors all the saints in Heaven, known and unknown.",
    },
    (11, 2): {
        "name": "All Souls' Day (Commemoration of the Faithful Departed)",
        "rank": "Commemoration",
        "dos": ["Attend Mass", "Pray for the souls in Purgatory", "Visit a cemetery and pray for the dead"],
        "donts": ["Don't neglect praying for your deceased family and friends"],
        "verse_ref": "2 Maccabees 12:46",
        "verse_text": "It is therefore a holy and wholesome thought to pray for the dead, that they may be loosed from sins.",
        "blurb": "A day dedicated to prayer for all the faithful departed.",
    },
    (12, 8): {
        "name": "The Immaculate Conception of the Blessed Virgin Mary",
        "rank": "Solemnity (Holy Day of Obligation)",
        "dos": ["Attend Mass", "Pray the Rosary", "Reflect on Mary's sinlessness from the first moment of her existence"],
        "donts": ["Don't miss Mass -- this is a Holy Day of Obligation in most places"],
        "verse_ref": "Luke 1:28",
        "verse_text": "Hail, full of grace, the Lord is with thee: blessed art thou among women.",
        "blurb": "Celebrates Mary being conceived without the stain of Original Sin.",
    },
    (12, 12): {
        "name": "Our Lady of Guadalupe",
        "rank": "Feast (Patroness of the Americas)",
        "dos": ["Pray for the protection of the unborn", "Ask Our Lady's intercession for the Americas"],
        "donts": ["Don't overlook her message of tenderness to the poor and forgotten"],
        "verse_ref": "Revelation 12:1",
        "verse_text": "And a great sign appeared in heaven: A woman clothed with the sun, and the moon under her feet, and on her head a crown of twelve stars.",
        "blurb": "Commemorates Our Lady's apparition to St. Juan Diego in Mexico in 1531.",
    },
    (12, 24): {
        "name": "Christmas Eve (Vigil of the Nativity)",
        "rank": "Vigil",
        "dos": ["Attend the Vigil Mass", "Prepare your home and heart for Christmas", "Spend time in quiet prayer"],
        "donts": ["Don't let the commercial rush crowd out prayerful anticipation"],
        "verse_ref": "Luke 2:7",
        "verse_text": "And she brought forth her firstborn son, and wrapped him up in swaddling clothes, and laid him in a manger.",
        "blurb": "The final day of Advent anticipation before the Nativity of the Lord.",
    },
    (12, 25): {
        "name": "The Nativity of the Lord (Christmas)",
        "rank": "Solemnity (Holy Day of Obligation)",
        "dos": ["Attend Mass", "Gather with family", "Give generously to those in need", "Sing the Gloria wholeheartedly"],
        "donts": ["Don't let the day pass without recognizing God becoming man for our salvation"],
        "verse_ref": "John 1:14",
        "verse_text": "And the Word was made flesh, and dwelt among us: and we saw his glory, the glory as it were of the only begotten of the Father, full of grace and truth.",
        "blurb": "Celebrates the birth of Jesus Christ, God made man.",
    },
    (12, 26): {
        "name": "St. Stephen, First Martyr",
        "rank": "Feast",
        "dos": ["Pray for persecuted Christians", "Reflect on the courage of the first martyr"],
        "donts": ["Don't let comfort make you indifferent to the price others pay for the faith"],
        "verse_ref": "Acts 7:59",
        "verse_text": "And they stoned Stephen, invoking, and saying: Lord Jesus, receive my spirit.",
        "blurb": "Honors the first Christian martyr, stoned to death for his faith in Christ.",
    },
    (12, 28): {
        "name": "The Holy Innocents, Martyrs",
        "rank": "Feast",
        "dos": ["Pray for the protection of children and the unborn", "Pray for grieving parents"],
        "donts": ["Don't turn away from the reality of innocent suffering in the world today"],
        "verse_ref": "Matthew 2:18",
        "verse_text": "A voice in Rama was heard, lamentation and great mourning; Rachel bewailing her children, and would not be comforted, because they are not.",
        "blurb": "Commemorates the infants killed by Herod in his attempt to kill the infant Jesus.",
    },
}


# ---------------------------------------------------------------------------
# Category templates for the wider Sanctoral Calendar (all the saints)
# ---------------------------------------------------------------------------
# Writing a fully bespoke dos/donts/verse for 150+ saints would make this
# file unmanageable, so every saint below is tagged with a "category" (the
# kind of holiness their life is remembered for) and draws its dos/donts/
# verse from these shared templates. You can always override any field for
# an individual saint by adding it directly in the SAINTS_CALENDAR entry
# (see the merge logic in `_build_saint_entry`).
CATEGORY_TEMPLATES = {
    "apostle": {
        "dos": ["Ask this Apostle's intercession for the spread of the Gospel",
                "Reflect on how the Apostles left everything to follow Christ"],
        "donts": ["Don't reduce discipleship to routine -- the Apostles paid with their lives"],
        "verse_ref": "Mark 3:14",
        "verse_text": "And he made that twelve should be with him, and that he might send them to preach.",
    },
    "evangelist": {
        "dos": ["Read a passage from this Evangelist's Gospel today",
                "Thank God for the written witness to Christ's life"],
        "donts": ["Don't let familiarity with the Gospels dull their power -- read them freshly"],
        "verse_ref": "John 20:31",
        "verse_text": "But these are written, that you may believe that Jesus is the Christ, the Son of God: and that believing, you may have life in his name.",
    },
    "martyr": {
        "dos": ["Pray for Christians who are persecuted for the faith today",
                "Ask this martyr's intercession for courage in your own trials"],
        "donts": ["Don't let comfort make you indifferent to the price others pay for the faith"],
        "verse_ref": "Matthew 10:39",
        "verse_text": "He that findeth his life, shall lose it: and he that shall lose his life for me, shall find it.",
    },
    "virgin_martyr": {
        "dos": ["Ask her intercession for purity of heart and courage",
                "Reflect on total consecration to Christ, even at great cost"],
        "donts": ["Don't underestimate what fidelity to Christ can demand"],
        "verse_ref": "2 Corinthians 11:2",
        "verse_text": "For I have espoused you to one husband, that I may present you as a chaste virgin to Christ.",
    },
    "bishop_martyr": {
        "dos": ["Pray for bishops and pastors of the Church",
                "Ask this saint's intercession for courageous Church leadership"],
        "donts": ["Don't expect faithful shepherding to come without cost"],
        "verse_ref": "John 10:11",
        "verse_text": "I am the good shepherd. The good shepherd giveth his life for his sheep.",
    },
    "deacon_martyr": {
        "dos": ["Pray for deacons and those who serve the poor",
                "Reflect on service to Christ in the poor, even to the point of death"],
        "donts": ["Don't separate charity toward the poor from love of Christ"],
        "verse_ref": "Matthew 25:40",
        "verse_text": "Amen I say to you, as long as you did it to one of these my least brethren, you did it to me.",
    },
    "pope_martyr": {
        "dos": ["Pray for the Pope and the unity of the Church",
                "Ask this saint's intercession for fidelity to Christ under pressure"],
        "donts": ["Don't take the Church's endurance through persecution for granted"],
        "verse_ref": "Matthew 16:18",
        "verse_text": "And I say to thee: That thou art Peter; and upon this rock I will build my church.",
    },
    "doctor": {
        "dos": ["Read a short passage of this saint's writing or teaching today",
                "Ask for a deeper understanding of the faith"],
        "donts": ["Don't let the faith remain unexamined -- these saints gave their minds to God too"],
        "verse_ref": "1 Peter 3:15",
        "verse_text": "Being ready always to satisfy every one that asketh you a reason of that hope which is in you.",
    },
    "bishop": {
        "dos": ["Pray for your own bishop and diocese",
                "Ask this saint's intercession for wise, faithful shepherds"],
        "donts": ["Don't neglect gratitude for those who have taught and guided you in the faith"],
        "verse_ref": "1 Timothy 4:12",
        "verse_text": "Be thou an example of the faithful, in word, in conversation, in charity, in faith, in chastity.",
    },
    "pope": {
        "dos": ["Pray for the Holy Father and his intentions",
                "Ask this saint's intercession for the unity and holiness of the Church"],
        "donts": ["Don't view the papacy as merely an institution -- pray for the man who carries it"],
        "verse_ref": "Luke 22:32",
        "verse_text": "But I have prayed for thee, that thy faith fail not: and thou, being once converted, confirm thy brethren.",
    },
    "founder": {
        "dos": ["Learn one fact about the religious order or community this saint founded",
                "Ask for the grace to respond generously to whatever God is asking of you"],
        "donts": ["Don't assume big things for God require big resources -- they started small too"],
        "verse_ref": "Luke 9:23",
        "verse_text": "If any man will come after me, let him deny himself, and take up his cross daily, and follow me.",
    },
    "religious": {
        "dos": ["Pray for men and women in consecrated religious life",
                "Ask this saint's intercession for a life more centered on prayer"],
        "donts": ["Don't dismiss the hidden, ordinary faithfulness that most holiness is made of"],
        "verse_ref": "Colossians 3:3",
        "verse_text": "For you are dead; and your life is hid with Christ in God.",
    },
    "virgin": {
        "dos": ["Ask her intercession for purity and single-hearted devotion to Christ",
                "Reflect on a life fully given to God"],
        "donts": ["Don't confuse consecration to God with mere self-denial -- it's a gift, not a loss"],
        "verse_ref": "1 Corinthians 7:34",
        "verse_text": "And the unmarried woman, and the virgin, thinketh on the things of the Lord, that she may be holy both in body and in spirit.",
    },
    "priest": {
        "dos": ["Pray for priests, especially those who are struggling",
                "Thank God for a priest who has shaped your own faith"],
        "donts": ["Don't take the sacraments a priest makes possible for granted"],
        "verse_ref": "Hebrews 5:1",
        "verse_text": "For every high priest taken from among men, is ordained for men in the things that appertain to God, that he may offer up gifts and sacrifices for sins.",
    },
    "missionary": {
        "dos": ["Pray for missionaries bringing the Gospel to unfamiliar places",
                "Ask yourself who in your own life needs to hear about Christ"],
        "donts": ["Don't assume evangelization is someone else's job"],
        "verse_ref": "Mark 16:15",
        "verse_text": "Go ye into the whole world, and preach the gospel to every creature.",
    },
    "widow": {
        "dos": ["Pray for widows and widowers, and for those who care for them",
                "Ask this saint's intercession for perseverance through loss"],
        "donts": ["Don't let grief become an excuse to withdraw from God -- bring it to Him instead"],
        "verse_ref": "James 1:27",
        "verse_text": "Religion clean and undefiled before God and the Father, is this: to visit the fatherless and widows in their tribulation.",
    },
    "king": {
        "dos": ["Pray for those who hold public authority, that they govern justly",
                "Ask this saint's intercession for integrity in positions of power"],
        "donts": ["Don't equate worldly power with true greatness -- this saint didn't"],
        "verse_ref": "Proverbs 29:4",
        "verse_text": "A just king setteth up the land: a covetous man shall destroy it.",
    },
    "hermit": {
        "dos": ["Spend a few extra quiet minutes in prayer today",
                "Ask for the grace to hear God in silence"],
        "donts": ["Don't fill every silence with noise -- give God room to speak"],
        "verse_ref": "1 Kings 19:12",
        "verse_text": "And after the fire a whistling of a gentle air. And when Elias heard it, he covered his face.",
    },
    "marian": {
        "dos": ["Pray the Rosary or the Angelus",
                "Ask Mary's intercession under this particular title"],
        "donts": ["Don't let devotion to Mary stay sentimental -- let it draw you closer to her Son"],
        "verse_ref": "Luke 1:48",
        "verse_text": "Because he hath regarded the humility of his handmaid: for behold from henceforth all generations shall call me blessed.",
    },
    "disciple": {
        "dos": ["Reflect on this saint's friendship with Christ",
                "Ask for the grace of greater intimacy with the Lord"],
        "donts": ["Don't settle for knowing about Christ instead of knowing Him personally"],
        "verse_ref": "John 15:15",
        "verse_text": "But I have called you friends: because all things whatsoever I have heard of my Father, I have made known to you.",
    },
    "angels": {
        "dos": ["Ask your Guardian Angel and these Archangels for protection today",
                "Thank God for the unseen help of the angels"],
        "donts": ["Don't forget you're never spiritually alone or unguarded"],
        "verse_ref": "Psalm 91:11",
        "verse_text": "For he hath given his angels charge over thee; to keep thee in all thy ways.",
    },
    "special": {
        "dos": ["Take a moment to learn about the meaning of today's feast",
                "Bring the day's intention to prayer"],
        "donts": ["Don't let the day pass unmarked"],
        "verse_ref": "Psalm 118:24",
        "verse_text": "This is the day which the Lord hath made: let us be glad and rejoice therein.",
    },
}


def _build_saint_entry(name: str, rank: str, category: str, blurb: str = None, **overrides) -> dict:
    """Merge a category template with saint-specific name/rank/blurb, allowing
    any field (dos, donts, verse_ref, verse_text) to be overridden per-saint."""
    template = CATEGORY_TEMPLATES[category]
    entry = {
        "name": name,
        "rank": rank,
        "dos": template["dos"],
        "donts": template["donts"],
        "verse_ref": template["verse_ref"],
        "verse_text": template["verse_text"],
        "blurb": blurb or f"Commemorates the life and witness of {name}.",
    }
    entry.update(overrides)
    return entry


# ---------------------------------------------------------------------------
# SAINTS_CALENDAR -- the wider General Roman Calendar (universal Latin
# Church calendar of saints), on top of the major solemnities/feasts
# already listed in FIXED_FEASTS above.
#
# Format: (month, day): (name, rank, category [, blurb])
# "Optional Memorial" days are included -- if two fall on the same date,
# only the first one listed here will show (edit freely to pick a
# favorite, or combine them into one entry).
#
# This covers the UNIVERSAL calendar. Your own diocese, country, or parish
# may keep additional local feasts -- add them the same way.
# ---------------------------------------------------------------------------
_RAW_SAINTS = [
    # Each entry: name, rank, category (for dos/donts template),
    # blurb (life-specific reflection), verse_ref, verse_text (life-specific).
    {"date": (1, 2), "name": "Sts. Basil the Great and Gregory Nazianzen, Bishops and Doctors", "rank": "Memorial", "category": "doctor",
     "blurb": "Two close friends and bishops who defended the divinity of Christ against Arianism, shaping Christian theology for all time.",
     "verse_ref": "Jude 1:3", "verse_text": "I was in all care to write unto you, exhorting you to contend earnestly for the faith once delivered to the saints."},
    {"date": (1, 7), "name": "St. Raymond of Penyafort, Priest", "rank": "Optional Memorial", "category": "priest",
     "blurb": "A Dominican canon lawyer who organized Church law and became a renowned, merciful confessor of penitents.",
     "verse_ref": "John 20:23", "verse_text": "Whose sins you shall forgive, they are forgiven them: and whose sins you shall retain, they are retained."},
    {"date": (1, 13), "name": "St. Hilary of Poitiers, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "Called the 'Hammer of the Arians' for his fearless defense of Christ's divinity, which cost him years of exile.",
     "verse_ref": "2 Timothy 4:2", "verse_text": "Preach the word: be instant in season, out of season: reprove, entreat, rebuke in all patience and doctrine."},
    {"date": (1, 17), "name": "St. Anthony of Egypt, Abbot", "rank": "Memorial", "category": "hermit",
     "blurb": "After hearing the Gospel read aloud in church, he sold everything he owned and went into the desert, becoming the father of Christian monasticism.",
     "verse_ref": "Matthew 19:21", "verse_text": "If thou wilt be perfect, go sell what thou hast, and give to the poor, and thou shalt have treasure in heaven: and come, follow me."},
    {"date": (1, 20), "name": "St. Fabian, Pope and Martyr", "rank": "Optional Memorial", "category": "pope_martyr",
     "blurb": "Guided the Church through years of peace before dying a martyr in the Decian persecution.",
     "verse_ref": "Acts 20:28", "verse_text": "Take heed to yourselves, and to the whole flock, wherein the Holy Ghost hath placed you bishops, to rule the church of God."},
    {"date": (1, 21), "name": "St. Agnes, Virgin and Martyr", "rank": "Memorial", "category": "virgin_martyr",
     "blurb": "A girl of about twelve or thirteen who refused marriage, saying she was already espoused to Christ, and was martyred for it under Diocletian.",
     "verse_ref": "2 Corinthians 11:2", "verse_text": "For I have espoused you to one husband, that I may present you as a chaste virgin to Christ."},
    {"date": (1, 22), "name": "St. Vincent, Deacon and Martyr", "rank": "Optional Memorial", "category": "deacon_martyr",
     "blurb": "A deacon tortured on a gridiron under Diocletian who reportedly remained joyful and unshaken throughout his ordeal.",
     "verse_ref": "Romans 8:35,37", "verse_text": "Who then shall separate us from the love of Christ?... But in all these things we overcome, because of him that hath loved us."},
    {"date": (1, 24), "name": "St. Francis de Sales, Bishop and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Bishop of Geneva famous for his gentleness, who taught that ordinary laypeople could reach real holiness in everyday life.",
     "verse_ref": "Matthew 11:29", "verse_text": "Take up my yoke upon you, and learn of me, because I am meek, and humble of heart: and you shall find rest to your souls."},
    {"date": (1, 25), "name": "The Conversion of St. Paul, Apostle", "rank": "Feast", "category": "apostle",
     "blurb": "The persecutor of Christians struck down by a blinding light on the road to Damascus, and reborn as the Apostle to the Gentiles.",
     "verse_ref": "Acts 9:3-5", "verse_text": "Suddenly a light from heaven shined round about him. And falling on the ground, he heard a voice saying to him: Saul, Saul, why persecutest thou me?"},
    {"date": (1, 26), "name": "Sts. Timothy and Titus, Bishops", "rank": "Memorial", "category": "bishop",
     "blurb": "Two of St. Paul's closest companions and disciples, made bishops and entrusted with young, fragile churches.",
     "verse_ref": "2 Timothy 1:6", "verse_text": "For which cause I admonish thee, that thou stir up the grace of God, which is in thee, by the imposition of my hands."},
    {"date": (1, 27), "name": "St. Angela Merici, Virgin", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Ursulines to educate girls at a time when female education was widely neglected.",
     "verse_ref": "Titus 2:3-4", "verse_text": "The aged women... teachers of good things. That they may teach the young women to be wise."},
    {"date": (1, 28), "name": "St. Thomas Aquinas, Priest and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "The greatest theologian of the Church, who near the end of his life said all he had written seemed like straw compared to what had been revealed to him in prayer.",
     "verse_ref": "1 Corinthians 13:2", "verse_text": "And if I should have all faith, so that I could remove mountains, and have not charity, I am nothing."},
    {"date": (1, 31), "name": "St. John Bosco, Priest", "rank": "Memorial", "category": "founder",
     "blurb": "Founded the Salesians to care for poor and abandoned boys in industrial Turin, believing kindness worked better than punishment.",
     "verse_ref": "Mark 10:14", "verse_text": "Suffer the little children to come unto me, and forbid them not: for of such is the kingdom of God."},

    {"date": (2, 3), "name": "St. Blaise, Bishop and Martyr", "rank": "Optional Memorial", "category": "bishop_martyr",
     "blurb": "A bishop and physician remembered for miraculously saving a boy choking on a fish bone; his blessing of throats continues today. (Some places instead keep St. Ansgar, the 'Apostle of the North,' who braved hostile Viking-era Scandinavia to plant the first churches there.)",
     "verse_ref": "Psalm 34:19", "verse_text": "Many are the afflictions of the just; but out of them all will the Lord deliver them."},
    {"date": (2, 5), "name": "St. Agatha, Virgin and Martyr", "rank": "Memorial", "category": "virgin_martyr",
     "blurb": "A Sicilian noblewoman who refused a Roman prefect's advances and was brutally tortured for her fidelity to Christ.",
     "verse_ref": "2 Corinthians 12:9", "verse_text": "My grace is sufficient for thee: for power is made perfect in infirmity."},
    {"date": (2, 6), "name": "St. Paul Miki and Companions, Martyrs", "rank": "Memorial", "category": "martyr",
     "blurb": "Twenty-six Christians crucified in Nagasaki in 1597 who sang hymns and preached forgiveness as they died.",
     "verse_ref": "Revelation 7:14", "verse_text": "These are they who are come out of great tribulation, and have washed their robes, and have made them white in the blood of the Lamb."},
    {"date": (2, 8), "name": "St. Josephine Bakhita, Virgin", "rank": "Optional Memorial", "category": "virgin",
     "blurb": "Kidnapped into slavery as a child in Sudan, she was later freed, became a Canossian nun, and radiated forgiveness toward her former captors. (Some places instead keep St. Jerome Emiliani, a former soldier who founded orphanages and is patron of abandoned children.)",
     "verse_ref": "Ephesians 4:32", "verse_text": "And be ye kind one to another, merciful, forgiving one another, even as God hath forgiven you in Christ."},
    {"date": (2, 10), "name": "St. Scholastica, Virgin", "rank": "Memorial", "category": "founder",
     "blurb": "Twin sister of St. Benedict; tradition holds she once prayed for a storm so a nighttime visit with her brother, spent speaking of heaven, would not have to end.",
     "verse_ref": "Psalm 133:1", "verse_text": "Behold how good and how pleasant it is for brethren to dwell together in unity."},
    {"date": (2, 11), "name": "Our Lady of Lourdes", "rank": "Optional Memorial", "category": "marian",
     "blurb": "Commemorates Mary's appearances to St. Bernadette Soubirous in 1858, and the healing spring that still draws pilgrims to Lourdes.",
     "verse_ref": "James 5:14-15", "verse_text": "Is any man sick among you? Let him bring in the priests of the church... and the prayer of faith shall save the sick man."},
    {"date": (2, 14), "name": "Sts. Cyril, Monk, and Methodius, Bishop", "rank": "Memorial", "category": "missionary",
     "blurb": "Brothers who became 'Apostles to the Slavs,' creating an alphabet for the Slavic peoples so they could hear the Gospel and liturgy in their own tongue.",
     "verse_ref": "Acts 2:8", "verse_text": "And how have we every man heard our own tongue wherein we were born?"},
    {"date": (2, 17), "name": "Seven Holy Founders of the Servite Order", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Seven Florentine noblemen who left behind wealth and status to found the Servite Order in devotion to Our Lady of Sorrows.",
     "verse_ref": "Matthew 19:27,29", "verse_text": "Behold we have left all things, and followed thee... shall possess life everlasting."},
    {"date": (2, 21), "name": "St. Peter Damian, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "A reforming monk and bishop who fought corruption and worldliness among the clergy of his time.",
     "verse_ref": "1 Timothy 3:2", "verse_text": "It behoveth therefore a bishop to be blameless."},
    {"date": (2, 22), "name": "The Chair of St. Peter, Apostle", "rank": "Feast", "category": "apostle",
     "blurb": "Celebrates not a relic but the teaching authority Christ gave to Peter and, through him, to his successors.",
     "verse_ref": "John 21:17", "verse_text": "He saith to him the third time: Simon, son of John, lovest thou me?... Feed my sheep."},
    {"date": (2, 23), "name": "St. Polycarp, Bishop and Martyr", "rank": "Memorial", "category": "bishop_martyr",
     "blurb": "A disciple of the Apostle John, burned at the stake for refusing to curse Christ, reportedly saying 'Eighty-six years I have served him.'",
     "verse_ref": "Revelation 2:10", "verse_text": "Be thou faithful until death: and I will give thee the crown of life."},

    {"date": (3, 4), "name": "St. Casimir", "rank": "Optional Memorial", "category": "king",
     "blurb": "A young Polish-Lithuanian prince known for chastity, piety, and charity to the poor despite his royal upbringing, who died young.",
     "verse_ref": "1 Timothy 4:12", "verse_text": "Let no man despise thy youth: but be thou an example of the faithful."},
    {"date": (3, 7), "name": "Sts. Perpetua and Felicity, Martyrs", "rank": "Memorial", "category": "martyr",
     "blurb": "A noblewoman and a slave, martyred together in the Carthage arena in 203 AD; Felicity gave birth in prison shortly before her death.",
     "verse_ref": "Galatians 3:28", "verse_text": "There is neither bond nor free... for you are all one in Christ Jesus."},
    {"date": (3, 8), "name": "St. John of God, Religious", "rank": "Optional Memorial", "category": "founder",
     "blurb": "After a disordered early life, he converted and founded the Hospitallers to care for the sick and poor.",
     "verse_ref": "Matthew 25:36", "verse_text": "I was sick, and you visited me."},
    {"date": (3, 9), "name": "St. Frances of Rome, Religious", "rank": "Optional Memorial", "category": "religious",
     "blurb": "A Roman noblewoman who remained a faithful wife and mother while founding a community devoted to serving the poor.",
     "verse_ref": "Proverbs 31:20", "verse_text": "She hath opened her hand to the needy, and stretched out her hands to the poor."},
    {"date": (3, 17), "name": "St. Patrick, Bishop", "rank": "Optional Memorial", "category": "missionary",
     "blurb": "Enslaved in Ireland as a young man, he escaped, then returned voluntarily as a missionary bishop who evangelized much of the island.",
     "verse_ref": "Romans 10:14-15", "verse_text": "How then shall they call on him, in whom they have not believed?... how beautiful are the feet of them that preach the gospel of peace."},
    {"date": (3, 18), "name": "St. Cyril of Jerusalem, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "Bishop and catechist exiled multiple times for his orthodoxy, whose lectures prepared new converts for baptism.",
     "verse_ref": "1 Peter 2:2", "verse_text": "As new born babes, desire the rational milk without guile, that thereby you may grow unto salvation."},
    {"date": (3, 23), "name": "St. Turibius of Mongrovejo, Bishop", "rank": "Optional Memorial", "category": "bishop",
     "blurb": "Archbishop of Lima who tirelessly evangelized and defended the indigenous peoples of Peru across a vast territory.",
     "verse_ref": "Mark 16:15", "verse_text": "Go ye into the whole world, and preach the gospel to every creature."},

    {"date": (4, 2), "name": "St. Francis of Paola, Hermit", "rank": "Optional Memorial", "category": "hermit",
     "blurb": "A hermit who founded the Minims, an order whose motto and rule of life was simply 'Charity.'",
     "verse_ref": "1 Corinthians 13:13", "verse_text": "And now there remain faith, hope, and charity, these three: but the greatest of these is charity."},
    {"date": (4, 4), "name": "St. Isidore of Seville, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "Called the last great scholar of the ancient world, he compiled an encyclopedia of all known knowledge; today he's invoked as patron of the internet.",
     "verse_ref": "Proverbs 2:6", "verse_text": "Because the Lord giveth wisdom: and out of his mouth cometh prudence and knowledge."},
    {"date": (4, 5), "name": "St. Vincent Ferrer, Priest", "rank": "Optional Memorial", "category": "priest",
     "blurb": "A Dominican preacher whose sermons on repentance moved crowds across Europe to conversion.",
     "verse_ref": "Matthew 3:2", "verse_text": "Do penance: for the kingdom of heaven is at hand."},
    {"date": (4, 7), "name": "St. John Baptist de la Salle, Priest", "rank": "Memorial", "category": "founder",
     "blurb": "Gave up wealth and a comfortable position to found the Brothers of the Christian Schools, pioneering free education for poor boys.",
     "verse_ref": "Proverbs 22:6", "verse_text": "Train up a child in the way he should go: and when he is old he will not depart from it."},
    {"date": (4, 11), "name": "St. Stanislaus, Bishop and Martyr", "rank": "Memorial", "category": "bishop_martyr",
     "blurb": "Bishop of Krakow martyred by a Polish king he had publicly rebuked for tyranny and injustice.",
     "verse_ref": "Acts 5:29", "verse_text": "We ought to obey God, rather than men."},
    {"date": (4, 13), "name": "St. Martin I, Pope and Martyr", "rank": "Optional Memorial", "category": "pope_martyr",
     "blurb": "A pope exiled and worked to death for defending orthodox Christology against imperial pressure.",
     "verse_ref": "Acts 4:19-20", "verse_text": "We cannot but speak the things which we have seen and heard."},
    {"date": (4, 21), "name": "St. Anselm, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "Archbishop of Canterbury famous for the phrase 'faith seeking understanding' and a classic argument for God's existence.",
     "verse_ref": "Hebrews 11:1", "verse_text": "Now faith is the substance of things to be hoped for, the evidence of things that appear not."},
    {"date": (4, 23), "name": "St. George, Martyr", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "A Roman soldier martyred under Diocletian, later remembered in legend as a dragon-slayer symbolizing the triumph of good over evil. (Some places instead keep St. Adalbert, a bishop-missionary martyred while preaching to the pagan Prussians.)",
     "verse_ref": "2 Timothy 2:3-4", "verse_text": "Labour as a good soldier of Christ Jesus. No man, being a soldier to God, entangleth himself with secular businesses."},
    {"date": (4, 24), "name": "St. Fidelis of Sigmaringen, Priest and Martyr", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "A lawyer turned Capuchin priest, martyred while preaching during the Counter-Reformation missions in Switzerland.",
     "verse_ref": "2 Timothy 4:7", "verse_text": "I have fought a good fight, I have finished my course, I have kept the faith."},
    {"date": (4, 25), "name": "St. Mark, Evangelist", "rank": "Feast", "category": "evangelist",
     "blurb": "Companion of Peter and Paul, and author of the earliest Gospel, traditionally symbolized by a lion.",
     "verse_ref": "Mark 1:1", "verse_text": "The beginning of the gospel of Jesus Christ, the Son of God."},
    {"date": (4, 28), "name": "St. Peter Chanel, Priest and Martyr", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "The first martyr of Oceania, killed in Futuna after a local chief's son converted to Christianity; his death led to the conversion of the whole island.",
     "verse_ref": "John 12:24", "verse_text": "Unless the grain of wheat falling into the ground die, itself remaineth alone. But if it die, it bringeth forth much fruit."},
    {"date": (4, 29), "name": "St. Catherine of Siena, Virgin and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "An uneducated laywoman and mystic whose letters convinced Pope Gregory XI to return the papacy to Rome from Avignon.",
     "verse_ref": "1 Corinthians 1:27", "verse_text": "But the foolish things of the world hath God chosen, that he may confound the wise."},
    {"date": (4, 30), "name": "St. Pius V, Pope", "rank": "Optional Memorial", "category": "pope",
     "blurb": "Implemented the reforms of the Council of Trent and called all of Christendom to pray the Rosary before the naval victory at Lepanto.",
     "verse_ref": "Ephesians 6:12", "verse_text": "For we wrestle not against flesh and blood; but against principalities and powers."},

    {"date": (5, 2), "name": "St. Athanasius, Bishop and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Bishop of Alexandria exiled five times for his unyielding defense of Christ's divinity against Arianism -- 'Athanasius against the world.'",
     "verse_ref": "Romans 8:31", "verse_text": "If God be for us, who is against us?"},
    {"date": (5, 3), "name": "Sts. Philip and James, Apostles", "rank": "Feast", "category": "apostle",
     "blurb": "Philip once asked Jesus to 'show us the Father'; James the Less later wrote an epistle stressing that living faith shows itself in works.",
     "verse_ref": "John 14:9", "verse_text": "Philip, he that seeth me seeth the Father also."},
    {"date": (5, 12), "name": "St. Pancras, Martyr", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "A fourteen-year-old orphaned convert beheaded under Diocletian for refusing to renounce his faith. (Some places instead keep Sts. Nereus and Achilleus, Roman soldiers who left the army rather than persecute Christians, and were martyred themselves.)",
     "verse_ref": "Matthew 19:14", "verse_text": "Suffer the little children, and forbid them not to come to me: for the kingdom of heaven is for such."},
    {"date": (5, 13), "name": "Our Lady of Fatima", "rank": "Optional Memorial", "category": "marian",
     "blurb": "Commemorates Mary's 1917 apparitions to three shepherd children in Fatima, Portugal, with a message of prayer, penance, and the Rosary.",
     "verse_ref": "Luke 2:19", "verse_text": "But Mary kept all these words, pondering them in her heart."},
    {"date": (5, 14), "name": "St. Matthias, Apostle", "rank": "Feast", "category": "apostle",
     "blurb": "Chosen by lot to take the place of Judas among the Twelve after the Ascension.",
     "verse_ref": "Acts 1:26", "verse_text": "And they gave them lot, and the lot fell upon Matthias, and he was numbered with the eleven apostles."},
    {"date": (5, 18), "name": "St. John I, Pope and Martyr", "rank": "Optional Memorial", "category": "pope_martyr",
     "blurb": "Sent by an Ostrogothic king to negotiate with the Byzantine emperor, he was imprisoned on his return and died from the mistreatment.",
     "verse_ref": "John 15:13", "verse_text": "Greater love than this no man hath, that a man lay down his life for his friends."},
    {"date": (5, 20), "name": "St. Bernardine of Siena, Priest", "rank": "Optional Memorial", "category": "priest",
     "blurb": "A Franciscan preacher devoted to promoting the Holy Name of Jesus, symbolized by his famous IHS monogram.",
     "verse_ref": "Philippians 2:9-10", "verse_text": "God also hath exalted him, and hath given him a name which is above all names: That in the name of Jesus every knee should bow."},
    {"date": (5, 21), "name": "St. Christopher Magallanes and Companions, Martyrs", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "Mexican priests martyred during the Cristero War for continuing to celebrate Mass despite a government ban.",
     "verse_ref": "1 Corinthians 11:26", "verse_text": "For as often as you shall eat this bread, and drink the chalice, you shall shew the death of the Lord, until he come."},
    {"date": (5, 25), "name": "St. Bede the Venerable, Priest and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "An English monk called the 'Father of English History,' who also translated Scripture into the language of his people.",
     "verse_ref": "Psalm 119:105", "verse_text": "Thy word is a lamp to my feet, and a light to my paths."},
    {"date": (5, 26), "name": "St. Philip Neri, Priest", "rank": "Memorial", "category": "founder",
     "blurb": "Known as the 'Apostle of Rome' for drawing young people away from vice through humor, joy, and genuine friendship rather than fear.",
     "verse_ref": "Nehemiah 8:10", "verse_text": "The joy of the Lord is our strength."},
    {"date": (5, 27), "name": "St. Augustine of Canterbury, Bishop", "rank": "Optional Memorial", "category": "missionary",
     "blurb": "Sent by Pope Gregory the Great to evangelize England, becoming its first Archbishop of Canterbury.",
     "verse_ref": "Romans 10:14", "verse_text": "How then shall they call on him, in whom they have not believed? Or how shall they believe him, of whom they have not heard? And how shall they hear, without a preacher?"},
    {"date": (5, 31), "name": "The Visitation of the Blessed Virgin Mary", "rank": "Feast", "category": "marian",
     "blurb": "Mary, newly pregnant with Jesus, hurries to help her older cousin Elizabeth -- and is greeted with the first proclamation of who her child is.",
     "verse_ref": "Luke 1:41-42", "verse_text": "The infant leaped in her womb. And Elizabeth was filled with the Holy Ghost... Blessed art thou among women, and blessed is the fruit of thy womb."},

    {"date": (6, 1), "name": "St. Justin, Martyr", "rank": "Memorial", "category": "martyr",
     "blurb": "A philosopher converted to Christianity who wrote reasoned defenses of the faith to Roman emperors before being beheaded for it.",
     "verse_ref": "1 Peter 3:15", "verse_text": "Being ready always to satisfy every one that asketh you a reason of that hope which is in you."},
    {"date": (6, 2), "name": "Sts. Marcellinus and Peter, Martyrs", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "An exorcist and a priest martyred under Diocletian, said to have converted their own jailer and his family before their deaths.",
     "verse_ref": "Acts 16:31", "verse_text": "Believe in the Lord Jesus, and thou shalt be saved, and thy house."},
    {"date": (6, 3), "name": "St. Charles Lwanga and Companions, Martyrs", "rank": "Memorial", "category": "martyr",
     "blurb": "Young Ugandan converts, pages of the king's court, burned alive in 1886 for refusing the king's demands and protecting their faith and purity.",
     "verse_ref": "Daniel 3:17-18", "verse_text": "Our God, whom we worship, is able to save us... But if not, be it known to thee, O king, that we will not worship thy gods."},
    {"date": (6, 5), "name": "St. Boniface, Bishop and Martyr", "rank": "Memorial", "category": "bishop_martyr",
     "blurb": "The 'Apostle of Germany,' famous for cutting down a great oak sacred to pagan worship to show its powerlessness; he was later martyred by pagans.",
     "verse_ref": "Acts 19:19-20", "verse_text": "Many of them who had followed curious arts, brought together their books, and burnt them... So mightily grew the word of God, and was confirmed."},
    {"date": (6, 6), "name": "St. Norbert, Bishop", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Premonstratensians and worked to reform a worldly clergy, restoring reverence for the Eucharist.",
     "verse_ref": "1 Timothy 3:1-2", "verse_text": "If a man desire the office of a bishop, he desireth a good work. It behoveth therefore a bishop to be blameless."},
    {"date": (6, 9), "name": "St. Ephrem, Deacon and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "Called the 'Harp of the Holy Spirit,' he defended orthodox teaching by writing hundreds of hymns in Syriac.",
     "verse_ref": "Colossians 3:16", "verse_text": "Teaching and admonishing one another in psalms, hymns, and spiritual canticles."},
    {"date": (6, 11), "name": "St. Barnabas, Apostle", "rank": "Memorial", "category": "apostle",
     "blurb": "Called 'son of encouragement,' he vouched for the newly converted Paul to a skeptical community and became his companion on the first missionary journeys.",
     "verse_ref": "Acts 4:36", "verse_text": "Joseph, who by the apostles was surnamed Barnabas (which is, by interpretation, The son of consolation)."},
    {"date": (6, 13), "name": "St. Anthony of Padua, Priest and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "A Franciscan Doctor known for powerful preaching -- when people wouldn't listen, he reportedly preached to the fish instead.",
     "verse_ref": "2 Timothy 4:2", "verse_text": "Preach the word: be instant in season, out of season: reprove, entreat, rebuke in all patience and doctrine."},
    {"date": (6, 19), "name": "St. Romuald, Abbot", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Camaldolese, blending solitary hermit life with monastic community, and reformed monasticism in his day.",
     "verse_ref": "Matthew 6:6", "verse_text": "When thou shalt pray, enter into thy chamber, and having shut the door, pray to thy Father in secret."},
    {"date": (6, 21), "name": "St. Aloysius Gonzaga, Religious", "rank": "Memorial", "category": "religious",
     "blurb": "A young Jesuit novice who renounced a noble inheritance and died young while caring for plague victims in Rome.",
     "verse_ref": "Matthew 19:29", "verse_text": "Every one that hath left house, or brethren... for my name's sake, shall receive an hundredfold, and shall possess life everlasting."},
    {"date": (6, 22), "name": "Sts. John Fisher, Bishop, and Thomas More, Martyrs", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "English martyrs executed under Henry VIII for refusing to accept the king as head of the Church; More described himself as dying 'the king's good servant, but God's first.' (Some places instead keep St. Paulinus of Nola, a wealthy bishop-poet who reportedly sold himself into slavery to ransom a widow's captive son.)",
     "verse_ref": "Matthew 10:28", "verse_text": "Fear ye not them that kill the body... but rather fear him that can destroy both soul and body into hell."},
    {"date": (6, 27), "name": "St. Cyril of Alexandria, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "Defended Mary's title as Mother of God at the Council of Ephesus against those who denied it.",
     "verse_ref": "Luke 1:43", "verse_text": "And whence is this to me, that the mother of my Lord should come to me?"},
    {"date": (6, 28), "name": "St. Irenaeus, Bishop and Martyr", "rank": "Memorial", "category": "bishop_martyr",
     "blurb": "A disciple of Polycarp who wrote 'Against Heresies' to refute the Gnostics, before he too was martyred.",
     "verse_ref": "1 Timothy 6:20", "verse_text": "Avoiding profane novelties of words, and oppositions of knowledge falsely so called."},
    {"date": (6, 30), "name": "The First Martyrs of the Holy Roman Church", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "Christians falsely blamed by Nero for the Great Fire of Rome in 64 AD and put to death for it.",
     "verse_ref": "1 Peter 4:16", "verse_text": "But if as a Christian, let him not be ashamed, but let him glorify God in that name."},

    {"date": (7, 3), "name": "St. Thomas, Apostle", "rank": "Feast", "category": "apostle",
     "blurb": "Doubted the Resurrection until he touched Christ's wounds himself, then later carried the Gospel as far as India.",
     "verse_ref": "John 20:28", "verse_text": "Thomas answered, and said to him: My Lord, and my God."},
    {"date": (7, 4), "name": "St. Elizabeth of Portugal", "rank": "Optional Memorial", "category": "widow",
     "blurb": "A queen known for quietly reconciling warring members of her own family and secretly caring for the poor.",
     "verse_ref": "Matthew 5:9", "verse_text": "Blessed are the peacemakers: for they shall be called children of God."},
    {"date": (7, 5), "name": "St. Anthony Zaccaria, Priest", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Barnabites and promoted frequent Communion and devotion to Christ crucified in an era of lax practice.",
     "verse_ref": "1 Corinthians 11:28", "verse_text": "But let a man prove himself: and so let him eat of that bread, and drink of the chalice."},
    {"date": (7, 6), "name": "St. Maria Goretti, Virgin and Martyr", "rank": "Optional Memorial", "category": "virgin_martyr",
     "blurb": "An eleven-year-old who resisted an assault and forgave her attacker from her deathbed -- he later converted because of her forgiveness.",
     "verse_ref": "Matthew 18:21-22", "verse_text": "I say not to thee, till seven times; but till seventy times seven times."},
    {"date": (7, 9), "name": "St. Augustine Zhao Rong and Companions, Martyrs", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "Honors 120 martyrs of China -- Chinese Catholics and missionaries -- killed across centuries of persecution.",
     "verse_ref": "2 Corinthians 4:8-9", "verse_text": "We are troubled on every side, but not distressed... persecuted, but not left."},
    {"date": (7, 11), "name": "St. Benedict, Abbot", "rank": "Memorial", "category": "founder",
     "blurb": "Father of Western monasticism, whose Rule -- built around 'ora et labora,' prayer and work -- still shapes religious life today.",
     "verse_ref": "1 Corinthians 10:31", "verse_text": "Whether you eat or drink, or whatsoever else you do, do all to the glory of God."},
    {"date": (7, 13), "name": "St. Henry", "rank": "Optional Memorial", "category": "king",
     "blurb": "A Holy Roman Emperor remembered for his personal piety and for founding dioceses and monasteries.",
     "verse_ref": "Matthew 6:33", "verse_text": "Seek ye first the kingdom of God, and his justice, and all these things shall be added unto you."},
    {"date": (7, 14), "name": "St. Kateri Tekakwitha, Virgin", "rank": "Optional Memorial", "category": "virgin",
     "blurb": "'Lily of the Mohawks,' the first Native American canonized saint, who faced fierce opposition from her own community after her conversion.",
     "verse_ref": "2 Corinthians 5:17", "verse_text": "If then any be a new creature in Christ, old things are passed away: behold, all things are made new."},
    {"date": (7, 15), "name": "St. Bonaventure, Bishop and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "The 'Seraphic Doctor,' a close friend of Aquinas who led the Franciscans and wrote on the soul's journey toward God.",
     "verse_ref": "Psalm 34:8", "verse_text": "O taste, and see that the Lord is sweet: blessed is the man that hopeth in him."},
    {"date": (7, 16), "name": "Our Lady of Mount Carmel", "rank": "Optional Memorial", "category": "marian",
     "blurb": "Honors Mary under the title connected to the Carmelite order, whose roots trace back to the prophet Elijah on Mount Carmel.",
     "verse_ref": "1 Kings 18:44", "verse_text": "Behold a little cloud arose out of the sea like a man's foot."},
    {"date": (7, 20), "name": "St. Apollinaris, Bishop and Martyr", "rank": "Optional Memorial", "category": "bishop_martyr",
     "blurb": "Tradition holds he was a disciple of St. Peter and became the first bishop of Ravenna before his martyrdom.",
     "verse_ref": "2 Timothy 2:2", "verse_text": "The things which thou hast heard of me... the same commend to faithful men, who shall be fit to teach others also."},
    {"date": (7, 21), "name": "St. Lawrence of Brindisi, Priest and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "A Capuchin linguist who rallied Christian troops against an Ottoman invasion while carrying nothing but a crucifix into battle.",
     "verse_ref": "Ephesians 6:17", "verse_text": "And take unto you... the sword of the Spirit (which is the word of God)."},
    {"date": (7, 22), "name": "St. Mary Magdalene", "rank": "Memorial", "category": "disciple",
     "blurb": "Freed by Jesus from seven demons, she stood at the foot of the Cross and became the first witness of the Resurrection.",
     "verse_ref": "John 20:16-17", "verse_text": "Jesus saith to her: Mary. She turning, saith to him: Rabboni... Go to my brethren, and say to them."},
    {"date": (7, 23), "name": "St. Bridget of Sweden, Religious", "rank": "Optional Memorial", "category": "religious",
     "blurb": "A noblewoman and mother of eight who became a mystic and founded a religious order after her husband's death.",
     "verse_ref": "Proverbs 31:28", "verse_text": "Her children rose up, and called her blessed."},
    {"date": (7, 24), "name": "St. Sharbel Makhluf, Priest", "rank": "Optional Memorial", "category": "founder",
     "blurb": "A Lebanese Maronite hermit-monk known for intense devotion to the Eucharist and extraordinary personal austerity.",
     "verse_ref": "John 6:56", "verse_text": "He that eateth my flesh, and drinketh my blood, abideth in me, and I in him."},
    {"date": (7, 25), "name": "St. James, Apostle", "rank": "Feast", "category": "apostle",
     "blurb": "Brother of John and the first of the Twelve to be martyred, beheaded by Herod Agrippa.",
     "verse_ref": "Acts 12:1-2", "verse_text": "And Herod... killed James, the brother of John, with the sword."},
    {"date": (7, 26), "name": "Sts. Joachim and Anne, Parents of the Blessed Virgin Mary", "rank": "Memorial", "category": "special",
     "blurb": "Honors the grandparents of Jesus by tradition, and all grandparents who quietly hand on the faith to the next generation.",
     "verse_ref": "2 Timothy 1:5", "verse_text": "Bearing in mind that faith which is in thee unfeigned, which also dwelt first in thy grandmother."},
    {"date": (7, 29), "name": "Sts. Martha, Mary, and Lazarus", "rank": "Memorial", "category": "disciple",
     "blurb": "Close friends of Jesus in Bethany -- Martha who served, Mary who sat at his feet, and Lazarus, whom he raised from the dead.",
     "verse_ref": "John 11:25", "verse_text": "I am the resurrection, and the life: he that believeth in me, although he be dead, shall live."},
    {"date": (7, 30), "name": "St. Peter Chrysologus, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "Called 'Golden-Worded' for his short, clear sermons that made theology accessible to ordinary people.",
     "verse_ref": "Matthew 13:23", "verse_text": "But he that received the seed upon good ground, is he that heareth the word, and understandeth."},
    {"date": (7, 31), "name": "St. Ignatius of Loyola, Priest", "rank": "Memorial", "category": "founder",
     "blurb": "A soldier wounded in battle who converted while recovering and reading the lives of the saints, later founding the Jesuits.",
     "verse_ref": "Philippians 3:7-8", "verse_text": "But the things that were gain to me, the same I have counted loss for Christ."},

    {"date": (8, 1), "name": "St. Alphonsus Liguori, Bishop and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Gave up a law career after realizing its emptiness, later founding the Redemptorists and writing extensively on moral theology.",
     "verse_ref": "James 1:5", "verse_text": "And if any of you want wisdom, let him ask of God, who giveth to all men abundantly."},
    {"date": (8, 4), "name": "St. John Vianney, Priest", "rank": "Memorial", "category": "priest",
     "blurb": "The Curé of Ars, who struggled academically in seminary yet spent up to sixteen hours a day hearing confessions.",
     "verse_ref": "Luke 15:7", "verse_text": "There shall be joy in heaven upon one sinner that doth penance, more than upon ninety-nine just who need not penance."},
    {"date": (8, 5), "name": "The Dedication of the Basilica of St. Mary Major", "rank": "Optional Memorial", "category": "marian",
     "blurb": "Tradition holds Mary indicated where this Roman basilica should be built through a miraculous summer snowfall.",
     "verse_ref": "Revelation 12:1", "verse_text": "And a great sign appeared in heaven: A woman clothed with the sun, and the moon under her feet, and on her head a crown of twelve stars."},
    {"date": (8, 7), "name": "St. Cajetan, Priest", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Theatines to work for the reform of the clergy and care for the sick and poor. (Some places instead keep St. Sixtus II and Companions, a pope and his deacons martyred together in 258 while celebrating the liturgy.)",
     "verse_ref": "James 2:17", "verse_text": "Even so faith, if it have not works, is dead in itself."},
    {"date": (8, 8), "name": "St. Dominic, Priest", "rank": "Memorial", "category": "founder",
     "blurb": "Founded the Order of Preachers to combat heresy through learning, preaching, and radical poverty.",
     "verse_ref": "Romans 10:17", "verse_text": "Faith then cometh by hearing; and hearing by the word of Christ."},
    {"date": (8, 9), "name": "St. Teresa Benedicta of the Cross (Edith Stein), Virgin and Martyr", "rank": "Feast", "category": "virgin_martyr",
     "blurb": "A Jewish philosopher who converted to Catholicism and became a Carmelite nun, killed at Auschwitz for her Jewish heritage.",
     "verse_ref": "Romans 8:38-39", "verse_text": "Neither death, nor life... shall be able to separate us from the love of God, which is in Christ Jesus our Lord."},
    {"date": (8, 10), "name": "St. Lawrence, Deacon and Martyr", "rank": "Feast", "category": "deacon_martyr",
     "blurb": "Gave the Church's treasures to the poor when a Roman prefect demanded them, then was martyred on a gridiron -- reportedly joking, 'turn me over, I'm done on this side.'",
     "verse_ref": "2 Corinthians 9:7", "verse_text": "For God loveth a cheerful giver."},
    {"date": (8, 11), "name": "St. Clare, Virgin", "rank": "Memorial", "category": "founder",
     "blurb": "Followed St. Francis of Assisi's example and founded the Poor Clares, embracing radical poverty.",
     "verse_ref": "Matthew 19:21", "verse_text": "Go sell what thou hast, and give to the poor... and come, follow me."},
    {"date": (8, 13), "name": "Sts. Pontian, Pope, and Hippolytus, Priest, Martyrs", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "A pope and a priest who had once opposed him, reconciled before both died together as exiled slaves in the Sardinian mines.",
     "verse_ref": "John 17:21", "verse_text": "That they all may be one, as thou, Father, in me, and I in thee."},
    {"date": (8, 14), "name": "St. Maximilian Kolbe, Priest and Martyr", "rank": "Memorial", "category": "martyr",
     "blurb": "A Franciscan friar who volunteered to die in place of a stranger, a husband and father, in the starvation bunker at Auschwitz.",
     "verse_ref": "John 15:13", "verse_text": "Greater love than this no man hath, that a man lay down his life for his friends."},
    {"date": (8, 16), "name": "St. Stephen of Hungary", "rank": "Optional Memorial", "category": "king",
     "blurb": "The first King of Hungary, who established Christianity in his kingdom and built up churches and care for the poor.",
     "verse_ref": "Psalm 72:12", "verse_text": "For he shall deliver the poor from the mighty: and the needy that had no helper."},
    {"date": (8, 19), "name": "St. John Eudes, Priest", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Eudists and promoted devotion to the Sacred Hearts of Jesus and Mary before it was widespread.",
     "verse_ref": "Ephesians 3:17-19", "verse_text": "That Christ may dwell by faith in your hearts... to know also the charity of Christ."},
    {"date": (8, 20), "name": "St. Bernard, Abbot and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "The 'Mellifluous Doctor,' a Cistercian abbot renowned for his preaching, his devotion to Mary, and his reform of monastic life.",
     "verse_ref": "Philippians 1:21", "verse_text": "For to me, to live is Christ: and to die is gain."},
    {"date": (8, 21), "name": "St. Pius X, Pope", "rank": "Memorial", "category": "pope",
     "blurb": "Encouraged frequent and early Communion for children, choosing as his motto 'to restore all things in Christ.'",
     "verse_ref": "Ephesians 1:10", "verse_text": "That in the dispensation of the fulness of times, he might re-establish all things in Christ, that are in heaven and on earth."},
    {"date": (8, 22), "name": "The Queenship of the Blessed Virgin Mary", "rank": "Memorial", "category": "marian",
     "blurb": "Honors Mary as Queen of Heaven, crowned in glory because of her closeness to her Son the King.",
     "verse_ref": "Revelation 12:1", "verse_text": "And a great sign appeared in heaven: A woman clothed with the sun, and the moon under her feet, and on her head a crown of twelve stars."},
    {"date": (8, 23), "name": "St. Rose of Lima, Virgin", "rank": "Optional Memorial", "category": "virgin",
     "blurb": "The first canonized saint of the Americas, who embraced extreme penance in imitation of St. Catherine of Siena.",
     "verse_ref": "2 Corinthians 12:9-10", "verse_text": "For when I am weak, then am I powerful."},
    {"date": (8, 24), "name": "St. Bartholomew, Apostle", "rank": "Feast", "category": "apostle",
     "blurb": "Often identified with Nathanael, whom Jesus described as an Israelite without guile the moment they met.",
     "verse_ref": "John 1:47", "verse_text": "Behold an Israelite indeed, in whom there is no guile."},
    {"date": (8, 25), "name": "St. Joseph Calasanz, Priest", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Piarists and opened some of the first free public schools in Europe for poor children.",
     "verse_ref": "Proverbs 22:6", "verse_text": "Train up a child in the way he should go: and when he is old he will not depart from it."},
    {"date": (8, 27), "name": "St. Monica", "rank": "Memorial", "category": "widow",
     "blurb": "Prayed and wept for nearly twenty years for the conversion of her wayward son, following him from Africa to Italy.",
     "verse_ref": "Luke 18:1", "verse_text": "We ought always to pray, and not to faint."},
    {"date": (8, 28), "name": "St. Augustine, Bishop and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Monica's son -- a former hedonist who converted after hearing a child's voice tell him to 'take up and read' Scripture in a garden, and became the greatest Doctor of the West.",
     "verse_ref": "Romans 13:13-14", "verse_text": "Let us walk honestly, as in the day... But put ye on the Lord Jesus Christ."},
    {"date": (8, 29), "name": "The Passion (Beheading) of St. John the Baptist", "rank": "Memorial", "category": "martyr",
     "blurb": "Killed by Herod at the request of Herodias's daughter, after John had publicly condemned Herod's unlawful marriage.",
     "verse_ref": "Mark 6:18", "verse_text": "For John said to Herod: It is not lawful for thee to have thy brother's wife."},

    {"date": (9, 3), "name": "St. Gregory the Great, Pope and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Sent missionaries to evangelize England, reformed the Church's liturgy and chant, and chose for himself the title 'Servant of the Servants of God.'",
     "verse_ref": "Mark 10:44", "verse_text": "And whosoever will be first among you, shall be the servant of all."},
    {"date": (9, 5), "name": "St. Teresa of Calcutta, Religious", "rank": "Optional Memorial", "category": "founder",
     "blurb": "An Albanian nun who left convent life to serve Kolkata's poorest and dying, founding the Missionaries of Charity.",
     "verse_ref": "Matthew 25:40", "verse_text": "Amen I say to you, as long as you did it to one of these my least brethren, you did it to me."},
    {"date": (9, 8), "name": "The Nativity of the Blessed Virgin Mary", "rank": "Feast", "category": "marian",
     "blurb": "Celebrates the birth of the woman through whom the Savior of the world would come.",
     "verse_ref": "Isaiah 11:1", "verse_text": "And there shall come forth a rod out of the root of Jesse, and a flower shall rise up out of his root."},
    {"date": (9, 9), "name": "St. Peter Claver, Priest", "rank": "Optional Memorial", "category": "missionary",
     "blurb": "A Jesuit missionary who ministered to enslaved Africans arriving in Cartagena, calling himself 'slave of the slaves forever.'",
     "verse_ref": "1 Corinthians 9:19", "verse_text": "Whereas I was free... I made myself the servant of all, that I might gain the more."},
    {"date": (9, 12), "name": "The Most Holy Name of Mary", "rank": "Optional Memorial", "category": "marian",
     "blurb": "Honors the name given to the mother of Jesus, invoked by countless generations of the faithful.",
     "verse_ref": "Luke 1:28", "verse_text": "Hail, full of grace, the Lord is with thee: blessed art thou among women."},
    {"date": (9, 13), "name": "St. John Chrysostom, Bishop and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Called 'Golden-Mouthed' for his preaching, he was exiled for denouncing the corruption of the imperial court in Constantinople.",
     "verse_ref": "2 Timothy 4:2", "verse_text": "Preach the word: be instant in season, out of season: reprove, entreat, rebuke in all patience and doctrine."},
    {"date": (9, 15), "name": "Our Lady of Sorrows", "rank": "Memorial", "category": "marian",
     "blurb": "Remembers Mary's sorrows, above all her presence at the foot of the Cross as her son was put to death.",
     "verse_ref": "John 19:25-27", "verse_text": "Now there stood by the cross of Jesus, his mother... Woman, behold thy son."},
    {"date": (9, 16), "name": "Sts. Cornelius, Pope, and Cyprian, Bishop, Martyrs", "rank": "Memorial", "category": "pope_martyr",
     "blurb": "A pope and a bishop who corresponded on how to keep the Church unified during and after persecution, both later martyred themselves.",
     "verse_ref": "Ephesians 4:3", "verse_text": "Careful to keep the unity of the Spirit in the bond of peace."},
    {"date": (9, 17), "name": "St. Robert Bellarmine, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "A Jesuit cardinal who wrote catechisms and defended Catholic teaching during the controversies of the Reformation.",
     "verse_ref": "1 Peter 3:15", "verse_text": "Being ready always to satisfy every one that asketh you a reason of that hope which is in you."},
    {"date": (9, 19), "name": "St. Januarius, Bishop and Martyr", "rank": "Optional Memorial", "category": "bishop_martyr",
     "blurb": "Bishop of Naples martyred under Diocletian; a vial reputed to hold his blood is said to periodically liquefy to this day.",
     "verse_ref": "Revelation 12:11", "verse_text": "And they overcame him by the blood of the Lamb, and by the word of their testimony."},
    {"date": (9, 20), "name": "Sts. Andrew Kim Taegon, Paul Chong Hasang, and Companions, Martyrs", "rank": "Memorial", "category": "martyr",
     "blurb": "Korean martyrs -- priests, catechists, and laypeople -- from a Church that was founded and led entirely by laypeople before any missionary priest ever arrived.",
     "verse_ref": "1 Peter 2:9", "verse_text": "But you are a chosen generation, a kingly priesthood, a holy nation."},
    {"date": (9, 21), "name": "St. Matthew, Apostle and Evangelist", "rank": "Feast", "category": "evangelist",
     "blurb": "A tax collector called away from his booth by two words from Jesus, who went on to write the first Gospel.",
     "verse_ref": "Matthew 9:9", "verse_text": "And Jesus... saw a man sitting in the custom house, named Matthew; and he saith to him: Follow me. And he arose up, and followed him."},
    {"date": (9, 23), "name": "St. Pius of Pietrelcina (Padre Pio), Priest", "rank": "Memorial", "category": "priest",
     "blurb": "A Capuchin friar who bore the wounds of Christ's Passion in his own body for fifty years and was renowned as a confessor.",
     "verse_ref": "Galatians 6:17", "verse_text": "For I bear the marks of the Lord Jesus in my body."},
    {"date": (9, 26), "name": "Sts. Cosmas and Damian, Martyrs", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "Twin physician brothers who treated the sick for free and were martyred under Diocletian.",
     "verse_ref": "Matthew 10:8", "verse_text": "Freely have you received, freely give."},
    {"date": (9, 27), "name": "St. Vincent de Paul, Priest", "rank": "Memorial", "category": "founder",
     "blurb": "Once briefly enslaved himself, he devoted his life to serving the poor, founding the Vincentians and the Daughters of Charity.",
     "verse_ref": "Matthew 25:40", "verse_text": "Amen I say to you, as long as you did it to one of these my least brethren, you did it to me."},
    {"date": (9, 28), "name": "St. Wenceslaus, Martyr", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "Duke of Bohemia (the 'Good King Wenceslas' of the Christmas carol), murdered by his own brother in a struggle for power.",
     "verse_ref": "Matthew 5:44", "verse_text": "Love your enemies: do good to them that hate you."},
    {"date": (9, 29), "name": "Sts. Michael, Gabriel, and Raphael, Archangels", "rank": "Feast", "category": "angels",
     "blurb": "Michael the warrior prince, Gabriel the messenger of the Annunciation, and Raphael the healer and guide of the Book of Tobit.",
     "verse_ref": "Revelation 12:7", "verse_text": "And there was a great battle in heaven: Michael and his angels fought."},
    {"date": (9, 30), "name": "St. Jerome, Priest and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Translated the entire Bible into Latin, producing the Vulgate, and famously taught that 'ignorance of Scripture is ignorance of Christ.'",
     "verse_ref": "2 Timothy 3:16", "verse_text": "All scripture, inspired of God, is profitable to teach, to reprove, to correct, to instruct in justice."},

    {"date": (10, 1), "name": "St. Thérèse of the Child Jesus, Virgin and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "A Carmelite nun who died young of tuberculosis, remembered for her 'Little Way' of doing small, ordinary things with great love.",
     "verse_ref": "Matthew 18:3", "verse_text": "Unless you be converted, and become as little children, you shall not enter into the kingdom of heaven."},
    {"date": (10, 2), "name": "The Holy Guardian Angels", "rank": "Memorial", "category": "angels",
     "blurb": "Celebrates the angels God assigns to watch over and protect each person.",
     "verse_ref": "Psalm 91:11", "verse_text": "For he hath given his angels charge over thee; to keep thee in all thy ways."},
    {"date": (10, 5), "name": "St. Faustina Kowalska, Religious", "rank": "Optional Memorial", "category": "religious",
     "blurb": "A Polish nun to whom Christ appeared with a message of Divine Mercy, which she recorded in her diary and which Pope John Paul II later spread worldwide.",
     "verse_ref": "Psalm 103:8", "verse_text": "The Lord is compassionate and merciful: longsuffering and plenteous in mercy."},
    {"date": (10, 6), "name": "St. Bruno, Priest", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Carthusians, the strictest of the contemplative orders, built around silence and solitude before God.",
     "verse_ref": "Psalm 46:10", "verse_text": "Be still, and see that I am God."},
    {"date": (10, 7), "name": "Our Lady of the Rosary", "rank": "Memorial", "category": "marian",
     "blurb": "Instituted after a Christian naval victory at Lepanto in 1571, credited to Christians praying the Rosary together.",
     "verse_ref": "Luke 1:28", "verse_text": "Hail, full of grace, the Lord is with thee: blessed art thou among women."},
    {"date": (10, 9), "name": "St. John Leonardi, Priest", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Clerics Regular of the Mother of God and worked for clergy reform and the Church's missionary efforts. (Some places instead keep St. Denis and Companions, a bishop of Paris beheaded with two companions for evangelizing Roman Gaul.)",
     "verse_ref": "Mark 16:15", "verse_text": "Go ye into the whole world, and preach the gospel to every creature."},
    {"date": (10, 11), "name": "St. John XXIII, Pope", "rank": "Optional Memorial", "category": "pope",
     "blurb": "'Good Pope John,' who convened the Second Vatican Council and became known worldwide for his warmth and openness.",
     "verse_ref": "John 13:34-35", "verse_text": "A new commandment I give unto you: That you love one another... by this shall all men know that you are my disciples."},
    {"date": (10, 14), "name": "St. Callistus I, Pope and Martyr", "rank": "Optional Memorial", "category": "pope_martyr",
     "blurb": "A former slave who became pope, known -- and criticized in his day -- for reconciling grave sinners back into the Church.",
     "verse_ref": "Luke 15:20", "verse_text": "And his father, seeing him, was moved with compassion, and running to him fell upon his neck, and kissed him."},
    {"date": (10, 15), "name": "St. Teresa of Avila, Virgin and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "A Carmelite mystic and reformer who wrote 'The Interior Castle,' mapping the soul's journey deeper into union with God.",
     "verse_ref": "Psalm 27:8", "verse_text": "My heart hath said to thee: My face hath sought thee: thy face, O Lord, will I still seek."},
    {"date": (10, 16), "name": "St. Margaret Mary Alacoque, Virgin", "rank": "Optional Memorial", "category": "virgin",
     "blurb": "A Visitation nun who received visions of Christ's Sacred Heart and spread devotion to it throughout the Church. (Some places instead keep St. Hedwig, a widowed duchess who gave away her wealth and entered a convent she had founded.)",
     "verse_ref": "John 19:34", "verse_text": "But one of the soldiers with a spear opened his side, and immediately there came out blood and water."},
    {"date": (10, 17), "name": "St. Ignatius of Antioch, Bishop and Martyr", "rank": "Memorial", "category": "bishop_martyr",
     "blurb": "A disciple of John who wrote letters to churches while being transported to Rome for execution, eager to be, in his words, 'the wheat of God.'",
     "verse_ref": "Philippians 1:21", "verse_text": "For to me, to live is Christ: and to die is gain."},
    {"date": (10, 18), "name": "St. Luke, Evangelist", "rank": "Feast", "category": "evangelist",
     "blurb": "A physician and Gentile convert who traveled with Paul and wrote both the Gospel of Luke and the Acts of the Apostles.",
     "verse_ref": "Colossians 4:14", "verse_text": "Luke, the most dear physician, saluteth you."},
    {"date": (10, 19), "name": "Sts. John de Brébeuf, Isaac Jogues, and Companions, Martyrs", "rank": "Optional Memorial", "category": "martyr",
     "blurb": "French Jesuit missionaries martyred in North America in the 17th century while bringing the Gospel to Native peoples.",
     "verse_ref": "Acts 20:24", "verse_text": "Neither do I count my life more precious than myself, so that I may consummate my course."},
    {"date": (10, 20), "name": "St. Paul of the Cross, Priest", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Passionists to keep alive devotion to the suffering and death of Christ.",
     "verse_ref": "Galatians 6:14", "verse_text": "But God forbid that I should glory, save in the cross of our Lord Jesus Christ."},
    {"date": (10, 22), "name": "St. John Paul II, Pope", "rank": "Optional Memorial", "category": "pope",
     "blurb": "Pope for 27 years, who survived an assassination attempt and played a key role in the fall of Communism in Eastern Europe, urging the world to 'be not afraid.'",
     "verse_ref": "2 Timothy 1:7", "verse_text": "For God hath not given us the spirit of fear: but of power, and of love, and of sobriety."},
    {"date": (10, 23), "name": "St. John of Capistrano, Priest", "rank": "Optional Memorial", "category": "priest",
     "blurb": "A Franciscan friar and former soldier who rallied Christian troops at the Siege of Belgrade against an Ottoman invasion.",
     "verse_ref": "2 Timothy 4:7", "verse_text": "I have fought a good fight, I have finished my course, I have kept the faith."},
    {"date": (10, 24), "name": "St. Anthony Mary Claret, Bishop", "rank": "Optional Memorial", "category": "founder",
     "blurb": "Founded the Claretians and became a prolific missionary, writer, and confessor to the Queen of Spain.",
     "verse_ref": "Romans 10:15", "verse_text": "How beautiful are the feet of them that preach the gospel of peace."},
    {"date": (10, 28), "name": "Sts. Simon and Jude, Apostles", "rank": "Feast", "category": "apostle",
     "blurb": "Jude -- patron of desperate causes -- once asked Jesus at the Last Supper why he would reveal himself only to the disciples and not the world.",
     "verse_ref": "John 14:22", "verse_text": "Lord, how is it, that thou wilt manifest thyself to us, and not to the world?"},

    {"date": (11, 3), "name": "St. Martin de Porres, Religious", "rank": "Optional Memorial", "category": "religious",
     "blurb": "A Peruvian Dominican brother of mixed race who faced discrimination yet became known for humility and tireless care of the poor, sick, and even animals.",
     "verse_ref": "James 2:5", "verse_text": "Hath not God chosen the poor in this world, rich in faith?"},
    {"date": (11, 4), "name": "St. Charles Borromeo, Bishop", "rank": "Memorial", "category": "bishop",
     "blurb": "Cardinal Archbishop of Milan who personally cared for plague victims and led key reforms after the Council of Trent.",
     "verse_ref": "John 10:11", "verse_text": "I am the good shepherd. The good shepherd giveth his life for his sheep."},
    {"date": (11, 9), "name": "The Dedication of the Lateran Basilica", "rank": "Feast", "category": "special",
     "blurb": "Celebrates the Pope's own cathedral church in Rome -- the 'mother church' of the whole world -- first dedicated in the 4th century.",
     "verse_ref": "1 Corinthians 3:16", "verse_text": "Know you not, that you are the temple of God, and that the Spirit of God dwelleth in you?"},
    {"date": (11, 10), "name": "St. Leo the Great, Pope and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Met Attila the Hun outside Rome and persuaded him not to sack the city, and defended orthodox teaching about Christ at the Council of Chalcedon.",
     "verse_ref": "Ephesians 4:5", "verse_text": "One Lord, one faith, one baptism."},
    {"date": (11, 11), "name": "St. Martin of Tours, Bishop", "rank": "Memorial", "category": "bishop",
     "blurb": "A Roman soldier who famously cut his cloak in half to share with a freezing beggar, later seeing in a dream that the beggar had been Christ.",
     "verse_ref": "Matthew 25:35-36", "verse_text": "I was... naked, and you covered me... As long as you did it to one of these my least brethren, you did it to me."},
    {"date": (11, 12), "name": "St. Josaphat, Bishop and Martyr", "rank": "Memorial", "category": "bishop_martyr",
     "blurb": "A Byzantine-rite bishop who worked for the reunion of Orthodox and Catholic Christians and was killed by a mob opposed to it.",
     "verse_ref": "John 17:21", "verse_text": "That they all may be one, as thou, Father, in me, and I in thee."},
    {"date": (11, 13), "name": "St. Frances Xavier Cabrini, Virgin", "rank": "Memorial", "category": "founder",
     "blurb": "An Italian-American nun who founded a missionary order and devoted her life to serving Italian immigrants in the United States.",
     "verse_ref": "Matthew 25:35", "verse_text": "I was a stranger, and you took me in."},
    {"date": (11, 15), "name": "St. Albert the Great, Bishop and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "Called the 'Universal Doctor,' he taught Thomas Aquinas and was a pioneering scientist as well as a theologian.",
     "verse_ref": "Proverbs 4:7", "verse_text": "The beginning of wisdom, get wisdom."},
    {"date": (11, 16), "name": "St. Gertrude, Virgin", "rank": "Optional Memorial", "category": "virgin",
     "blurb": "A German Benedictine mystic whose visions of Christ's Sacred Heart deeply shaped medieval devotional life. (Some places instead keep St. Margaret of Scotland, a queen known for her personal piety and tireless care for the poor and orphans.)",
     "verse_ref": "Jeremiah 31:3", "verse_text": "I have loved thee with an everlasting love."},
    {"date": (11, 17), "name": "St. Elizabeth of Hungary, Religious", "rank": "Memorial", "category": "religious",
     "blurb": "A Hungarian princess widowed young, who gave away her wealth to the poor and built hospitals before dying as a Franciscan tertiary.",
     "verse_ref": "1 John 3:17", "verse_text": "He that hath the substance of this world, and shall see his brother in need, and shall shut up his bowels from him: how doth the charity of God abide in him?"},
    {"date": (11, 18), "name": "The Dedication of the Basilicas of Sts. Peter and Paul", "rank": "Optional Memorial", "category": "special",
     "blurb": "Honors the two great basilicas built in Rome over the tombs of the Apostles Peter and Paul.",
     "verse_ref": "Ephesians 2:20", "verse_text": "Built upon the foundation of the apostles and prophets, Jesus Christ himself being the chief corner stone."},
    {"date": (11, 21), "name": "The Presentation of the Blessed Virgin Mary", "rank": "Memorial", "category": "marian",
     "blurb": "An ancient tradition recalling Mary being presented and consecrated to God's service in the Temple as a child.",
     "verse_ref": "Luke 1:48", "verse_text": "Because he hath regarded the humility of his handmaid: for behold from henceforth all generations shall call me blessed."},
    {"date": (11, 22), "name": "St. Cecilia, Virgin and Martyr", "rank": "Memorial", "category": "virgin_martyr",
     "blurb": "A Roman virgin martyr, patroness of musicians, remembered for singing to God in her heart even on her wedding day.",
     "verse_ref": "Ephesians 5:19", "verse_text": "Speaking to yourselves in psalms, and hymns, and spiritual canticles, singing and making melody in your hearts to the Lord."},
    {"date": (11, 23), "name": "St. Columban, Abbot", "rank": "Optional Memorial", "category": "founder",
     "blurb": "An Irish monk-missionary who founded monasteries across Gaul and Italy, unafraid to publicly correct the morals of Frankish rulers. (Some places instead keep St. Clement I, the third successor of Peter as pope, martyred in exile for continuing to lead the Church.)",
     "verse_ref": "2 Timothy 4:2", "verse_text": "Preach the word: be instant in season, out of season: reprove, entreat, rebuke in all patience and doctrine."},
    {"date": (11, 24), "name": "St. Andrew Dung-Lac and Companions, Martyrs", "rank": "Memorial", "category": "martyr",
     "blurb": "Honors 117 Vietnamese martyrs -- priests, catechists, and laypeople -- killed across centuries of persecution.",
     "verse_ref": "Revelation 7:14", "verse_text": "These are they who are come out of great tribulation, and have washed their robes, and have made them white in the blood of the Lamb."},
    {"date": (11, 30), "name": "St. Andrew, Apostle", "rank": "Feast", "category": "apostle",
     "blurb": "The first of the Twelve called by Jesus, who immediately went and brought his brother Simon Peter to meet him.",
     "verse_ref": "John 1:41-42", "verse_text": "He findeth first his brother Simon... and he brought him to Jesus."},

    {"date": (12, 3), "name": "St. Francis Xavier, Priest", "rank": "Memorial", "category": "missionary",
     "blurb": "A co-founder of the Jesuits who became one of history's greatest missionaries, evangelizing across India and Japan and dying still hoping to reach China.",
     "verse_ref": "1 Corinthians 9:22", "verse_text": "I became all things to all men, that I might save all."},
    {"date": (12, 4), "name": "St. John Damascene, Priest and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "The last of the great Eastern Doctors, who defended the veneration of icons during the Iconoclast controversy.",
     "verse_ref": "Colossians 1:15", "verse_text": "Who is the image of the invisible God, the firstborn of every creature."},
    {"date": (12, 6), "name": "St. Nicholas, Bishop", "rank": "Optional Memorial", "category": "bishop",
     "blurb": "Bishop of Myra famous for secretly giving dowries to three poor sisters to save them from being sold into slavery -- the root of the Santa Claus legend.",
     "verse_ref": "Matthew 6:3-4", "verse_text": "But when thou dost alms, let not thy left hand know what thy right hand doth... And thy Father who seeth in secret, will repay thee."},
    {"date": (12, 7), "name": "St. Ambrose, Bishop and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "Bishop of Milan who baptized Augustine and once required Emperor Theodosius to do public penance for ordering a massacre.",
     "verse_ref": "Acts 5:29", "verse_text": "We ought to obey God, rather than men."},
    {"date": (12, 9), "name": "St. Juan Diego Cuauhtlatoatzin", "rank": "Optional Memorial", "category": "special",
     "blurb": "A poor indigenous convert in 16th-century Mexico to whom Our Lady of Guadalupe appeared, asking that a church be built on Tepeyac hill.",
     "verse_ref": "1 Corinthians 1:27", "verse_text": "But the foolish things of the world hath God chosen, that he may confound the wise."},
    {"date": (12, 11), "name": "St. Damasus I, Pope", "rank": "Optional Memorial", "category": "pope",
     "blurb": "The pope who commissioned St. Jerome to produce the Latin Vulgate translation of the Bible.",
     "verse_ref": "2 Timothy 3:16", "verse_text": "All scripture, inspired of God, is profitable to teach, to reprove, to correct, to instruct in justice."},
    {"date": (12, 13), "name": "St. Lucy, Virgin and Martyr", "rank": "Memorial", "category": "virgin_martyr",
     "blurb": "A Sicilian virgin martyr whose name means 'light,' consecrated to Christ and martyred under Diocletian.",
     "verse_ref": "John 8:12", "verse_text": "I am the light of the world: he that followeth me, walketh not in darkness."},
    {"date": (12, 14), "name": "St. John of the Cross, Priest and Doctor", "rank": "Memorial", "category": "doctor",
     "blurb": "A Carmelite friar imprisoned by his own confreres, who wrote 'Dark Night of the Soul' out of that very darkness.",
     "verse_ref": "Psalm 23:4", "verse_text": "For though I should walk in the midst of the shadow of death, I will fear no evils, for thou art with me."},
    {"date": (12, 21), "name": "St. Peter Canisius, Priest and Doctor", "rank": "Optional Memorial", "category": "doctor",
     "blurb": "A Jesuit whose catechisms shaped Catholic education across Germany for centuries during the Counter-Reformation.",
     "verse_ref": "Deuteronomy 6:6-7", "verse_text": "And these words... thou shalt tell them to thy children."},
    {"date": (12, 23), "name": "St. John of Kanty, Priest", "rank": "Optional Memorial", "category": "priest",
     "blurb": "A Polish priest and professor renowned for extreme generosity to the poor despite his own learning and status.",
     "verse_ref": "Luke 6:38", "verse_text": "Give, and it shall be given to you."},
    {"date": (12, 27), "name": "St. John, Apostle and Evangelist", "rank": "Feast", "category": "evangelist",
     "blurb": "The 'beloved disciple' who cared for Mary after the Crucifixion, and the only apostle not to die a martyr's death.",
     "verse_ref": "John 19:26-27", "verse_text": "Woman, behold thy son... Behold thy mother. And from that hour, the disciple took her to his own."},
    {"date": (12, 29), "name": "St. Thomas Becket, Bishop and Martyr", "rank": "Optional Memorial", "category": "bishop_martyr",
     "blurb": "Archbishop of Canterbury murdered in his own cathedral by knights of King Henry II after conflicts over the Church's rights.",
     "verse_ref": "Acts 5:29", "verse_text": "We ought to obey God, rather than men."},
    {"date": (12, 31), "name": "St. Sylvester I, Pope", "rank": "Optional Memorial", "category": "pope",
     "blurb": "Pope during the reign of Constantine, whose legates presided over the Council of Nicaea in the newly peaceful era for the Church.",
     "verse_ref": "Acts 9:31", "verse_text": "Now the church had peace... and was edified."},
]

SAINTS_CALENDAR = {}
for _entry in _RAW_SAINTS:
    _key = _entry["date"]
    # Don't clobber a solemnity/feast already defined directly in FIXED_FEASTS
    if _key not in FIXED_FEASTS:
        SAINTS_CALENDAR[_key] = _build_saint_entry(
            _entry["name"], _entry["rank"], _entry["category"],
            blurb=_entry.get("blurb"),
            verse_ref=_entry.get("verse_ref"),
            verse_text=_entry.get("verse_text"),
        )

# Merge the saints into the main fixed-feast lookup table.
FIXED_FEASTS.update(SAINTS_CALENDAR)


# ---------------------------------------------------------------------------
# Year-dependent Sunday feasts that aren't tied to Easter
# (Holy Family, Baptism of the Lord) -- computed alongside the moveable ones.
# ---------------------------------------------------------------------------
def _sunday_on_or_before(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)


def get_extra_sunday_feasts(year: int) -> dict:
    """Feast of the Holy Family (Sunday within the Octave of Christmas, or
    Dec 30 if Christmas itself is a Sunday) and Baptism of the Lord (the
    Sunday after Jan 6, or the Monday after if Jan 6 falls on a Sunday)."""
    christmas = date(year, 12, 25)
    if christmas.weekday() == 6:  # Christmas is itself a Sunday
        holy_family = date(year, 12, 30)
    else:
        # First Sunday after Christmas, within Dec 26-31
        days_ahead = (6 - christmas.weekday()) % 7
        holy_family = christmas + timedelta(days=days_ahead or 7)

    epiphany = date(year, 1, 6)
    if epiphany.weekday() == 6:
        baptism = epiphany + timedelta(days=1)
    else:
        days_ahead = (6 - epiphany.weekday()) % 7
        baptism = epiphany + timedelta(days=days_ahead)

    return {
        _k(holy_family): {
            "name": "The Holy Family of Jesus, Mary, and Joseph",
            "rank": "Feast",
            "dos": ["Pray for your own family, however imperfect",
                    "Spend extra time with family today", "Ask the Holy Family's intercession for your household"],
            "donts": ["Don't compare your family to an idealized image -- the Holy Family knew hardship too (the flight into Egypt, poverty, misunderstanding)"],
            "verse_ref": "Luke 2:51",
            "verse_text": "And he went down with them, and came to Nazareth, and was subject to them.",
            "blurb": "Holds up Jesus, Mary, and Joseph as the model for every Christian family.",
        },
        _k(baptism): {
            "name": "The Baptism of the Lord",
            "rank": "Feast",
            "dos": ["Renew your own baptismal promises", "Thank God for your baptism and godparents/sponsors"],
            "donts": ["Don't treat your baptism as a one-time event with no bearing on today"],
            "verse_ref": "Matthew 3:17",
            "verse_text": "And behold a voice from heaven, saying: This is my beloved Son, in whom I am well pleased.",
            "blurb": "Marks the close of the Christmas season and Jesus' public revelation as the Son of God.",
        },
    }


def get_feast(target_date: date) -> dict | None:
    """
    Return the feast dict for the given date, or None if it's an ordinary day.
    Priority: Easter-based moveable feasts > Holy Family/Baptism of the Lord
    (also year-dependent, but not Easter-based) > fixed-date feasts and saints.
    """
    key = _k(target_date)

    moveable = get_moveable_feasts(target_date.year)
    if key in moveable:
        return moveable[key]

    extra_sundays = get_extra_sunday_feasts(target_date.year)
    if key in extra_sundays:
        return extra_sundays[key]

    if key in FIXED_FEASTS:
        return FIXED_FEASTS[key]

    return None
