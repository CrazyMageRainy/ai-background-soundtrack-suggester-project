now to implement the score song function. Based the songs using the recipe in @README.md . Calculate the score using 
@README.md Algorithem recipe and its weights includoing bonus/penalty modifiers
Mood clash-> val:	-4.0 ->	Opposing moods (chill↔aggressive, peaceful↔intense)
Double categorical hit ->	+3.5	-> Both genre AND mood match
A favorite artist will give +2.0
the score should be calculated using a Fixed-Weight Linear Sum to create the score_song function.
THe function returns both its total numeric score as well as well as a list of reasons for the score: (the features + the bonuses/penalties), allowing the user to understand the score

Algorithm recipe: 
- +26.0 points for genre match
- +12.0 for mood match
- +5.0 for favorite artist
- Mood clash-> val:	-4.0 ->	Opposing moods (chill↔aggressive, peaceful↔intense)
- Double categorical hit ->	+3.5	-> Both genre AND mood match
-  favorite artist will give +2.0
- closeness x 6.0 for valence
- closenes  x5.0 for danceability
- clossness x9.0 for energy
- closeness = 1- abs(diff) [diff being user_pref - song_score]