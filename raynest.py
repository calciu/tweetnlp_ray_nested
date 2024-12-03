import ray
import tweetnlp

# Initialize Ray
#ray.init(address="auto")  # Use address="auto" for a cluster; omit for local testing
ray.init()

# Load TweetNLP model
model = tweetnlp.load_model("sentiment")

# Function to process a small batch of tweets
def process_subchunk(tweets):
    return [model.sentiment(tweet) for tweet in tweets]

fcorelev_ref = ray.put(process_subchunk) # my modif: store big Object and get an ObjectRef

# Define a Ray task for subchunk processing
@ray.remote
def process_core_level(process_subchunk, subchunk): #modif: first arg is the function 
    return process_subchunk(subchunk)

# Define a Ray task for node-level chunk processing
@ray.remote
def process_node_level(chunk, num_cores):
    # Split the chunk into subchunks for cores
    subchunk_size = len(chunk) // num_cores + 1
    subchunks = [chunk[i:i + subchunk_size] for i in range(0, len(chunk), subchunk_size)]
    
    # Parallelize subchunk processing across cores
    core_futures = [process_core_level.remote(fcorelev_ref, subchunk) for subchunk in subchunks] # modif: use ref to functions big ObjectRef 
    
    # Collect and combine results
    results = ray.get(core_futures)
    return [res for sublist in results for res in sublist]

# Input tweets
tweets = [
    "I love this new feature on Twitter!",
    "This app update is terrible.",
    "Neutral feelings about this news.",
    "What a fantastic day to be online!",
    "Why is this so buggy?",
    "Twitter spaces are pretty cool.",
    "I miss the old days of the internet.",
    "This is groundbreaking!",
    "Not sure how I feel about this feature.",
    "Amazing news today!",
]

# Chunk tweets for node-level parallelism
num_nodes = 2  # Number of nodes
num_cores_per_node = 4  # Cores available per node
chunk_size = len(tweets) // num_nodes + 1
node_chunks = [tweets[i:i + chunk_size] for i in range(0, len(tweets), chunk_size)]

# Distribute tasks across nodes
node_futures = [process_node_level.remote(chunk, num_cores_per_node) for chunk in node_chunks]

# Gather all results
final_results = ray.get(node_futures)

# Flatten results
all_results = [res for sublist in final_results for res in sublist]

# Display results
for tweet, sentiment in zip(tweets, all_results):
    print(f"Tweet: {tweet}\nSentiment: {sentiment}\n")
