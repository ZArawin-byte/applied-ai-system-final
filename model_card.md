# 🎧 Model Card: Music Recommender AI

## 1. Model Name

**FeelingLoader 2.0**

---

## 2. Intended Use

Describe what your recommender is designed to do and who it is for.

- What kind of recommendations does it generate
- What assumptions does it make about the user
- Is this for real users or classroom exploration

FeelingLoader 2.0 extends the original Module 3 recommender into a full AI-integrated system. It reads a user's preferred genre, mood, and energy level, scores all songs in the catalog, and returns the top recommendations. It then uses the Google Gemini API to generate a natural language explanation of why each song was picked. A guardrail step validates the user profile before any recommendations are made. This is for classroom exploration and portfolio demonstration, not for real production use.

---

## 3. How the Model Works

Explain your scoring approach in simple language.

- What features of each song are used (genre, energy, mood, etc.)
- What user preferences are considered
- How does the model turn those into a score
- What changes did you make from the starter logic

The model looks at three things for each song: genre, mood, and energy. It compares those to what the user said they like and gives points 2 points for a genre match, 1.5 for a mood match, and up to 1 point based on how close the song's energy is to what the user wants. The song with the most points gets recommended first.

The problem is that genre gets more points than mood and energy combined. So even if a user wants calm, happy music, a loud rock song can still win just because the genre matched. This means the user might not experience new songs that actually fit how they feel.

---

## 4. Data

Describe the dataset the model uses.

- How many songs are in the catalog
- What genres or moods are represented
- Did you add or remove data
- Are there parts of musical taste missing in the dataset

There are 20 songs in the catalog with different genres and moods. Genre is a category of similar-sounding songs, and mood describes the emotion the song gives. The dataset includes genres like pop, lofi, rock, jazz, ambient, synthwave, and indie pop, and moods like happy, chill, intense, relaxed, moody, and focused. During testing, adding songs showed how genre having more points than mood meant songs were not always recommended based on how the user actually felt.

---

## 5. Strengths

Where does your system seem to work well

- User types for which it gives reasonable results
- Any patterns you think your scoring captures correctly
- Cases where the recommendations matched your intuition

The system works well when the user's preferred genre has multiple songs in the catalog. For example, the pop profile got good results because there were 3 pop songs, so the top recommendation matched genre, mood, and energy all at once. The scoring is also easy to understand you can see exactly why each song was recommended.

---

## 6. Limitations and Bias

Where the system struggles or behaves unfairly.

- Features it does not consider
- Genres or moods that are underrepresented
- Cases where the system overfits to one preference
- Ways the scoring might unintentionally favor some users

The biggest limitation is that the system values genre over the user's current feeling. A rock fan who wants calm music will still get loud, intense rock because genre points outweigh energy and mood points. This means the system treats users as fixed categories like "rock person" or "pop person" instead of responding to how they actually feel right now.

Also, genres with only one song in the catalog (like rock) always push that one song to the top, even if it is a bad match. The system also does not consider time of day, listening history, or how often a user skips a song.

---

## 7. Evaluation

How you checked whether the recommender behaved as expected.

- Which user profiles you tested
- What you looked for in the recommendations
- What surprised you
- Any simple tests or comparisons you ran

Three user profiles were tested:

- **Pop + happy + energy 0.8** — results made sense. "Sunrise City" ranked first with a perfect genre, mood, and energy match.
- **Lofi + chill + energy 0.35** — results made sense. Lofi songs dominated the top 3 because genre and mood both matched.
- **Rock + happy + energy 0.3** — results were surprising. "Storm Runner" ranked first even though it is intense and high energy. The user wanted calm and happy, but the genre match alone pushed it to the top. This showed the bias clearly.

The biggest surprise was how one number (the genre weight) could make the whole system behave unfairly for users with niche genre preferences.

---

## 8. Future Work

Ideas for how you would improve the model next.

- Additional features or preferences
- Better ways to explain recommendations
- Improving diversity among the top results
- Handling more complex user tastes

- Add time of day as a feature for example, give more weight to calm songs in the morning and high energy songs at night.
- Lower the genre weight and increase the mood weight so the system responds more to how the user feels rather than just what category they belong to.
- Add more songs per genre so users with niche tastes have real options instead of always getting the same one song.

---

## 9. Personal Reflection

A few sentences about your experience.

- What you learned about recommender systems
- Something unexpected or interesting you discovered
- How this changed the way you think about music recommendation apps

I learned that recommendation systems are written by humans and are usually biased because of the choices those humans make. For example, the coder decided to give genre more points than mood that was not random, it was a decision, and it had consequences. I discovered that even a simple system with just 10 songs and 3 features can already show real problems like filter bubbles, where the algorithm keeps confirming what it thinks it knows about you instead of showing you something new.

Building this changed how I think about apps like Spotify and TikTok. When those apps keep showing me the same type of content, it is not magic it is just weighted math, and someone decided what those weights should be. Human judgment still matters because no algorithm can fully understand how a person feels in the moment.

---

## 10. AI Collaboration

**Helpful suggestion:** When the Gemini API kept failing due to quota and key issues, the AI assistant suggested building a rule-based fallback explanation that uses actual song data (genre match, mood match, energy proximity) to generate readable per-song explanations. This was a good architectural decision — the app now always shows meaningful output even when the API is unavailable, which made the demo more reliable.

**Flawed suggestion:** The AI initially used `gemini-1.5-flash` as the model name, which caused 404 errors because that model was not available for the API version being used. The AI did not anticipate the version mismatch and kept suggesting the same model name even after repeated failures. Switching to `gemini-2.0-flash` and then to the new `google-genai` SDK (replacing the deprecated `google-generativeai` package) required manual debugging of the logs to identify the real cause.
