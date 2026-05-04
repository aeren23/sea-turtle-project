"""
Loss functions module for SeaTurtle Photo-ID Metric Learning.
"""

from pytorch_metric_learning import losses

def get_arcface_loss(num_classes: int, embedding_dim: int = 512):
    """
    Returns an ArcFace Loss function for metric learning.
    
    ArcFace introduces an additive angular margin penalty that forces
    the model to learn more discriminative embeddings. Unlike Triplet Loss,
    it does not require a hard-negative miner or special samplers.
    
    Args:
        num_classes: Total number of unique identity classes.
        embedding_dim: Size of the embedding vector from the model.
        
    Returns:
        ArcFaceLoss instance with learnable parameters.
    """
    ARCFACE_MARGIN = 28.6    # Angular margin in degrees
    ARCFACE_SCALE = 64       # Scaling factor for logits
    
    loss_func = losses.ArcFaceLoss(
        num_classes=num_classes,
        embedding_size=embedding_dim,
        margin=ARCFACE_MARGIN,
        scale=ARCFACE_SCALE
    )
    
    return loss_func
