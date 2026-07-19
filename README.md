# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real recommendation systems, like Spotify or YouTube, mostly rely on two approaches: collaborative filtering (looking at what similar users listened to) and content-based filtering (looking at the actual attributes of the content itself). My design uses only the second one. It doesn't look at other users at all, just compares a song's own attributes against what one user says they like.

**What features does each `Song` use in your system**

Every song in the dataset carries a full profile: title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. The scoring rule is only meant to use four of those attributes, genre, mood, energy, and acousticness, since those are the only four things `UserProfile` states a preference for. Tempo, valence, and danceability stay part of the dataset (they add richness and make the songs feel more real), but the plan is to leave them out of the scoring math. I looked into using valence early on since it lines up with the arousal-valence model of mood, but decided it would be redundant with the mood field for a system this simple.

**What information does your `UserProfile` store**

A user profile stores four preferences: `favorite_genre`, `favorite_mood`, `target_energy`, and `likes_acoustic`. That's it, no listening history, no likes/skips, just a snapshot of what someone says they want right now.

**How does your `Recommender` compute a score for each song**

Each song is meant to be scored against those four preferences using this Algorithm Recipe:

- **+2.0** if the song's genre matches the user's favorite genre
- **+1.0** if the song's mood matches the user's favorite mood
- **Up to +2.0** for energy, based on how close the song's energy is to the user's target, the formula is `(1 - |target_energy - song_energy|) * 2.0`, so a perfect match scores the full 2.0, and the score drops the further apart they are
- **+0.5** if the song's acousticness lines up with whether the user likes acoustic music

That puts the max possible score at 5.5 if a song matches on everything.

I chose to weight genre higher than mood on purpose, it's the starting point my project instructions suggested, and I want to test it as my baseline before trying anything else. I got a good argument from Claude that mood should count for more, since mood reflects what you want right now while genre is more of a general taste. That's a fair point, but I don't have any real data to back it up yet, so I'm saving that idea to test later as an actual experiment instead of just taking the AI's word for it.

**How do you choose which songs to recommend**

Once every song in the catalog has a score, the plan is to sort them from highest to lowest and take the top `k`, usually the top 5. The scoring rule judges one song at a time; the ranking rule is what turns all those individual judgments into an actual ordered list. One thing worth noting: since genre and energy carry the biggest weights, this design will lean harder on those than on mood, which could make recommendations feel a bit "safe" (same genre showing up again and again) rather than actually matching the mood someone's in right now.

**Expected bias:** Because energy is weighted equal to genre (both up to 2.0 points), the system will likely favor loud songs regardless of genre almost as much as it favors true genre matches. I tested this with a rock/intense profile and found that high-energy songs from unrelated genres (metal, pop, hip hop) scored 2.4–3.5, while the actual genre match scored 5.48, a real gap, but one that could shrink if my rock catalog stays small.

```python
UserProfile(
    favorite_genre="rock",
    favorite_mood="intense",
    target_energy=0.9,
    likes_acoustic=False,
)
```

In other words, the system may end up recommending loud music more than your genre, especially in categories with few songs.

**Pipeline at a glance**

```
UserProfile
  (favorite_genre, favorite_mood, target_energy, likes_acoustic)
        │
        ▼
Score each Song against the profile
  genre match      → +2.0
  mood match       → +1.0
  energy closeness → up to +2.0
  acoustic match    → +0.5
        │
        ▼
Sort all songs by score, high → low
        │
        ▼
Take the top k  →  recommendation list
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Default profile: `favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False`

```
Loaded songs: 18

Top recommendations:

Sunrise City - Score: 5.46
Because: genre match (+2.0), mood match (+1.0), energy closeness (+1.96), acousticness match (+0.5)

Gym Hero - Score: 4.24
Because: genre match (+2.0), energy closeness (+1.74), acousticness match (+0.5)

Rooftop Lights - Score: 3.42
Because: mood match (+1.0), energy closeness (+1.92), acousticness match (+0.5)

Night Drive Loop - Score: 2.40
Because: energy closeness (+1.90), acousticness match (+0.5)

Neon Horizon - Score: 2.38
Because: energy closeness (+1.88), acousticness match (+0.5)
```

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

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

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this taught me that turning data into predictions is really just turning data into comparisons. My recommender doesn't "know" anything about music, it just takes whatever four values a user gives it (genre, mood, energy, acoustic preference) and checks each song against those same four values, adding up points for whatever lines up. There's no learning, no history, no understanding of the music itself, it's addition and sorting. But when I ran it against profiles like Chill Lofi, the output still felt like a real recommendation, which honestly surprised me more than I expected it to.

The bias and unfairness part showed up in ways I didn't fully predict going in. My catalog has 13 out of 15 genres represented by exactly one song, so a user who likes lofi (three songs) gets a much better experience than someone who likes classical or metal (one song each), not because the scoring math treats them differently, but because the data itself isn't evenly distributed. I also proved that a song with zero genre match can mathematically outrank a true genre match, and that the system never tells a user when their requested genre or mood doesn't exist in the catalog at all, it just quietly falls back to whatever signal is left and still looks confident.

AI tools helped most with turning my scoring recipe into actual working code quickly, once I had a specific plan, it could implement it fast. But I had to double-check its reasoning constantly, not its code. The clearest example was when Claude argued that mood should count for more than genre in my scoring weights, a reasonable argument, but I had no real data to back it up, so I saved it as something to test later instead of just accepting it. A similar thing happened when AI claimed there was an energy 'gap' around target_energy=0.6 in my catalog, and when I checked my actual songs.csv, Sunday Backroad sits at 0.58, basically a perfect match, so that claim turned out to be wrong. Both cases taught me that AI reasoning about my own data needs to be checked against the actual data, not trusted just because it sounds confident.
