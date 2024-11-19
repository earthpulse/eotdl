def compute_percentiles(base_features, percentiles=[0.1, 0.25, 0.50, 0.75, 0.9]):
    """
    Computes P10, P25, P50, P75, P90 without depending on metadata early.
    """
    # Inner function to compute quantiles
    def compute_stats(input_timeseries):
        return input_timeseries.quantiles(percentiles)
    # Apply dimension to calculate statistics
    stats = base_features.apply_dimension(
        dimension='t', target_dimension="bands", process=compute_stats
    )
    # Create dynamic band names only after statistics are computed
    band_names = base_features.metadata.band_names if base_features.metadata else []
    percentile_labels = [f"P{int(p * 100):02d}" for p in percentiles]
    all_bands = [
        f"{band}_{stat}"
        for band in band_names
        for stat in percentile_labels
    ]
    return stats.rename_labels("bands", all_bands)
