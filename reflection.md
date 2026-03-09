# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
  The UI looked fined until I started testing out the game and noticed many bugs

- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
  1. When my guesses were larger than the secret number but each time the game told me to go higher. My expectation was for the game to tell me to go lower.
  Problem:
  if guess > secret:
    return "Too High", "📈 Go HIGHER!"   # ← message is backwards
  else:
    return "Too Low", "📉 Go LOWER!"     # ← message is backwards
  2. The new game button is not starting a new game, it just says "Game over. Start a new game to try again." when i fail and "You already won. Start a new game to play again.". My expectation is for it to start a new game.
  if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(1, 100)
    st.success("New game started.")
    st.rerun()
    Fix: include st.session_state.status() = "playing"
  3. There difficulty levels aren't consistent. Normal level has more attempts than easy level. Easy should have more attempts. The hard level has a smaller guess range than normal. Normal should have a smaller range
  Problem:
  def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100
  4. At an even numbered attempt, the secret is converted to a string so even if you guessed the correct answer, it would be wrong because its being compared to a string at even attempts
  Problem 158-163:
        if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)? Claude

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  For the problem about the "Start New Game" button not working, it suggested that I add a line of code that changed the status of the game to "playing". Code: st.session_state.status() = "playing

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
  The problem with the hints was that when a guess was larger than a secret, the hint would suggest going higher instead of lower and vice versa. Claude suggested that the problem was because the code was converting the the secret to string at even attempts, which would incorrectly assume a guess of 4 is higher than a secret of 30.This could have been a small portion of the problem but the main problem is the code itself hints a user to go higher when a guess is larger than a secret and to go lower when a guess is smaller.
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  I used pytests and confirmed by testing out the actual game

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
  A test I run manually was on the "New Game" button. Before, the button wasn't starting a new game when it was clicked so after fixing the bug, I tested manually on the game and it worked. I also testing using pytests by checking the statuses of the game

- Did AI help you design or understand any tests? How?
  It helped me design and understand the tests by showing me all the possible edge cases. One example is when testing whether the code was incorrectly parsing the guess number into a string when an attempt was even. It gave me multiple edge cases such as when guessing correctly at an even attempt.
---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
  Because the secret was a randomly generated integer on the scale of 1 to 100

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  Every time you interact with a Streamlit app the entire Python script reruns from top to bottom, like refreshing a page. Session state is like a notepad that persists across those reruns, so the app can remember things like your score or the secret number instead of resetting everything each time.

- What change did you make that finally gave the game a stable secret number?
  The fix was wrapping the secret generation in a if "secret" not in st.session_state: check — so instead of calling random.randint() on every rerun, the secret is only generated once when the game first loads, and then stored in session state where it persists across all subsequent reruns.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  Thoroughly reviewing AI generated code and using tests

- What is one thing you would do differently next time you work with AI on a coding task?
  I would try to come up with my own test cases 

- In one or two sentences, describe how this project changed the way you think about AI generated code.
  It helped me see that there's so many ways that AI can support in building projects. From this project, I learned that it's not only useful for generating code, but also for creating test cases and for debugging
