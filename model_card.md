# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**

---

## 2. Intended Use

Describe what your recommender is designed to do and who it is for.

Prompts:

- What kind of recommendations does it generate
- What assumptions does it make about the user
- Is this for real users or classroom exploration

---

## 3. How the Model Works

Explain your scoring approach in simple language.

Prompts:

- What features of each song are used (genre, energy, mood, etc.)
- What user preferences are considered
- How does the model turn those into a score
- What changes did you make from the starter logic

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data

Describe the dataset the model uses.

Prompts:

- How many songs are in the catalog
- What genres or moods are represented
- Did you add or remove data
- Are there parts of musical taste missing in the dataset

---

## 5. Strengths

Where does your system seem to work well

Prompts:

- User types for which it gives reasonable results
- Any patterns you think your scoring captures correctly
- Cases where the recommendations matched your intuition

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

My catalog's genre distribution is extremely uneven, 12 of my 14 genres have exactly one song, while lofi has three. That means a user whose favorite genre is lofi gets three chances at a genre-match bonus, and two of those songs also match "chill" mood, stacking bonuses, while a user who likes classical or metal has exactly one shot, with zero fallback if that one song's mood or energy happens to be off. I initially thought there was also a genre "gap" in the energy scoring around target_energy=0.6, but checking my actual data, that turned out to be wrong, Sunday Backroad sits at energy 0.58, which is a near-perfect match for a target of 0.6. So the real bias isn't in the energy formula itself, it's entirely a catalog composition problem: users whose taste happens to align with lofi/chill are structurally better served than users who like any of the 12 singleton genres, regardless of how well the scoring math works.

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

### Chill Lofi

```
=== Chill Lofi ===

Top recommendations:

Library Rain - Score: 5.50
Because: genre match (+2.0), mood match (+1.0), energy closeness (+2.00), acousticness match (+0.5)

Midnight Coding - Score: 5.36
Because: genre match (+2.0), mood match (+1.0), energy closeness (+1.86), acousticness match (+0.5)

Focus Flow - Score: 4.40
Because: genre match (+2.0), energy closeness (+1.90), acousticness match (+0.5)

Spacewalk Thoughts - Score: 3.36
Because: mood match (+1.0), energy closeness (+1.86), acousticness match (+0.5)

Coffee Shop Stories - Score: 2.46
Because: energy closeness (+1.96), acousticness match (+0.5)
```

Also matched my intuition — mellow, low-energy tracks up top, acoustic bonus applied consistently.

### Deep Intense Rock

```
=== Deep Intense Rock ===

Top recommendations:

Storm Runner - Score: 5.48
Because: genre match (+2.0), mood match (+1.0), energy closeness (+1.98), acousticness match (+0.5)

Gym Hero - Score: 3.44
Because: mood match (+1.0), energy closeness (+1.94), acousticness match (+0.5)

Block Party Anthem - Score: 2.46
Because: energy closeness (+1.96), acousticness match (+0.5)

Neon Horizon - Score: 2.42
Because: energy closeness (+1.92), acousticness match (+0.5)

Broken Amplifier - Score: 2.40
Because: energy closeness (+1.90), acousticness match (+0.5)
```

Straightforward — the top pick nails genre, mood, and energy all at once.

### Sad Rave (adversarial — contradictory preferences)

```
=== Sad Rave ===

Top recommendations:

Broken Amplifier - Score: 4.00
Because: genre match (+2.0), energy closeness (+2.00)

Autumn Piano Sketch - Score: 2.10
Because: mood match (+1.0), energy closeness (+0.60), acousticness match (+0.5)

Gym Hero - Score: 1.96
Because: energy closeness (+1.96)

Storm Runner - Score: 1.92
Because: energy closeness (+1.92)

Block Party Anthem - Score: 1.86
Because: energy closeness (+1.86)
```

This is the profile I built to be internally contradictory (high-energy metal, but melancholic and acoustic-loving), and it didn't break anything. It just fell back to whatever criteria still lined up for each song, no crash, no invalid scores, just a genre match here, an energy match there.

### Genre/Mood Ghost (adversarial — genre/mood not in catalog)

```
=== Genre/Mood Ghost ===

Top recommendations:

Night Drive Loop - Score: 2.20
Because: energy closeness (+1.70), acousticness match (+0.5)

Rooftop Lights - Score: 2.18
Because: energy closeness (+1.68), acousticness match (+0.5)

Sunrise City - Score: 2.06
Because: energy closeness (+1.56), acousticness match (+0.5)

Neon Horizon - Score: 1.98
Because: energy closeness (+1.48), acousticness match (+0.5)

Sunday Backroad - Score: 1.96
Because: energy closeness (+1.96)
```

I asked for `reggae` and `euphoric`, neither of which exist anywhere in my catalog. The system didn't error out or flag anything, it just quietly dropped the genre and mood bonuses and ranked everything on energy and acousticness alone, still confidently returning 5 songs like nothing was wrong.

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

**High-Energy Pop vs. Chill Lofi — opposite energy targets**

These two profiles ask for almost opposite things: High-Energy Pop wants `target_energy = 0.9`, Chill Lofi wants `target_energy = 0.35`. And that's exactly what happened, completely different songs won each one. Sunrise City (a high-energy pop track) topped High-Energy Pop at 5.34, while Library Rain (a mellow lofi track) topped Chill Lofi at 5.50. No overlap in the top 5 between the two lists at all. This is really just confirming the energy part of the scoring is doing its job in both directions, it's not secretly biased toward "high energy is always better," it rewards whatever's actually close to what the person asked for. The one small wrinkle: Chill Lofi's winner scored slightly higher (5.50 vs 5.34) because Library Rain's energy closeness bonus hit +2.00, basically a perfect match, while Sunrise City's was +1.84, a very good but not perfect match. So even between two "correct" results, small differences in how close a song's actual energy is to the target shift the final number.

**Deep Intense Rock vs. Sad Rave — same "intense" family, but Sad Rave contradicts itself**

Both of these profiles are chasing a similar vibe on paper (rock-adjacent, high energy), but Sad Rave was built to be self-contradictory: it asks for metal + melancholic + energy 0.95, but also says the user likes acoustic music, which is an odd combination since intense, high-energy metal songs are rarely acoustic-leaning. You can see the difference in how cleanly each profile resolves. Deep Intense Rock has one song, Storm Runner, that satisfies genre, mood, and energy all at once, so it sweeps every bonus and wins big at 5.48, well ahead of the runner-up at 3.44. Sad Rave never finds a song like that, because no song in the catalog is simultaneously metal, melancholic, and acoustic-friendly. Instead the winner, Broken Amplifier, only picks up genre match (+2.0) and energy closeness (+2.00) for a total of 4.00, with no mood or acoustic credit at all. The system didn't fail or break, it just correctly reported that nothing in the catalog fully satisfies a set of preferences that don't fully agree with each other, so the "best" answer is a partial match rather than a perfect one.

**High-Energy Pop vs. Genre/Mood Ghost — real matches vs. no matches at all**

High-Energy Pop asks for `pop` and `happy`, both of which are real values in the catalog, so the top song can actually earn genre and mood credit on top of energy and acoustic credit, landing at 5.34. Genre/Mood Ghost asks for `reggae` and `euphoric`, neither of which exists anywhere in the data, so there is no possible way for any song to earn genre or mood points, no matter how good a fit it is otherwise. Its top song, Night Drive Loop, tops out at 2.20 using only energy closeness and acousticness. Two things stand out from comparing them. First, the ceiling is roughly cut in half when genre and mood can't contribute (5.34 vs. 2.20), which makes sense since those two bonuses are worth up to 3.0 of the total score. Second, look at how bunched together the Ghost results are: 2.20 down to 1.96 across the top 5, a spread of only 0.24. Compare that to High-Energy Pop's spread of 2.88 (5.34 down to 2.46). When genre and mood are in play, they do a lot of work separating "great fit" from "okay fit." When they're not in play, every song is only being judged on energy and acousticness, which vary a lot less from song to song, so everything ends up clustered close together instead of clearly ranked.

**Why does Gym Hero keep showing up near the top, even for profiles that aren't asking for "intense"?**

Gym Hero is tagged as a pop song with mood `intense`. It shows up as the #2 result for High-Energy Pop, a profile whose mood preference is `happy`, not `intense` at all. Here's the actual math from the terminal output that explains it:

- **High-Energy Pop** (favorite_mood = "happy"): Gym Hero scores 4.44, built from genre match (+2.0), energy closeness (+1.94), and acousticness match (+0.5). Notice there's no mood bonus in that list at all, because "happy" doesn't match Gym Hero's actual mood of "intense." It still lands in 2nd place anyway.
- **Deep Intense Rock** (favorite_mood = "intense"): Gym Hero scores 3.44, this time from mood match (+1.0), energy closeness (+1.94), and acousticness match (+0.5), but no genre match, because Gym Hero is tagged "pop," not "rock."
- **Sad Rave**: Gym Hero scores only 1.96, from energy closeness alone, no genre, mood, or acoustic credit survives here.

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

Ideas for how you would improve the model next.

Prompts:

- Additional features or preferences
- Better ways to explain recommendations
- Improving diversity among the top results
- Handling more complex user tastes

---

## 9. Personal Reflection

A few sentences about your experience.

Prompts:

- What you learned about recommender systems
- Something unexpected or interesting you discovered
- How this changed the way you think about music recommendation apps
