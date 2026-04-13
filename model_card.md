# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  
**GenreFirst**
<!-- Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**   -->

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

<!-- Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

--- -->
This model is still only for classroom exploration and not ready for real users. There is still some tweaking with weights like with genre, as well as going more indepth with moods clashing with user fav mood. Also, subgenres or similar genres can be done to give bonuses if they relate to the users fav genre. It mainly recommends based on genre, likely more useful to compare between songs of a genre instead of exploring different genres.

## 3. How the Model Works  

<!-- Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program. -->

Categorical features: genre, mood, artist
Numerical features: energy, valence, danceability
<!-- Loaded but unused: tempo_bpm, acousticness -->
Used a basic Fix weight Linear sum and a bonus/penalty modifier to try to control the recommendations more to the user preferences. The main changes would be ommiting tempo and acousticness, both being very niche in their usuage and won't affect the value as much.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog    __There are 18 songs__
- What genres or moods are represented  
__Genres__
pop
lofi
rock
ambient
jazz
synthwave
indie pop
metal
classical
electronic
country
drum and bass
folk
latin
trip hop

__Moods__
happy
chill
intense
relaxed
moody
focused
aggressive
melancholy
energetic
nostalgic
dark
peaceful
passionate
dreamy

- Did you add or remove data  __Only more songs were added__
- Are there parts of musical taste missing in the dataset  
__A bunch of genres and the relationship between subgenres with a shared name or have similar music have been ommited. Lyrical context is not included. A song can have more than one mode or fit in more than one genre.__
---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

It works really well when a user's taste fits neatly into one genre and mood. The lofi/chill user gets Midnight Coding, Library Rain, and Focus Flow as its top 3, which feels right for a study playlist. Same with the rock/intense profile. Storm Runner lands at #1 with everything (genre, mood, and favorite artist). The closeness scores also do their job within a genre. The three lofi tracks don't just tie, the one that best matches the user's energy and valence actually comes out on top. Adding the bonus/penalty can really help a lot, especially for edge cases.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The genre weight (+26) is so dominant that it only sticks to a user's stated genre, while nearly ignoring how well a song actually matches their energy, valence, or danceability target score. For example, Gym Hero (energy 0.93) ranks #2 for a user wanting calm pop (energy 0.1) purely because it's labeled "pop," even though its fit in other features is poor. This creates a filter bubble where users are locked into one genre and never shown songs from closely related genres that might suit them better. It gets worse with there being no way to diversy to other genres, they will all cluster at the top of the list. Also, high "danceability" genres like pop, latin, and electronic receive a hidden advantage for users with high danceability pref scores, accidently favoring those genres, not even mentioning the large genre bonus.

---

## 7. Evaluation  

<!-- How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  

- What you looked for in the recommendations  -->
__I mainly looked for the genres and mood, while adding energy as a third option. I attempted to add penalties and bonuses in case certain conditions are met which can impact the total score.__ 
- What surprised you  

__Genre weight impacts the score a lot. Gym hero didn't get number 1 for most cases but it definently stuck around for some user preferences. The current data bias and the implementation of how genres and daneability is done causes this song to pop up in lists. They need to be tuned down more so that an unfit song in a preffered genre doesn't influence the total score of the song that much.__
- Any simple tests or comparisons you ran  
__Changing the weights of genres and mood really shifted the songs recommended. The mood will recommend songs that are aren't from the fav genre of the user.__
---

## 8. Future Work  

<!-- Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes   -->

- Add a similar genre bonus so related genres like indie pop and pop still get a smaller reward instead of being completely ignored.
- Add more mood clashes so songs with clearly incompatible moods (like happy vs melancholy or chill vs intense) actually get penalized.
- Add a penalty when the difference between a user's preferred value and a song's value is too large — this would stop songs like Gym Hero (energy 0.93) from showing up for someone who wants energy at 0.1.
---

## 9. Personal Reflection  

<!-- A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps   -->
This is a pretty fun project. Weights really are important when trying to create something like this or models. The results change dramatically when I change it. There is definently a lot of features I could have added, especially more bonus/penalties which would help fine tune the recomendations. Making the genre weight too big was definently the main issue with my model. I am considering lowering its value as well as the danceability, funnily enough. AI tools really helped a lot this time. I usually write down my thoughts in other files such in evaluation.md, cause I was trying put it in a large pile to figure out what to improve. I have to double check the code especially when it tries to make a big edit, to avoid any concerning logic errors. Luckily that didn't really happen. I stopped claude to clarify what I want to be implemented, and I usually find myself referencing my other files besides the required ones to try to steer the ai to a certain result.
I had a feeling something like this is being used with algorithems in Youtube and Spotify, as usually I get recommended the songs from the same genre that I've been listining to the last few months.
I think the best ratio for weights should be that no weight should be bigger than the sum of the other features, else it monopolizes the total score.
The current implementation is a bit difficult to scale with many genres moods, as I would have to figure out the logic on which moods should be considered clashing one another. Also I would have to determine whether two genres are close enough to consider adding a bit of points to recommend to a user with a fav "genre". 
One more thing I considered was the Per user weights which was recommended by claude, where the weights are defined based on the user themselves. This allows the user to define the features that should be a priority while scoring.
Even if it was a simple algorithem, tweaking it gave very interesting results, changing the weights. I would like to add more features as well as more bonuses and penalties so I can make recommendations for my own personal use.
