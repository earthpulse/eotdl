from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.io import MemoryFile
import rasterio


def reproject_tif(src, dst_crs):
	transform, width, height = calculate_default_transform(
		src.crs, dst_crs, src.width, src.height, *src.bounds)
	kwargs = src.meta.copy()
	kwargs.update({
		'crs': dst_crs,
		'transform': transform,
		'width': width,
		'height': height
	})
	memfile = MemoryFile()
	dst = memfile.open(**kwargs)
	for i in range(1, src.count + 1):
		reproject(
			source=rasterio.band(src, i),
			destination=rasterio.band(dst, i),
			src_transform=src.transform,
			src_crs=src.crs,
			dst_transform=transform,
			dst_crs=dst_crs,
			resampling=Resampling.nearest
		)
	memfile2 = MemoryFile(memfile)
	return memfile2.open()