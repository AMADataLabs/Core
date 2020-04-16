A note on the two ranking scripts (as opposed to one):

Originally when Kari developed the model, the entire physician population had not been scored. Therefore, to compare the model with future WSLive results the results were mapped back to samples and fed back into the model to generate new predictions (rank_wslive_polo_addrs.py). This was then compared with the new results to judge the accuracy of the model.

Now that the entire population has been scored (via rank_ppd_polo_addrs.py), there is no need for the original ranking script. Any random sample that is submitted to Humach is already scored and can be directly compared with survey results.

That said, the piece of the original ranking script that maps survey results back to Masterfile data is needed to allow for future retraining of the model.