# Qualitative Evaluation

## Query 1: weight loss book

### BM25 Results
1. Lose Weight Fast: Over 50 Incredible Weight Loss Tips and Weight Loss Motivation Secrets Revealed (2020 UPDATE)
2. HYPOTHYROIDISM DIET ~ The secrets to your thyroid and weight loss
3. Fat Fast Cookbook: 50 Easy Recipes to Jump Start Weight Loss
4. Fat Fast Cookbook: 50 Easy Recipes to Jump Start Weight Loss
5. Yoga For Beginners: An Easy Yoga Guide To Relieve Stress, Lose Weight, And Heal Your Body

### Semantic Results
1. Lose Weight Fast: Over 50 Incredible Weight Loss Tips and Weight Loss Motivation Secrets Revealed (2020 UPDATE)
2. Dr. Corson's Top 5 Nutrition Tips: How To Lose Weight Naturally, Have More Energy, Look Better, Feel Better and Live Longer
3. The Poverty Cookbook: My Favorites
4. Fat Fast Cookbook: 50 Easy Recipes to Jump Start Weight Loss
5. Fat Fast Cookbook: 50 Easy Recipes to Jump Start Weight Loss

### Comments
- Better method: Both are very similar, but BM25 is slightly better.
- Why: Both methods retrieve similar results, but BM25 seems to be more precise overall. While it includes a yoga related book, it is still somewhat relevant to weight loss. However, semantic search retrieves an unrelated cookbook ("The Poverty Cookbook"), which is not related to the query.
- Are the top results useful: Yes, most results from both methods are related to weight loss and nutrition.
- Did BM25 fail anywhere: Slightly, as it includes a yoga related book which is indirectly related to weight loss.
- Did semantic fail anywhere: Yes, it retrieves an unrelated cookbook ("The Poverty Cookbook"), showing weaker precision.

## Query 2: healthy eating guide

### BM25 Results
1. Mommy Muscles: A practical guide for building your body and mental muscles
2. Blood Pressure: Blood Pressure Solution: The Step-By-Step Guide to Lowering High Blood Pressure
3. EATING BETTER: Bread Machine Bread Making Recipes for a Healthy Gut
4. EATING BETTER: Bread Machine Bread Making Recipes for a Healthy Gut
5. Fast And Easy Cabbage Recipes: An Guide To An Healthy And Natural Diet

### Semantic Results
1. Dr. Corson's Top 5 Nutrition Tips: How To Lose Weight Naturally, Have More Energy, Look Better, Feel Better and Live Longer
2. Food Addiction Binge Eating And Hypoglycemia: How To Heal It and Get Back To Balance
3. Eat in Peace to Live in Peace: Your Handbook for Vitality
4. Cooking Easy: Healthy Quinoa and More for Diabetics
5. Lose Weight Fast: Over 50 Incredible Weight Loss Tips and Weight Loss Motivation Secrets Revealed (2020 UPDATE)

### Comments
- Better method: Both are very similar, but semantic is slightly better.
- Why: Semantic search retrieves results that are more related to healthy eating and overall wellness. BM25 includes some relevant items but also returns less precise matches like bread machine cookbooks, which are not fully aligned with the idea of healthy eating guide.
- Are the top results useful: Yes, both methods return somewhat useful results, but semantic results are slightly  more  aligned with healthy eating.
- Did BM25 fail anywhere: Yes, it retrieves bread machine cookbooks which are more specific and not necessarily focused on healthy eating as a general concept.
- Did semantic fail anywhere: Slightly, as it includes a weight loss book which is related but not exactly the same as a healthy eating guide.

## Query 3: beginner cookbook

### BM25 Results
1. Beginners Guide To SolidWorks 2016 - Level I
2. Ketogenic Diet: Rapid Weight Loss
3. The Lazy Cook's Way to Weight Loss: Eat More, Lose More!
4. A Daughter's Cookbook
5. Everyday Cooking For One: 101 Easy, Quick and Delicious Recipes

### Semantic Results
1. The Poverty Cookbook: My Favorites
2. Desserts: The Ultimate Recipe Guide
3. Food Storage for Self-Sufficiency and Survival
4. The Canning Cookbook for Beginners
5. Ketogenic Diet: Rapid Weight Loss

### Comments
- Better method: Both are very similar, but semantic is slightly better.
- Why: Semantic results are more closely related to cooking and recipes, including cookbooks and food related content. BM25 retrieves some relevant items but also includes some unrelated results like a SolidWorks guide.
- Are the top results useful: Partially. Semantic results are more consistently relevant to cooking, however, A mentioned above, BM25 includes some useful items but also irrelevant ones.
- Did BM25 fail anywhere: Yes, it retrieves unrelated content such as a SolidWorks guide.
- Did semantic fail anywhere: Slightly, as it includes broader food related items that are not strictly beginner cookbooks.

## Query 4: book for better habits

### BM25 Results
1. Positive Thoughts For The Day: Banish Negative Thinking And Create A Happier, Calmer, And Healthier You
2. Lose Weight Fast: Over 50 Incredible Weight Loss Tips and Weight Loss Motivation Secrets Revealed (2020 UPDATE)
3. 13 Things Mentally Strong People Don't Do: Take Back Your Power, Embrace Change, Face Your Fears, and Train Your Brain for Happiness and Success
4. 13 Things Mentally Strong People Don't Do: Take Back Your Power, Embrace Change, Face Your Fears, and Train Your Brain for Happiness and Success
5. The Mechanic (Old Habits Book 1)

### Semantic Results
1. Quick, Answer Me Before I Forget The Question
2. The Poverty Cookbook: My Favorites
3. All That Glisters
4. Eat in Peace to Live in Peace: Your Handbook for Vitality
5. More Grammar Sex: Essays About Life and Stuff

### Comments
- Better method: BM25 overall
- Why: BM25 retrieves results related to self-improvement, mindset, and habits, which storngly align with the query. Semantic search returns mostly unrelated or loosely connected items that do not clearly address habits.
- Are the top results useful: BM25 results are mostly useful and relevant to improving habits, while semantic results are largely not useful.
- Did BM25 fail anywhere: Slightly, as it includes a weight loss book which is not strongly relted to habits.
- Did semantic fail anywhere: Yes, many results are unrelated that do not relate to habits.

## Query 5: good books for beginners learning investing

### BM25 Results
1. Personal Finance: Budgeting and Saving Money (FREE Bonus Included) (Finance, Personal Finance, Budgeting, Saving Money)
2. Personal Finance: Budgeting and Saving Money (FREE Bonus Included) (Finance, Personal Finance, Budgeting, Saving Money)
3. Trading: The Secrets to Building a Successful Trading Business (Stock Trading, Futures Trading, Options Trading, Day Trading, Forex Trading)
4. How To Write Your First Ebook: 7 Steps To Write Your First Ebook In 7 Days
5. You Are a Badass: How to Stop Doubting Your Greatness and Start Living an Awesome Life

### Semantic Results
1. Trading: The Secrets to Building a Successful Trading Business (Stock Trading, Futures Trading, Options Trading, Day Trading, Forex Trading)
2. How To Write Your First Ebook: 7 Steps To Write Your First Ebook In 7 Days
3. Personal Finance: Budgeting and Saving Money (FREE Bonus Included) (Finance, Personal Finance, Budgeting, Saving Money)
4. More Grammar Sex: Essays About Life and Stuff
5. All That Glisters

### Comments
- Better method: Both are very similar, but BM25 is slightly better.
- Why: BM25 retrieves more finance related content such as budgeting and trading, which are relevant to beginners learning investing. Semantic search includes some relevant results, but introduces unrelated results like essays and general fiction.
- Are the top results useful: Partially. Some results are useful for beginners in finance, but not all are directly focused on investing.
- Did BM25 fail anywhere: Yes, it retrieves unrelated items such as an ebook writing guide and a self help book, which are not relevant to investing.
- Did semantic fail anywhere: Yes, it retrieves unrelated items such as essays and fiction, reducing overall relevance.


# Overall Insights

## Strengths and Weaknesses

- BM25 performs well for queries with specific keywords, since it focuses on terms that exactly match.

- Semantic search performs better for broader or conceptual queries, however, it can return unrelated results.

## Challenging Query Types

- Queries that are more abstract or conceptual (e.g., "book for better habits") are challenging, especially for semantic search, which returned strongly unrelated results.

- Longer or more complex queries (e.g., "good books for beginners learning investing") can also reduce performance for both methods, as those queries include multiple concepts that may be harder to match precisely.

## Where More Advanced Methods Could Help

- A hybrid approach which combines BM25 and semantic search could improve performance.

- Re-ranking models or more advanced embeddings could better capture user intent and improve relevance.