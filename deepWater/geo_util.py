"""Module to handle processing the raw GeoTIFF data from satellite imagery."""

import rasterio
import rasterio.warp
import os
import itertools
import numpy as np
from io_util import get_file_name
from config import WGS84_DIR


def read_geotiff(file_name):
    """TODO: Docstring."""
    raster_dataset = rasterio.open(file_name)
    bands = np.dstack(raster_dataset.read())
    return raster_dataset, bands


def reproject_dataset(geotiff_path):
    """TODO: Add docstring.
    TODO: Add link to rasterio docs."""

    # We want to project the GeoTIFF coordinate reference system (crs)
    # to WGS84 (e.g. into the familiar Lat/Lon pairs). WGS84 is analogous
    # to EPSG:4326
    dst_crs = 'EPSG:4326'

    with rasterio.open(geotiff_path) as src:
        transform, width, height = rasterio.warp.calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        satellite_img_name = get_file_name(geotiff_path)
        out_file_name = "{}_wgs84.tif".format(satellite_img_name)
        out_path = os.path.join(WGS84_DIR, out_file_name)
        with rasterio.open(out_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                rasterio.warp.reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=rasterio.warp.Resampling.nearest)

        return rasterio.open(out_path), out_path


def create_tiles(bands_data, tile_size, path_to_geotiff):
    """From https://github.com/trailbehind/DeepOSM."""

    rows, cols = bands_data.shape[0], bands_data.shape[1]

    all_tiled_data = []

    tile_indexes = itertools.product(
        range(0, rows, tile_size), range(0, cols, tile_size))

    for (row, col) in tile_indexes:
        in_bounds = row + tile_size < rows and col + tile_size < cols
        if in_bounds:
            new_tile = bands_data[row:row + tile_size, col:col + tile_size]
            all_tiled_data.append((new_tile, (row, col), path_to_geotiff))

    return all_tiled_data


def image_from_tiles(tiles, tile_size, image_shape):
    image = np.zeros(image_shape, dtype=np.uint8)

    for tile, (row, col), _ in tiles:
        tile = np.reshape(tile, (tile_size, tile_size))
        image[row:row + tile_size, col:col + tile_size] = tile

    return image


def overlay_bitmap(bitmap, raster_dataset, out_path, color='blue'):
    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255)
    }
    red, green, blue = raster_dataset.read()
    red[bitmap == 1] = colors[color][0]
    green[bitmap == 1] = colors[color][1]
    blue[bitmap == 1] = colors[color][2]
    profile = raster_dataset.profile
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(red, 1)
        dst.write(green, 2)
        dst.write(blue, 3)

    return rasterio.open(out_path)


def visualise_features(features, tile_size, out_path):
    get_path = lambda (tiles, features, path): path
    sorted_by_path = sorted(features, key=get_path)
    for path, predictions in itertools.groupby(sorted_by_path, get_path):
        raster_dataset = rasterio.open(path)
        bitmap_shape = (raster_dataset.shape[0], raster_dataset.shape[1])
        bitmap = image_from_tiles(predictions, tile_size, bitmap_shape)

        satellite_img_name = get_file_name(path)
        out_file_name = "{}.tif".format(satellite_img_name)
        out = os.path.join(out_path, out_file_name)
        overlay_bitmap(bitmap, raster_dataset, out)

def visualise_results(results, tile_size, out_path):
    get_predictions = lambda (tiles, pos, path): (tiles[0], pos, path)
    get_labels = lambda (tiles, pos, path): (tiles[1], pos, path)
    get_false_positives =  lambda (tiles, pos, path): (tiles[2], pos, path)

    get_path = lambda (tiles,pos , path): path
    sorted_by_path = sorted(results, key=get_path)
    for path, result_tiles in itertools.groupby(sorted_by_path, get_path):
        raster_dataset = rasterio.open(path)
        bitmap_shape = (raster_dataset.shape[0], raster_dataset.shape[1])

        result_tiles = list(result_tiles)
        predictions = map(get_predictions, result_tiles)
        labels = map(get_labels, result_tiles)
        false_positives = map(get_false_positives, result_tiles)

        satellite_img_name = get_file_name(path)
        out_file_name = "{}_results.tif".format(satellite_img_name)
        out = os.path.join(out_path, out_file_name)
        for tiles, color in [(labels, 'blue'), (predictions, 'green'), (false_positives, 'red')]:
            bitmap = image_from_tiles(tiles, tile_size, bitmap_shape)
            raster_dataset = overlay_bitmap(bitmap, raster_dataset, out, color=color)

def visualise(feautures, tile_size, out_path, colors=['blue']):
    get_path = lambda (tiles, pos, path): path
    sorted_by_path = sorted(features, key=get_path)
    for path, tile_data in itertools.groupby(sorted_by_path, get_path):
        raster_dataset = rasterio.open(path)
        bitmap_shape = (raster_dataset.shape[0], raster_dataset.shape[1])

        get_tiles = lambda (tiles, pos, path): tiles
        tiles = map(get_tiles, tile_data)
        tiles_colors = zip(zip(*tiles), colors)

        # TODO: do the loop from 147.