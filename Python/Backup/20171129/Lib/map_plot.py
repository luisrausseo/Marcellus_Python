import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def states(st):
    if st == 'TX':
        return [-106, 25, -93, 37]
    if st == 'PA':
        return [-81.5, 39.5, -74, 42]

def create_map(st, sf_path, sf_name):
    m = Basemap(llcrnrlon=states(st)[0],llcrnrlat=states(st)[1],
                urcrnrlon=states(st)[2],urcrnrlat=states(st)[3],
                projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
    m.readshapefile('C:\\Users\\luisrausseo\\Dropbox\\TTU\\Project\\Shapefiles\\cb_2016_us_state_20m',
                    name='states', drawbounds=True)
    m.readshapefile(sf_path, name=sf_name, drawbounds=True)
    return m

def plot_point(m, lat, lon):
    x, y = m(lon, lat)
    m.plot(x, y, 'ro')
    return 0

def draw_map(m, map_title):
    plt.title(map_title)
    m.drawlsmask(land_color = "#ddaa66", 
                 ocean_color ="#7777ff",
                 resolution = 'l',
                 grid = 1.25)
    plt.show()
    return 0
