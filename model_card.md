# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**Vibra**

---

## 2. Intended Use

**What kind of recommendations does it generate**

It takes a person's stated taste (favorite genre, favorite mood, target energy, and whether they like acoustic music) and scores every song in the catalog against that, then hands back the top 5. It's not predicting anything, it's just measuring how close each song is to what you already said you wanted.

**What assumptions does it make about the user**

It assumes the user actually knows and can state their preferences upfront, there's no listening history or behavior involved, just whatever four values you give it. It also assumes those preferences map cleanly onto the exact genre and mood strings in my catalog, which, as I found out, doesn't always hold up.

**Is this for real users or classroom exploration**

This is a classroom exploration project, not something built for real users. With only 18 songs and known issues like silent failures on genres that don't exist, I wouldn't hand this to an actual person expecting real music recommendations.

---

## 3. How the Model Works

Every song gets compared against what one person says they like, there's no "other users" involved at all, it's just this one profile against every song in the catalog.

A user profile is four things: their favorite genre, their favorite mood, how much energy they want (on a 0 to 1 scale), and whether they like acoustic music or not.

Each song gets a score built from four rules:

- If the song's genre matches the user's favorite genre, that's +2.0 points.
- If the song's mood matches the user's favorite mood, that's +1.0 point.
- Energy works differently, it's not just yes or no, it's how close the song's energy is to what the user asked for. A perfect match gets up to +2.0, and it gets smaller the further apart they are.
- If the song's acousticness lines up with whether the user likes acoustic music, that's +0.5.

Add all four up and that's the song's total score, out of a possible 5.5 if it hits everything perfectly. Every song in the catalog gets scored this way, then they're sorted highest to lowest, and the top 5 get shown as the recommendations.

I started with genre worth more than mood, and I wanted to test that before changing anything. I also thought about scoring on valence, danceability, and tempo too, but decided against it, those three stay in the dataset but don't affect the score, since I wanted to keep things simple and only score on the four things the user actually says they want.

---

## 4. Data

My catalog has 18 songs total, I started with 10 and added 8 more later to get more variety. Each song has genre, mood, energy, tempo, valence, danceability, and acousticness, but I only score on four of those: genre, mood, energy, and acousticness.

Genre-wise it's pretty spread out, 15 different genres across 18 songs (pop, lofi, rock, ambient, jazz, synthwave, indie pop, classical, hip hop, r&b, folk, electronic, ambient pop, metal, country). Only lofi has more than one song in most cases, it's got three (Midnight Coding, Library Rain, Focus Flow). Everything else is basically a single song representing that whole genre.

Moods are similar, chill shows up the most (three songs), everything else is one or two songs at most.

I didn't remove any of the original data, I only added to it. What's missing is any real depth per genre, since almost every genre only has one song, there's no way to recommend "more like this" within that genre if the one song doesn't happen to also match on mood or energy. There's also no lyrics, no artist history, no listening behavior, this is purely based on the attributes tagged to each song.

---

## 5. Strengths

**User types for which it gives reasonable results**

Users whose taste maps cleanly onto an actual genre/mood combo in my catalog get solid results, High-Energy Pop and Chill Lofi both came back with lists that felt right to me. Deep Intense Rock was probably the cleanest case, Storm Runner hit genre, mood, and energy all at once and won by a wide margin, exactly what I'd expect.

**Any patterns you think your scoring captures correctly**

The energy formula seems to genuinely work in both directions, not just favor "loud" songs. High-Energy Pop and Chill Lofi asked for almost opposite energy levels and got completely different top 5 lists with zero overlap.

**Cases where the recommendations matched your intuition**

The Chill Lofi results matched my intuition the most, Library Rain and Midnight Coding topping the list is exactly what I'd expect from someone who wants mellow, low-key music. Nothing in that top 5 felt like it snuck in for the wrong reason either, even the lower-scoring songs still sounded like they belonged on a chill playlist.

---

## 6. Limitations and Bias

Where the system struggles or behaves unfairly.

**Features it does not consider**

My dataset actually has tempo, valence, and danceability sitting right there in the CSV, and none of them get scored. The model only looks at genre, mood, energy, and acousticness. So two songs that are wildly different in tempo or danceability can end up scored identically if their genre/mood/energy/acousticness line up. That's a real blind spot, not a hypothetical one, the data's there, I'm just not using it.

**Genres or moods that are underrepresented**

With only 18 songs in the catalog, a bunch of genre/mood combos are represented by exactly one song. For example, there's only one true "rock/intense" song and only one "classical" song. That means the second you step even slightly outside a song's exact best-fit profile, there's nothing else in that lane to recommend the system has no real alternatives to offer, it just falls back to whatever's closest on the remaining criteria.

**Cases where the system overfits to one preference**

There's a structural bias baked into the scoring math itself, and I proved it out: the max score you can get with zero genre credit is 3.5 (mood 1.0 + energy 2.0 + acoustic 0.5), but a genre match alone only guarantees a floor of 2.0. That means a song with no genre match at all can mathematically outrank a true genre match. I saw this happen for real against a classical/happy profile, Sunrise City (pop, no genre match) scored 3.50 and beat out Autumn Piano Sketch (classical, an actual genre match) at 2.86. So the system can end up overfitting to energy/acoustic closeness instead of the thing the user actually asked for.

On top of that, compound genre names lose all genre credit because matching is exact-string only. "indie pop" doesn't match a "pop" preference, and "ambient pop" doesn't match "ambient", both scored zero genre credit even though these are obviously closely related genres. This isn't a one-off, I saw it happen in two separate tests.

**Ways the scoring might unintentionally favor some users**

Users whose taste maps cleanly onto exact genre/mood strings in the catalog get accurate results. Users whose taste is close but not exact (compound genres, adjacent moods) get quietly penalized without any indication that's what happened. And here's the part that makes it worse: the system never tells you when a requested genre or mood doesn't exist in the catalog at all, it just silently falls back to energy/acoustic scoring with no warning. So a "this genre doesn't exist in my catalog" result looks exactly the same as a "this genre exists but nothing scored high enough" result. A user has no way to tell the difference, which means the system can quietly fail a whole category of users without ever surfacing that it did.

My catalog's genre distribution is extremely uneven, 13 of my 15 genres have exactly one song, while lofi has three. That means a user whose favorite genre is lofi gets three chances at a genre-match bonus, and two of those songs also match "chill" mood, stacking bonuses, while a user who likes classical or metal has exactly one shot, with zero fallback if that one song's mood or energy happens to be off. I initially thought there was also a genre "gap" in the energy scoring around target_energy=0.6, but checking my actual data, that turned out to be wrong, Sunday Backroad sits at energy 0.58, which is a near-perfect match for a target of 0.6. So the real bias isn't in the energy formula itself, it's entirely a catalog composition problem: users whose taste happens to align with lofi/chill are structurally better served than users who like any of the 13 singleton genres, regardless of how well the scoring math works.

---

## 7. Evaluation

I ran 6 user profiles through the recommender. Three were realistic profiles meant to check normal behavior, and three were adversarial profiles I built specifically to try to break the scoring logic.

**Realistic profiles:**

- High-Energy Pop
- Chill Lofi
- Deep Intense Rock

**Adversarial profiles:**

- Sad Rave, genre, mood, and energy that all contradict each other (metal + melancholic + energy 0.95, but also `likes_acoustic: True`)
- Genre/Mood Ghost, a genre (`reggae`) and mood (`euphoric`) that don't exist anywhere in my catalog
- Zero Energy Absolutist, a boundary value, `target_energy = 0.0`

What I was looking for was mainly: does it crash, does it return garbage scores, and do the top 5 still make some kind of sense given whatever signal is actually available.

### High-Energy Pop

```
=== High-Energy Pop ===

Top recommendations:

Sunrise City - Score: 5.34
Because: genre match (+2.0), mood match (+1.0), energy closeness (+1.84), acousticness match (+0.5)

Gym Hero - Score: 4.44
Because: genre match (+2.0), energy closeness (+1.94), acousticness match (+0.5)

Rooftop Lights - Score: 3.22
Because: mood match (+1.0), energy closeness (+1.72), acousticness match (+0.5)

Storm Runner - Score: 2.48
Because: energy closeness (+1.98), acousticness match (+0.5)

Block Party Anthem - Score: 2.46
Because: energy closeness (+1.96), acousticness match (+0.5)
```

This one looked right — high-energy, upbeat songs at the top, genre and mood matches driving the highest scores.

### Chill Lofi (mood-first)

```
=== Chill Lofi (mood-first) ===

Top recommendations:

Library Rain - Score: 5.00
Because: genre match (+1.00), mood match (+2.50), energy closeness (+1.00), acousticness match (+0.50)

Midnight Coding - Score: 4.93
Because: genre match (+1.00), mood match (+2.50), energy closeness (+0.93), acousticness match (+0.50)

Spacewalk Thoughts - Score: 3.93
Because: mood match (+2.50), energy closeness (+0.93), acousticness match (+0.50)

Coffee Shop Stories - Score: 1.48
Because: energy closeness (+0.98), acousticness match (+0.50)

Old Porch Stories - Score: 1.47
Because: energy closeness (+0.97), acousticness match (+0.50)
```

Also matched my intuition — mellow, low-energy tracks up top, acoustic bonus applied consistently.

### Deep Intense Rock (energy-focused)

```
=== Deep Intense Rock (energy-focused) ===

Top recommendations:

Storm Runner - Score: 5.96
Because: genre match (+1.00), mood match (+1.00), energy closeness (+3.46), acousticness match (+0.50)

Gym Hero - Score: 4.89
Because: mood match (+1.00), energy closeness (+3.40), acousticness match (+0.50)

Block Party Anthem - Score: 3.93
Because: energy closeness (+3.43), acousticness match (+0.50)

Neon Horizon - Score: 3.86
Because: energy closeness (+3.36), acousticness match (+0.50)

Broken Amplifier - Score: 3.83
Because: energy closeness (+3.33), acousticness match (+0.50)
```

Straightforward — the top pick nails genre, mood, and energy all at once.

### Sad Rave (energy-focused, adversarial — contradictory preferences)

```
=== Sad Rave (energy-focused) ===

Top recommendations:

Broken Amplifier - Score: 4.50
Because: genre match (+1.00), energy closeness (+3.50)

Gym Hero - Score: 3.43
Because: energy closeness (+3.43)

Storm Runner - Score: 3.36
Because: energy closeness (+3.36)

Block Party Anthem - Score: 3.26
Because: energy closeness (+3.26)

Neon Horizon - Score: 3.19
Because: energy closeness (+3.19)
```

This is the profile I built to be internally contradictory (high-energy metal, but melancholic and acoustic-loving), and it didn't break anything. It just fell back to whatever criteria still lined up for each song, no crash, no invalid scores, just a genre match here, an energy match there.

### Genre/Mood Ghost (mood-first, adversarial — genre/mood not in catalog)

```
=== Genre/Mood Ghost (mood-first) ===

Top recommendations:

Night Drive Loop - Score: 1.35
Because: energy closeness (+0.85), acousticness match (+0.50)

Rooftop Lights - Score: 1.34
Because: energy closeness (+0.84), acousticness match (+0.50)

Neon Horizon - Score: 1.24
Because: energy closeness (+0.74), acousticness match (+0.50)

Block Party Anthem - Score: 1.22
Because: energy closeness (+0.72), acousticness match (+0.50)

Storm Runner - Score: 1.19
Because: energy closeness (+0.69), acousticness match (+0.50)
```

I asked for `reggae` and `euphoric`, neither of which exist anywhere in my catalog. The system didn't error out or flag anything, it just quietly dropped the genre and mood bonuses and ranked everything on energy and acousticness alone, still confidently returning 5 songs like nothing was wrong.

### Genre/Mood Ghost (default) — added for isolated comparison

```
=== Genre/Mood Ghost (default) ===

Top recommendations:

Night Drive Loop - Score: 2.20
Because: energy closeness (+1.70), acousticness match (+0.50)

Rooftop Lights - Score: 2.18
Because: energy closeness (+1.68), acousticness match (+0.50)

Neon Horizon - Score: 1.98
Because: energy closeness (+1.48), acousticness match (+0.50)

Sunday Backroad - Score: 1.96
Because: energy closeness (+1.96)

Block Party Anthem - Score: 1.94
Because: energy closeness (+1.44), acousticness match (+0.50)
```

I re-ran this profile under default weights specifically to keep the High-Energy Pop vs. Genre/Mood Ghost comparison below isolated to one variable (genre/mood match availability), since Genre/Mood Ghost itself now runs under mood-first mode for the main evaluation.

### Zero Energy Absolutist (adversarial — boundary value)

```
=== Zero Energy Absolutist ===

Top recommendations:

Spacewalk Thoughts - Score: 4.94
Because: genre match (+2.0), mood match (+1.0), energy closeness (+1.44), acousticness match (+0.5)

Library Rain - Score: 2.80
Because: mood match (+1.0), energy closeness (+1.30), acousticness match (+0.5)

Midnight Coding - Score: 2.66
Because: mood match (+1.0), energy closeness (+1.16), acousticness match (+0.5)

Autumn Piano Sketch - Score: 2.00
Because: energy closeness (+1.50), acousticness match (+0.5)

Floating Above Clouds - Score: 1.90
Because: energy closeness (+1.40), acousticness match (+0.5)
```

`target_energy = 0.0` is as extreme as the boundary gets, and it handled it fine — energy closeness scores just got smaller instead of doing anything weird like going negative or throwing a divide-by-zero.

### What surprised me

None of the adversarial profiles crashed the system or produced invalid scores. The scoring degrades gracefully; when genre or mood has no match, it just falls back to whatever criteria still apply (usually energy and acousticness). That part I expected going in, but two things caught me off guard:

1. **Compound genre names lose all genre credit because of exact-string matching.** Looking through the catalog, `Rooftop Lights` is tagged `indie pop` and `Floating Above Clouds` is tagged `ambient pop`. When I ran a `pop` preference against `indie pop`, and separately an `ambient` preference against `ambient pop`, both scored zero genre credit, the strings just don't match exactly, even though to a human these are obviously related genres. This happened independently in two different tests, so it's not a one-off fluke, it's a real gap in the matching logic.

2. **The system never signals when a genre or mood doesn't exist in the catalog at all.** In the Genre/Mood Ghost test, `reggae` and `euphoric` don't appear anywhere in `data/songs.csv`, so there was zero chance of a genre or mood match from the start. But the recommender doesn't know or care, it still confidently hands back 5 fully ranked songs based on whatever partial signal is left (mostly energy and acousticness), with nothing in the output telling you the genre/mood match failed completely. From the outside, a "genre doesn't exist" result looks identical to a "genre exists but nothing scored high enough" result.

### Comparing Profiles

**High-Energy Pop vs. Chill Lofi — opposite energy targets, different scoring modes**

These two profiles ask for almost opposite things: High-Energy Pop wants `target_energy = 0.9` under default weights, Chill Lofi wants `target_energy = 0.35` under mood-first weights. Completely different songs won each one, with no overlap in the top 5 at all. Sunrise City (a high-energy pop track) topped High-Energy Pop at 5.34, while Library Rain (a mellow lofi track) topped Chill Lofi at 5.00. This still confirms the energy part of the scoring works in both directions, it's not secretly biased toward "high energy is always better," it rewards whatever's actually close to what the person asked for. The two scores aren't directly comparable this time though, since they're running under different weight schemes: Library Rain's energy closeness bonus is +1.00 under mood-first's lighter energy weighting, versus Sunrise City's +1.84 under default's heavier energy weighting. A cleaner apples-to-apples comparison would need both profiles on the same mode, this pairing mostly shows that both modes correctly reward whichever song best fits the stated preferences, just with different point totals along the way.

**Deep Intense Rock vs. Sad Rave — same "intense" family, but Sad Rave contradicts itself**

Both of these profiles are chasing a similar vibe on paper (rock-adjacent, high energy), but Sad Rave was built to be self-contradictory: it asks for metal + melancholic + energy 0.95, but also says the user likes acoustic music, which is an odd combination since intense, high-energy metal songs are rarely acoustic-leaning. Deep Intense Rock runs under energy-focused mode and has one song, Storm Runner, that satisfies genre, mood, and energy all at once, so it sweeps every bonus and wins big at 5.96, well ahead of the runner-up Gym Hero at 4.89. Sad Rave (also energy-focused) never finds a song like that, because no song in the catalog is simultaneously metal, melancholic, and acoustic-friendly. Instead the winner, Broken Amplifier, only picks up genre match (+1.00) and energy closeness (+3.50) for a total of 4.50, with no mood or acoustic credit at all. The system didn't fail or break, it just correctly reported that nothing in the catalog fully satisfies a set of preferences that don't fully agree with each other, so the "best" answer is a partial match rather than a perfect one.

**High-Energy Pop vs. Genre/Mood Ghost — real matches vs. no matches at all**

To keep this comparison isolated to one variable (whether genre/mood can match at all, not which scoring mode is used), I'm comparing High-Energy Pop against the "Genre/Mood Ghost (default)" block above, both running under default weights. High-Energy Pop asks for `pop` and `happy`, both of which are real values in the catalog, so the top song can actually earn genre and mood credit on top of energy and acoustic credit, landing at 5.34. Genre/Mood Ghost asks for `reggae` and `euphoric`, neither of which exists anywhere in the data, so there is no possible way for any song to earn genre or mood points, no matter how good a fit it is otherwise. Its top song, Night Drive Loop, tops out at 2.20 using only energy closeness and acousticness. Two things stand out from comparing them. First, the ceiling is roughly cut in half when genre and mood can't contribute (5.34 vs. 2.20), which makes sense since those two bonuses are worth up to 3.0 of the total score under default weights. Second, look at how bunched together the Ghost results are: 2.20 down to 1.96 across the top 5, a spread of only 0.24. Compare that to High-Energy Pop's spread of 2.88 (5.34 down to 2.46). When genre and mood are in play, they do a lot of work separating "great fit" from "okay fit." When they're not in play, every song is only being judged on energy and acousticness, which vary a lot less from song to song, so everything ends up clustered close together instead of clearly ranked.

**Why does Gym Hero keep showing up near the top, even for profiles that aren't asking for "intense"?**

Gym Hero is tagged as a pop song with mood `intense`. It shows up as the #2 result for High-Energy Pop, a profile whose mood preference is `happy`, not `intense` at all. Here's the actual math from the terminal output that explains it:

- **High-Energy Pop** (default, favorite_mood = "happy"): Gym Hero scores 4.44, built from genre match (+2.00), energy closeness (+1.94), and acousticness match (+0.50). Notice there's no mood bonus in that list at all, because "happy" doesn't match Gym Hero's actual mood of "intense." It still lands in 2nd place anyway.
- **Deep Intense Rock** (energy-focused, favorite_mood = "intense"): Gym Hero scores 4.89, this time from mood match (+1.00), energy closeness (+3.40), and acousticness match (+0.50), but no genre match, because Gym Hero is tagged "pop," not "rock." The energy-focused weighting also pushes this score up much higher than it would be under default weights.
- **Sad Rave** (energy-focused): Gym Hero scores only 3.43, from energy closeness alone, no genre, mood, or acoustic credit survives here.

One extra thing this shows: since Deep Intense Rock and Sad Rave both use energy-focused weights, Gym Hero's score across all three profiles isn't just about which criteria match, it's also about which scoring mode is active. The same song's "just energy closeness" component is worth a lot more here (+3.40, +3.43) than it would be under default weights, which is part of why Gym Hero keeps surfacing near the top even when genre or mood don't line up.

### Logic Experiment: Weight Shift

**What I actually tested:** I changed genre match from +2.0 to +1.0 (a halving, close to the template's 2.0 -> 0.5 example) and doubled the max energy contribution from +2.0 to +4.0 (formula: `(1 - abs(target_energy - song_energy)) * 4.0`). Mood (+1.0) and acoustic (+0.5) stayed the same. New max possible score: 6.5.

I didn't test adding tempo or valence to the score. I chose the weight shift instead because I'd already found that with my original weights, a song with zero genre match could mathematically outscore a true genre match, so I wanted to see if making energy even stronger would surface that problem in real test data, not just in a hypothetical.

**How the system behaved for different types of users (before vs. after):**

```
=== Deep Intense Rock (before → after) ===
Storm Runner:  5.48 → 6.46
Gym Hero:      3.44 → 5.38
Gap:           2.04 → 1.08
```

Storm Runner still won, but its lead over Gym Hero (a pop song with no genre match) shrank by almost half. I checked all 6 of my test profiles, no song actually flipped rank anywhere, the genre-matched song still came out on top every time, just by a smaller margin.

**Was this more accurate, or just different?**

Honestly, just different, not clearly more accurate. Nothing in my actual catalog flipped rank, so on the surface it looks like a safe change. But the math says the underlying risk got worse, not better; the theoretical case where a wrong-genre song beats a true genre match (my classical/happy example) would now have an even bigger gap in the wrong song's favor, since energy is worth twice as much.

---

## 8. Future Work

**Additional features or preferences**

I'd actually start using valence, danceability, and tempo instead of just letting them sit unused in the dataset, since they're already there and could add real signal. I'd also want some kind of fuzzy genre matching so "indie pop" and "pop" don't score as a total mismatch just because the strings aren't identical.

**Better ways to explain recommendations**

I'd want the system to flag when a user's requested genre or mood doesn't exist in the catalog at all, instead of silently falling back to energy and acousticness with no warning. Right now a "genre doesn't exist" result looks identical to a "genre exists but scored low" result, and that's genuinely confusing from the outside.

**Improving diversity among the top results**

With 13 of my 15 genres having exactly one song, there's basically no alternative to offer once you're even slightly outside that one song's best-fit profile. I'd want a bigger, more evenly distributed catalog so users who like less common genres get real options instead of just whatever's closest on energy.

**Handling more complex user tastes**

Right now a user can only state one genre and one mood, so someone who likes "either rock or electronic" has no way to express that. I'd want to support multiple acceptable values per preference, so the system isn't forcing every user into a single narrow lane.

---

## 9. Personal Reflection

**What you learned about recommender systems**

I learned that a recommender doesn't need anything fancy to feel legitimate, mine is just addition and sorting, but it still produces results that look and feel like real recommendations. I also learned how much a system's behavior depends on the shape of its data, not just its math, the scoring logic never changed, but the results were only as good as how evenly my catalog covered different genres and moods.

**Something unexpected or interesting you discovered**

The most interesting thing was proving, with actual numbers, that a song with zero genre match could mathematically outrank a true genre match, that wasn't something I guessed at, I built the scoring recipe and it still had a real blind spot I didn't see coming until I tested it. I also didn't expect how confidently the system would fail, when I asked for a genre and mood that don't exist anywhere in my catalog, it never told me that, it just quietly handed back 5 ranked songs like nothing was wrong.

**How this changed the way you think about music recommendation apps**

It made me a lot more suspicious of confident-looking recommendations from real apps, if my tiny 18-song system can silently fail and still look convincing, I have to assume bigger systems have their own invisible blind spots too. It also made me appreciate that a recommendation isn't really "correct" or "incorrect," it's just a reflection of whatever the underlying data and scoring rules happen to reward.
