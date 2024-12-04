# tweetnlp_ray_nested
chatGPT answer to: "tweetnlp with python ray with chunks for nodes and subchunks for cores" some corrections

After receiving some very good hint from chatGPT answering my above question, I have to add some corrections
in order to make their python script work

First error : ConnectionError: Could not find any running Ray instance so ray.init(...) replaced with simply ray.init()

After rerunning another error: ValueError: The remote function __main__.process_node_level is too large (476 MiB > FUNCTION_SIZE_ERROR_THRESHOLD=95 MiB)
added after f process_subchunk : fcorelev_ref = ray.put(process_subchunk) # my modif: store big Object and get an ObjectRef
added argument in function in process_core_level(
adeed in process_node_level at process_core_level as first arg fcorelev_ref

It seems that the remote ray task process_core_level takes as first argument the name of the function it returns
and also when remote process_node_level calls process_core_level the latter is given as first arg fcorelev_ref in order to correctly retrieve the big Object

The python script can then be easily adapted to interact with a slurm script that might fix one node per task and then indicate the cores per task and an array of tasks in order to do sentiment analysis on a big tweet dataset using node and core parallelism by nesting the core_level within the node_level process.
