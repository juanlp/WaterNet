DATA_DIR = "/Users/Tim/dev/python/DeepWater/data/"
TRAIN_DATA_DIR = DATA_DIR + "working/train_data/"
SENTINEL_DIR = DATA_DIR + "input/Sentinel-2/"
SHAPEFILE_DIR = DATA_DIR + "input/Shapefiles/"

TILES_DIR = TRAIN_DATA_DIR + "tiles/"
WATER_BITMAPS_DIR = TRAIN_DATA_DIR + "water_bitmaps/"

MODELS_DIR = DATA_DIR + "working/models/"

OUTPUT_DIR = DATA_DIR + "output/"
OUTPUT_IMGS_DIR = OUTPUT_DIR + "imgs/"
LOGS_DIR = OUTPUT_DIR + "logs/"

MUENSTER_SHAPEFILE = DATA_DIR + "input/Shapefiles/muenster-regbez-latest-free/gis.osm_water_a_free_1.shp"
NETHERLANDS_SHAPEFILE = DATA_DIR + "input/Shapefiles/netherlands-latest-free/gis.osm_water_a_free_1.shp"

MUENSTER_SATELLITE = SENTINEL_DIR + "S2A_OPER_MSI_L1C_TL_SGS__20161204T105758_20161204T143433_A007584_T32ULC_N02_04_01.tif"
AMSTERDAM_SATELLITE = SENTINEL_DIR + "S2A_OPER_MSI_L1C_TL_SGS__20160908T110617_20160908T161324_A006340_T31UFU_N02_04_01.tif"

SENTINEL_DATASET_TRAIN = [(AMSTERDAM_SATELLITE, [NETHERLANDS_SHAPEFILE])]
SENTINEL_DATASET_TEST = [(MUENSTER_SATELLITE, [MUENSTER_SHAPEFILE])]
SENTINEL_DATASET = {
    "train": SENTINEL_DATASET_TRAIN,
    "test": SENTINEL_DATASET_TEST
}