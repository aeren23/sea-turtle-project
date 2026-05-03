"""
Loss functions module for SeaTurtle Photo-ID Metric Learning.
"""

from pytorch_metric_learning import losses, miners

def get_triplet_loss_and_miner(margin: float = 0.2):
    """
    Returns a Triplet Margin Loss function along with a Hard Negative Miner.
    
    The Miner acts as an active filter during training:
    Instead of calculating loss on all triplets (which includes many 'easy' 
    negatives that don't teach the model anything), it dynamically selects 
    only the 'hardest' triplets (e.g., two different turtles that look very 
    similar). This forces the CNN to learn micro-textures.
    
    Args:
        margin (float): The minimum desired distance between a positive pair 
                        and a negative pair in the embedding space.
                        
    Returns:
        tuple: (miner, loss_func)
    """
    # MultiSimilarityMiner is generally considered one of the best for Re-ID tasks
    miner = miners.MultiSimilarityMiner()
    
    # Standard Triplet Margin Loss
    loss_func = losses.TripletMarginLoss(margin=margin)
    
    return miner, loss_func
