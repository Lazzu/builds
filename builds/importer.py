
def import_pipeline(pipeline):
    """
    Dynamically imports modules / classes
    """
    mod = __import__('pipelines.' + pipeline, fromlist=[pipeline])
    return getattr(mod, pipeline)
