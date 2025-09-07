import pandas as pd
import geopandas as gpd
import pyarrow

def to_geoparquet(csvFile, geoFile, leftID='eqdcellcode', rightID='cellCode', exportPath='./data/export.parquet'):
    """
        Convert a GBIF cube download into a GeoParquet file, using the geometry of a GPKG

        Parameters
        ----------
        csvFile : str
            Path to the GBIF cube csv file.
        geoFile : str
            Path to the GeoPackage file.
        leftID : str, optional
            Column name within the GBIF cube to match the geometry. Default is 'edqcellcode'.
        rightID : str, optional
            Column name within the GeoPackage geometry. Default is 'cellCode'
        exportPath : str, optional
            Path to which the GeoParquet file needs to be exported.

        Returns
        -------
        A GeoParquet file at the location of exportPath
    """

    # Read tab-separated CSV, keep key as string to preserve leading zeros
    data = pd.read_csv(csvFile, sep="\t", dtype={leftID: "string"})
    data[leftID] = data[leftID].str.strip()

    # Read the GeoPackage (no crs= here)
    geoRef = gpd.read_file(geoFile, engine="pyogrio", use_arrow=True)

    # If the layer has no CRS and you KNOW it should be WGS84, set it explicitly
    if geoRef.crs is None:
        geoRef = geoRef.set_crs(4326)

    # Ensure join key is string and trimmed
    geoRef[rightID] = geoRef[rightID].astype("string").str.strip()

    # ✅ Merge DATAFRAMES, not strings
    merged = pd.merge(data, geoRef, left_on=leftID, right_on=rightID, how="inner")

    # Build GeoDataFrame and write Parquet
    gdf = gpd.GeoDataFrame(merged, geometry="geometry", crs=geoRef.crs)
    gdf.to_parquet(exportPath, index=False)
