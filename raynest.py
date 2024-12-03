import ray
import tweetnlp

# Initialize Ray
ray.init()

# Load TweetNLP model
model = tweetnlp.load_model("sentiment")

# Define a function for processing a batch of tweets
def analyze_tweets(tweets):
    return [model.sentiment(tweet) for tweet in tweets]

# Wrap the function in Ray
@ray.remote
def parallel_analyze_tweets(tweets):
    return analyze_tweets(tweets)

# Example tweets
tweets = [
    "I love this new feature on Twitter!",
    "This app update is terrible.",
    "Neutral feelings about this news.",
    "What a fantastic day to be online!",
    "Why is this so buggy?"
]

# Split tweets into chunks for parallel processing
def chunkify(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

# Number of cores or workers
num_workers = 2
chunk_size = len(tweets) // num_workers + 1
tweet_chunks = chunkify(tweets, chunk_size)

# Distribute work across workers
futures = [parallel_analyze_tweets.remote(chunk) for chunk in tweet_chunks]

# Gather results
results = ray.get(futures)

# Flatten results
all_results = [res for sublist in results for res in sublist]

# Display results
for tweet, sentiment in zip(tweets, all_results):
    print(f"Tweet: {tweet}\nSentiment: {sentiment}\n")

