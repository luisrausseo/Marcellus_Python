from Lib import wells_reader as wr
from Lib import map_plot as mp
import numpy as np

csv_wells = 'Data\\wells.csv'
csv_prod = 'Data\\production.csv'
sf_path = 'Shapefiles\\PA_Counties_clip'
sf_name = 'states'
st = 'PA'
title = 'Pennsylvania'
#-------------------------------------------------------------------------
#TEST FOR GRAPHS
production = wr.get_data(csv_prod, 'prod')
#wr.graph_WellData(production, ['3700322092', '3700322194'])
wr.graph_EPL(production, '3700322092',[0.001,0.009,1.3136])

#--------------------------------------------------------------------------
#TEST MAP
#wells = wr.get_data(csv_wells, 'wells')
#wells = wr.get_rows(wells, ['marcellus', 'marcellus shale', 'marcellus shale (unconventional)'], 'formation')
#lat, lon = np.array(wells['latitude']), np.array(wells['longitude'])
#m = mp.create_map(st, sf_path, sf_name)
#mp.plot_point(m, lat, lon)
#mp.draw_map(m, title)
