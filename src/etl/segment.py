def segment_by_province_product(df):
    segments = {}
    for (provincia, producto), group in df.groupby(["Provincia", "Producto"]):
        group = group.sort_values("Fecha")
        segments[(provincia, producto)] = group
    return segments